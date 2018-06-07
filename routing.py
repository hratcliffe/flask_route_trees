""" H Ratcliffe, University of Warwick, March 2018
  Extraction and handling of routing info
"""
from urlparse import urlparse
import re
from copy import deepcopy

import match_heuristics as mh

class simple_node:
	""" Tree node for a given route
	Contains the endpoint name, full route, and details such as decorators
	Also contains link to parent node
	"""
	def __init__(self, name='', route=None):
		self.name = name
		self.safe_name = self._make_safe(name)
		self.route = route
		self.login = None
		self.type = None
		self.methods = None
		self.id = "" #ID for the tree this node should be in
		self.parent = None
		self.children = []

	def set_name(self, name):
		self.name = name
		self.safe_name = self._make_safe(name)
	def set_id(self, id):
		self.id = id
	def set_route(self, route):
		self.route = route
	def set_login(self, login):
		self.login = login
	def set_type(self, type):
		self.type = type
	def set_methods(self, methods):
		self.methods = methods
	def _make_safe(self, name):
		"""Make a name which is safe for DOT and Graphviz to use"""
		return name.replace(':', '_')

class flask_route:
	"""
	A full route, comprised of route sections
	"""
	def __init__(self, path = []):
		assert(self._check_path(path))
		self.path = path

	def replace_path(new_path):
		assert(self._check_path(new_path))
		self.path = new_path
	def add_to_path(new_section):
		if isinstance(new_section, route_section):
			self.path.append(new_section)
	def _check_path(self, path):
		for section in path:
			if not isinstance(section, route_section):
				return False
		return True

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
		return pstr[0:-1]
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
	"""A single segment of a route
	This is not particularly useful as is, but derived
	classes can add a lot of power
	"""
	def __init__(self, value = ''):
		self.value = value #String
	def set_value(self, value):
		self.value = value
	def __str__(self):
		return self.value
	def __eq__(self, other):
		#Should handle equality with any derived types too
		if isinstance(other, flask_placeholder):
			return True
		return self.value == other.value
	def __ne__(self, other):
		return not self.__eq__(other)
		
class flask_placeholder(route_section):
	"""A single segment of a route which is a flask-style placeholder
	That is, of the form '<type:name>'
	"""
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

def split_url_path(url):
	"""Split url into chunks"""
	#Ensure trailing slash to get parts correct
	if url =='' or url[-1] != '/':
		url = url + '/'
	parts = url.split('/')
	try:
		#Final part is now blank
		return parts[0:-1]
	except:
		return parts

def parse_route_segment(string):
	"""Turn a string containing a route segment into
	a suitable route_section object
	"""
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
	"""Turn url into flask_route object
	"""
	parts = split_url_path(url)
	new_parts = []
	for part in parts:
		new_parts.append(parse_route_segment(part))
	return flask_route(new_parts)

def get_parent(route, all_routes):
	"""Get parent of given route (best guess)
	
	Parameters:
	route -- the route to consider
	all_routes -- all possible routes to select from
	"""
	parent = None
	if len(route.path) == 1:
		return None
	potential = deepcopy(route)
	all_matches = []
	while(len(potential.path) > 0):
		#Compile all possible, shorter, matches
		potential = flask_route(potential.path[0:-1])
		for rt in all_routes:
			if potential == rt:
				all_matches.append(rt)
	parent = mh.select_match(route, all_matches)
	return parent

def add_ids(node_dict, id):
	
	for key, value in node_dict.items():
		value.set_id(id)
	return node_dict
