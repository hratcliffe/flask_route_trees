""" H Ratcliffe, University of Warwick, March 2018
 Controls concrete and heuristic matching of parts of route paths
 Routes are defined in routing.py
 Config controls how strong a match we consider between strings and placeholders 
(wildcards)
 Longer matches are preferred
"""

from copy import deepcopy

import config as ch
import routing as rt

#Internal config objects setup on import
_hc = ch.heuristics()

def select_match(route, options):
	"""Select 'best' match for a given route

	Parameters:
	route -- route to match
	options -- list of possible matches
	"""
	if len(options) == 1:
		return options[0]
	
	#We have all matching we order them and take the last (highest)
	matches = order_matches(deepcopy(options), route)
	if len(matches) >= 1:
		return matches[-1]
	else:
		return None
	
def order_matches(matches, target):
	"""Orders matches by their strength
	
	Parameters:
	matches -- list of all matches
	target -- target route to match (affects strength factors)
	"""

	annotated_matches = []
	for item in matches:
		match_spec = [item.pathlen()*_hc.LEN]
		#Length is given varying precedence
		layer = 0
		for piece in item.path:
			match_spec.append(matchyness(piece, target.path[layer])*_hc.LAY**layer)
			#Can have rolloff or rollon for later pieces
			layer = layer + 1
		#Total the matchyness
		match_val = sum(match_spec)
		annotated_matches.append((match_val, item))
	#Sort by matchyness
	return [match[1] for match in sorted(annotated_matches, key = lambda mat : mat[0])]

def matchyness(section, option):
	"""Assign numerical 'matchyness' value between target and value
	
	Parameters:
	section -- target value
	option -- proposed match
	"""
	if section != option:
		return _hc.NEQ
	if isinstance(section, rt.flask_placeholder):
		if isinstance(option, rt.flask_placeholder):
			return _hc.PP #Placeholder - placeholder
		else:
			return _hc.PS #Placeholder - string
	else:
		if option.value == section.value:
			return _hc.SS #String - string
		elif isinstance(option, rt.flask_placeholder):
			return _hc.SP #String - placeholder
		else:
			return _hc.NEQ

def reload_config():
	"""Reload the config object"""
	_hc = ch.heuristics()
	print('Loaded '+str(_hc))
