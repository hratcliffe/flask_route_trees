from astroid import MANAGER

import identify as id
import match_heuristics as mh
import output as out
import routing as rt

def parse_routing(ast):
	"""Parse flask routing from an ast
	
	Returns - tree (see generate_tree for format)
	"""
	all_nodes = get_nodes(ast)
	app = id.identify_app(ast)
	return generate_tree(app, all_nodes)

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

def generate_tree(app, all_nodes):
	"""Generate routing tree from app info and node dict
	
	Parameters:
	app -- app info (see id.identify_app)
	all_nodes -- dict of nodes (see get_nodes)

	Returns - tree as tuple: (root node, dict of nodes) where every node has parent and children specified
	"""
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

if __name__ == '__main__':

	try: input = raw_input
	except NameError: pass
	
	input('Filename to parse:', filename)
	generate_routing(filename)
	