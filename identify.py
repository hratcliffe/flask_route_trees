import config
import astroid
import re


_fn_type = astroid.scoped_nodes.FunctionDef
_import_type = astroid.node_classes.Import
_assign_type = astroid.node_classes.Assign
_call_type = astroid.node_classes.Call
_decorator_type = astroid.node_classes.Decorators
_attribute_type = astroid.node_classes.Attribute
_return_type = astroid.node_classes.Return
_blueprint_identifier = 'Blueprint'

_type_strings = ['none', 'json', 'page', 'other']
_method_strings = ['get', 'post']

def identify_app(ast):
	"""Try and find the app name from a Blueprint spec
	Parameters:
	ast -- asteroid ast of source code
	
	Returns - tuple of the app name and the blueprint call node
	"""
	app = ('', None)
	for item in ast.nodes_of_class(_assign_type):
		try:
			if type(item.value) == _call_type and item.value.func.name == _blueprint_identifier:
				app = (item.value.args[0].value, item)
		except:
			pass
	return app

def get_login_decorator(function):
	"""Try and get any login decorator
	Parameters:
	function -- the function to examine, as a _fn_type object
	
	Returns - tuple (true if login_required exists, login decorator)
	"""
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
	"""Try and get routing decorator(s)
	Parameters:
	function -- the function to examine, as a _fn_type object
	
	Returns - tuple (route string, route decorator)
	"""
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

def get_type(function):
	"""Try and get function 'return type'
	Since we can't run the code, we're just looking for a few tip-offs, such as
	whether the return line contains 'jsonify' or 'render_template'
	If more than one return, tries to give representative

	Parameters:
	function -- the function to examine, as a _fn_type object
	
	Returns - tuple (return string type, return object)
	"""
	return_opt = ('none', None)
	secondary_return_opt = ('none', None)
	for item in function.body:
		if type(item) == _return_type:
			if 'jsonify' in item.as_string():
				return_opt = ('json', item)
			elif '{' in item.as_string():
				secondary_return_opt = ('json', item)
			elif 'render_template' in item.as_string():
				return_opt = ('page', item)
	return return_opt

def get_methods(function):
	"""Try and get route 'methods', i.e. the list in
	@app.route(route, methods=['POST'])
	Parameters:
	function -- the function to examine, as a _fn_type object
	
	Returns -  methods string list (see _methods_strings)
	"""
	route = get_route_decorator(function)
	if not route[1]:
		return []
	keywds = route[1].keywords
	meth = []
	if not keywds:
		return []
	for wd in keywds:
		if wd.arg == 'methods':
			meth = wd.value.as_string()
	reg = re.compile('\[(.*)\]')
	match = re.match(reg, meth)
	if match is not None:
		grps = match.groups()[0].split(',')
		for item in grps:
			item = item.strip()
	return grps
