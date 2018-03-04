import astroid
from urlparse import urlparse
import re
import graphviz
from copy import deepcopy

_fn_type = astroid.scoped_nodes.FunctionDef
_import_type = astroid.node_classes.Import
_assign_type = astroid.node_classes.Assign
_call_type = astroid.node_classes.Call
_decorator_type = astroid.node_classes.Decorators
_attirbute_type = astroid.node_classes.Attribute
_blueprint_identifier = 'Blueprint'

#Simple node contains
	#Function name
	#routing
	#login y/n
	#return type
class simple_node:
	def __init__(self, name='', route=None):
		self.name = name
		self.safe_name = self.make_safe(name)
		self.route = route
		self.login = None
		self.ret_type = None
		
		self.parent = None
		self.children = []
		self.dummy = False

	def set_name(self, name):
		self.name = name
		self.safe_name = self.make_safe(name)
	def set_route(self, route):
		self.route = route
	def set_login(self, login):
		self.login = login
	def set_ret_type(self, ret_type):
		self.ret_type = ret_type
	def make_safe(self, name):
		#Make a name which is safe for DOT and Graphviz to use
		return name.replace(':', '_')

class flask_route:
	def __init__(self, path = []):
		self.path = path
	def _replace_path(new_path):
		self.path = new_path
	def add_to_path(new_section):
		if isinstance(new_section, route_section):
			self.path.append(new_section)
	def __str__(self):
		pstr = ''
		for item in self.path:
			pstr += str(item)
			pstr +='/'
		return pstr
	def str_notr(self):
		pstr = ''
		for item in self.path:
			pstr += str(item)
			pstr +='/'
		return pstr[1:-1]
	def __eq__(self, other):
		if len(self.path) != len(other.path):
			return False
		i = 0
		for item in self.path:
			if item != other.path[i]:
				return False
			i = i + 1
		return True
	def __ne__(self, other):
		return not self.__eq__(other)
	def pathlen(self):
		return len(self.path)

class route_section:
	def __init__(self, value = ''):
		self.value = value #String segment
	def set_value(self, value):
		self.value = value
	def __str__(self):
		return self.value
	def __eq__(self, other):
		if isinstance(other, flask_placeholder):
			return True
		return self.value == other.value
	def __ne__(self, other):
		return not self.__eq__(other)
		
class flask_placeholder(route_section):
	def __init__(self, value='', var='', typestr=''):
		route_section.__init__(self, value)
		self.var = var #The placeholder name used
		self.typestr = typestr #The flask type string
	def set_var(self, var):
		self.var = var
	def set_typestr(self, typestr):
		self.typestr = typestr
	def __str__(self):
		return self.value
	def full_str(self):
		return self.value + '['+self.var + ','+ self.typestr+']'
	def __eq__(self, other):
		if isinstance(other, route_section):
			return True
		return False
	def __ne__(self, other):
		return not self.__eq__(other)


def select_match(route, options):
	#Select 'best' parent for route
	#All match, so go left to right favouring higher precedence
	layer_opts = []
	layer = 0
	matches = deepcopy(options)
	for section in route.path[0:-1]:
		layer_opts = [opt.path[layer] for opt in matches]
		best = select_precedence(section, layer_opts)
		matches = [match for match in matches if match.path[layer] == best]
		layer += 1
	#Now we have all 'matching' we want to order them
	matches = order_matches(matches, route)
	if len(matches) >= 1:
		#If more than one match, pick last(highest) in ordered list
		return matches[-1]
	else:
		return None
	
def select_precedence(section, options):
	#Select the correct match for route
	#E.g if have 'abc' and '<string:item>' options abc matches first
	#We match naively for now, assuming a placeholder matches to a placeholder and a string to a string, unless there is no string
	choice = None
	second_choice = None
	for item in options:
		if isinstance(section, flask_placeholder):
			if isinstance(item, flask_placeholder):
				choice = item
				#This doesn't handle overlapping placeholders at all
				break
			else:
				second_choice = item
		else:
			if item.value == section.value:
				choice = item
				break
	if choice is None:
		choice = second_choice
	return choice

def order_matches(matches, target):
	#Provide list of all possible matches, will order them
	#Placeholder type ordering depends on target
	#Precedence is left to right
	#Strings are better than placeholders. Longer is better than shorter

	lengthed_matches = []
	for item in matches:
		match_spec = [item.pathlen()]
		layer = 0
		for piece in item.path:
			match_spec.append(matchness(piece, target.path[layer]))
			layer = layer + 1
		lengthed_matches.append((match_spec, item))
	return [match[1] for match in sorted(lengthed_matches, key = lambda mat : mat[0])]
	
def matchability(section):
	#Assign numerical 'matchyness' value
	if isinstance(section, flask_placeholder):
		return 2
	elif isinstance(section,route_section):
		return 4
	else:
		return 0

def matchness(section, option):
	#Assign numerical 'matchyness' ordering
	if section != option:
		return 0
	if isinstance(section, flask_placeholder):
		if isinstance(option, flask_placeholder):
			return 1
		else:
			return 2
	else:
		if option.value == section.value:
			return 3

#Find the Blueprint spec. This gives the name for routing
#Returns tuple of the app name and the blueprint call node
#This is hardly slick, but it'll do
def identify_app(ast):
	app = ('', None)
	for item in ast.nodes_of_class(_assign_type):
			try:
				if type(item.value) == _call_type and item.value.func.name == _blueprint_identifier:
					app = (item.value.args[0].value, item)
			except:
				pass
	return  app

#This would probably be the proper way but its hard
#Create object representing the routing decorator
#Create object representing login decorator
#Define function to check presence of decorator on ast FunctionDef object
def has_decorator(function, decorator):
	return False

#Instead do this:
def get_login_decorator(function):
	#Return tuple (true if login_required exists, login decorator)
	login = None
	if function.decorators is not None: 
		for item in function.decorators.get_children():
			try:
				if item.name == 'login_required':
					login = item
			except:
				pass
	return (login is not None, login)

def get_route_decorator(function):
	#Return tuple (route string, route decorator)
	route = ''
	routing = None
	if function.decorators is not None: 
		for item in function.decorators.get_children():
			try:
				if type(item) == _call_type:
					if item.func.attrname == 'route':
						routing = item
						route = item.args[0].value
			except:
				pass
	return (route, routing)

def split_url_path(url):
	#Split url into chunks
	return url.split('/')

def parse_flask_placeholder(string):
	#This is pretty clumsy but enough for now
	reg = re.compile('<(\w+):(\w+)>')
	match = re.match(reg, string)
	if match is not None:
		try:
			grps = match.groups()
			return flask_placeholder(string, grps[1], grps[0])
		except:
			return route_section(string)
	else:
		return route_section(string)
	
def parse_flask_routing(url):
	#Split url into list of route_section objects
	#Ensure trailing slash
	if url =='' or url[-1] != '/':
		url = url + '/'
	parts = url.split('/')
	new_parts = []
	#Ignore last part as that is empty section after trailing slash
	#Technically could be sections like '//' with blank part
	for part in parts[0:-1]:
		new_parts.append(parse_flask_placeholder(part))
	return flask_route(new_parts)

def parse_routing(ast):
	
	#All_nodes is dict mapping routes to nodes
	#'Tree' is then created where each node holds its children
	all_nodes = {}
	for item in ast.nodes_of_class(_fn_type):
		node = simple_node()
		node.set_name(item.name)
		node.set_route(get_route_decorator(item))
		node.set_login(get_login_decorator(item))
		#Find return type info
		#TBC
		
		#Add to dict keyed on route
		all_nodes[node.route[0]] = node
	#return all_nodes
	app = identify_app(ast)
	return generate_tree(app, all_nodes)

def generate_tree(app, all_nodes):
	#Generate a list of lists where each entry is a level in our tree
	route_tree = []
	all_routes = all_nodes.keys()
	all_unpacked_routes = []
	for item in all_routes:
		flask_route = parse_flask_routing(item)
		depth = len(flask_route.path)
		if len(route_tree) > depth:
			route_tree[depth].append(flask_route)
		else:
			route_tree.extend([[] for _ in range(depth - len(route_tree) + 1)])
			route_tree[depth].append(flask_route)
		all_unpacked_routes.append(flask_route)
	#return all_unpacked_routes
	#route_tree is now layered lists 
	#Now fill in parent info, and put children under parents
	if app:
		tree_root = simple_node(app[0] ,'')
	else:
		tree_root = simple_node('app_root' ,'')
	for layer in route_tree:
		for item in layer:
			parent = get_parent(item, all_unpacked_routes)
			if parent is None:
				parent = tree_root.route
			try:
				all_nodes[str(parent)].children.append(item)
			except:
				try:
					#Perhaps there's no trailing slash
					all_nodes[str_notr(parent)].children.append(item)
				except Exception as e:
					print e
			try:
				all_nodes[str(item)].parent = parent
			except Exception as e:
				print e
	return tree_root, all_nodes

def get_parent(route, all_routes):
	#Find next url up and return
	# E.g. if have a, a/b then parent of a/b/c is 'a/b' and of a/d/e is 'a'
	#This also deals with flask placeholders in simple form using select_precendence
	#This is neither complete nor absolute!!!
	parent = None
	if len(route.path) == 1:
		return None
	potential = deepcopy(route)
	all_matches = []
	found = False
	while(not found):
		potential = flask_route(potential.path[0:-1])
		for rt in all_routes:
			if potential == rt:
				all_matches.append(rt)
				found = True
	parent = select_match(route, all_matches)
	return parent


def basic_show_tree(tree, nodes):

	for level in tree:
		level_str = ''
		for item in level:
			if item is None:
				continue
			for piece in item:
				level_str = level_str + str(piece)
			level_str = level_str + '\t'
		print level_str

def tree_to_graphviz(tree):

	dot = graphviz.Digraph(comment='Routing for App', format='png')
	dot.attr(fontsize='12')
	dot.node(tree[0].safe_name)
	for item in tree[1]:
		if item:
			if tree[1][item].login[0]:
				dot.node(tree[1][item].safe_name, str(item), shape='box')
			else:
				dot.node(tree[1][item].safe_name, str(item))
	for item in tree[1]:
		if item:
			if tree[1][item].parent:
				dot.edge(tree[1][str(tree[1][item].parent)].safe_name, tree[1][item].safe_name)
			else:
				dot.edge(tree[0].safe_name, tree[1][item].safe_name)
	return dot

if __name__ == '__main__':

	filename = 'example.py'
	MAN = astroid.MANAGER
	ast = MAN.ast_from_file(filename, source=True)
	tree = parse_routing(ast)
	dot = tree_to_graphviz(tree)
	dot.render('app.png', view=True)
	dot.view()
	