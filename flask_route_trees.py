""" H Ratcliffe, University of Warwick, March 2018
Create simple graphs of routing trees for flask apps
"""

from astroid import MANAGER

import identify as id
import match_heuristics as mh
import output as out
import routing as rt

from hashlib import md5

def parse_routing(ast, id_prefix = ""):
	"""Parse flask routing from an ast
	
	Returns - tree (see generate_tree for format)
	"""
	all_nodes = get_nodes(ast)
	app = id.identify_app(ast)
	return generate_tree(app, all_nodes, id_prefix)

def get_nodes(ast):
	"""Parse nodes from an ast
	
	Returns - dict of rt.simple_node objects keyed on route string
	"""
	#All_nodes is dict mapping routes to nodes
	all_nodes = {}
	for item in ast.nodes_of_class(id._fn_type):
		node = rt.simple_node()
		node.set_name(item.name)
		node.set_route(id.get_route_decorator(item))
		node.set_login(id.get_login_decorator(item))
		node.set_type(id.get_type(item))
		node.set_methods(id.get_methods(item))

		all_nodes[node.route[0]] = node
	return all_nodes

def generate_tree(app, all_nodes, id_prefix):
	"""Generate routing tree from app info and node dict
	
	Parameters:
	app -- app info (see id.identify_app)
	all_nodes -- dict of nodes (see get_nodes)
	id_prefix -- Unique string prepended to all node IDs to avoid name collisions in multiapp trees

	Returns - tree as tuple: (root node, dict of nodes) where every node has parent and children specified
	"""
	all_nodes = rt.add_ids(all_nodes, id_prefix)
	all_unpacked_routes, route_tree = unpack_routes_and_tree(all_nodes)
	#route_tree is now layered lists 
	#Now fill in parent info, and put children under parents
	if app:
		tree_root = rt.simple_node(app[0] ,'')
	else:
		tree_root = rt.simple_node('app_root' ,'')
	for layer in route_tree:
		for item in layer:
			parent = rt.get_parent(item, all_unpacked_routes)
			if parent is None:
				parent = tree_root.route
			try:
				all_nodes[str(parent)].children.append(item)
			except:
				try:
					#Perhaps there's no trailing slash
					all_nodes[parent.str_notr()].children.append(item)
				except Exception as e:
					print 'Error 1', str(e)
			try:
				all_nodes[str(item)].parent = parent
			except Exception as e:
				try:
					all_nodes[item.str_notr()].parent = parent
				except:
					print 'Error 2', str(e), 'on', str(item), item.str_notr()
	return tree_root, all_nodes

def unpack_routes_and_tree(all_nodes):
	"""Unpack route strings into route objects
	
	Parameters:
	all_nodes -- dict of rt.simple_node objects
	
	Returns - tuple (list of route objs, layered list/tree)
	"""

	all_routes = all_nodes.keys()
	all_unpacked_routes = []
	route_tree = []
	for item in all_routes:
		flask_route = rt.parse_flask_routing(item)
		depth = len(flask_route.path)
		if len(route_tree) > depth:
			route_tree[depth].append(flask_route)
		else:
			route_tree.extend([[] for _ in range(depth - len(route_tree) + 1)])
			route_tree[depth].append(flask_route)
		all_unpacked_routes.append(flask_route)
	return all_unpacked_routes, route_tree

def generate_routing(filename):
	"""Parse file generate tree and create dot file and png
	
	Parameters:
	filename -- python file containing flask routing
	"""
	MAN = MANAGER
	ast = MAN.ast_from_file(filename, source=True)
	tree = parse_routing(ast)
	dot = out.tree_to_graphviz(tree)
	
	output_name = tree[0].name
	if output_name == '':
		output_name = filename
	dot.render(output_name, view=True)

def generate_partial_routing(filename):
	"""Parse file generate tree and create dot string
	
	Parameters:
	filename -- python file containing flask routing
	"""
	MAN = MANAGER
	ast = MAN.ast_from_file(filename, source=True)
	tree = parse_routing(ast)
	return tree

def generate_multiapp_routing(filename):
	"""Parse file, generate tree for each app, and create dot file and png
	
	Parameters:
	filename -- python file containing list of filenames each of which points to a single Flask app
	"""
	MAN = MANAGER
	with open(filename, 'r') as infile:
		file_list = infile.readlines()
	
	dot, root = out.head_tree_graphviz('App')
	
	#Attempt to find common part of all filenames
	#We then assume the the first level after this common part
	#is a folder and everything within should go into a shared tree
	common_part_list = None
	for file in file_list:
		file_parts = file.split('/')
		while '' in file_parts:
			file_parts.remove('')
		if common_part_list is None: 
			common_part_list = file_parts
		else:
			for i in range(0, min(len(common_part_list), len(file_parts))):
				trim = False
				if common_part_list[i] != file_parts[i]: 
					trim = True
					break
			if i > 0 and trim:
				common_part_list = common_part_list[0:i]

	i = len(common_part_list) + 1
	linked = []
	for file in file_list:
		#Generate an id from the common parts of all names plus one level down
		parts = file.split('/')
		while '' in parts:
			parts.remove('')
		core_name = parts[i-1]
		parts = "/".join(parts[0:i])
		id_prefix = md5(parts).hexdigest()

		ast = MAN.ast_from_file(file, source=True)
		tree = parse_routing(ast, id_prefix)
		tree[0].set_id(id_prefix)
		tree[0].set_name(core_name)
		try:
			out.add_tree_to_dot(tree, dot)
		except Exception as e:
			print('Error handling '+file +' '+str(e))
		if id_prefix not in linked:
			out.link_to_root(dot, tree[0].id, root)
			linked.append(id_prefix)

	output_name = 'Routes_'+filename
	dot.render(output_name, view=True)

if __name__ == '__main__':

	try: input = raw_input
	except NameError: pass

	mode = input('[S]ingle or [M]ulti app routing:')

	if mode.upper() == 'S':
		filename = input('Filename to parse:')
		generate_routing(filename)
	elif mode.upper() == 'M':
		filename = input('File containing list of files:')
		generate_multiapp_routing(filename)
		
	else:
		print('Unknown mode input, try S or M')