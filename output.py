""" H Ratcliffe, University of Warwick, March 2018
  Controls output of tree. Currently uses
  dot format for display
"""
import graphviz

_oc = None

def tree_to_graphviz(tree):
	""" Create a dot object from a tree
	"""
	dot = graphviz.Digraph(comment='Routing for App. Grey nodes require login. Ovals are pages, boxes are data (json). Embellishments indicate methods were specified', format='png')
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
