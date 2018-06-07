""" H Ratcliffe, University of Warwick, March 2018
  Controls output of tree. Currently uses
  dot format for display
"""
import graphviz

_oc = None

def tree_to_graphviz(tree):
	""" Create a dot object from a tree
	"""
	dot = graphviz.Digraph(comment='Routing for App. Grey nodes require login. Ovals are pages, boxes are data (json). Embellishments indicate methods were specified', format='png', strict=True)
	dot.attr(fontsize='12')
	dot.node(tree[0].safe_name, shape='doubleoctagon')
	for item in tree[1]:
		box = 'oval'
		styles = []
		if item:
			if tree[1][item].type[0]=='json': box = 'box'
			if tree[1][item].methods != [] : styles.append('diagonals')
			if tree[1][item].login[0]:
				styles.append('filled')
				dot.node(tree[1][item].safe_name, str(item), style=','.join(styles), fillcolor='gray', shape = box)
			else:
				dot.node(tree[1][item].safe_name, str(item), shape=box, style=','.join(styles))
	for item in tree[1]:
		if item:
			if tree[1][item].parent:
				dot.edge(tree[1][str(tree[1][item].parent)].safe_name, tree[1][item].safe_name)
			else:
				dot.edge(tree[0].safe_name, tree[1][item].safe_name)
	return dot


def head_tree_graphviz(app):
	""" Create a dot object describing top of tree for 'app'
	"""
	dot = graphviz.Digraph(comment='Routing for App. Grey nodes require login. Ovals are pages, boxes are data (json). Embellishments indicate methods were specified', format='png')
	dot.attr(fontsize='12')
	dot.node(app, shape='doubleoctagon')
	root = app
	return (dot, root)


def add_tree_to_dot(tree, dot):
	""" Add nodes for given tree to dot object
	"""

	dot.node(tree[0].id, tree[0].safe_name, shape='octagon')
	for item in tree[1]:
		box = 'oval'
		styles = []
		if item:
			if tree[1][item].type[0]=='json': box = 'box'
			if tree[1][item].methods != [] : styles.append('diagonals')
			if item == '/':
				item_as_label = tree[0].safe_name + '/'
			else:
				item_as_label = str(item)
			if tree[1][item].login[0]:
				styles.append('filled')
				dot.node(tree[1][item].id+tree[1][item].safe_name, item_as_label, style=','.join(styles), fillcolor='gray', shape = box)
			else:
				dot.node(tree[1][item].id+tree[1][item].safe_name, item_as_label, shape=box, style=','.join(styles))
	for item in tree[1]:
		if item:
			try:
				if tree[1][item].parent:
					dot.edge(tree[1][item].id + tree[1][str(tree[1][item].parent)].safe_name,  tree[1][item].id + tree[1][item].safe_name)
				else:
					dot.edge(tree[0].id, tree[1][item].id+tree[1][item].safe_name)
			except:
					dot.edge(tree[0].id, tree[1][item].id+tree[1][item].safe_name)
	return dot

def link_to_root(dot, node, root):
	dot.edge(root, node)

