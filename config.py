""" H Ratcliffe, University of Warwick, March 2018
  Create and read config objects for heuristics and output
"""

import json

_default_file = 'default.conf'

class heuristics:
	"""Factors controlling heuristics of matching
		NEQ -- 	Power of no match
		PP -- 	Power of Placeholder-Placeholder match
		PS -- 	Power of Placeholder-String match
		SS -- 	Power of String-String match
		SP -- 	Power of String-Placeholder match
		LAY -- 	Multipler applied to each subsequent 'level' of match (set to != 1 to favour earlier or later segments
		LEN -- 	Multipler applied to length (in segments) of match
	"""
	def __init__(self, filename = _default_file):
		#If default config does not exist, create it
		if filename == _default_file:
			try:
				open(filename, 'r')
			except:
				create_default_config()
		
		json_in = read_json(filename)
		self._from_json(json_in['heuristics'])
	def _from_json(self, json_in):
		self.NEQ = json_in.get('NEQ', 0)
		self.PP = json_in.get('PP', 0)
		self.PS = json_in.get('PS', 0)
		self.SS = json_in.get('SS', 0)
		self.SP = json_in.get('SP', 0)
		self.LAY = json_in.get('LAY', 0)
		self.LEN = json_in.get('LEN', 0)
	def __str__(self):
		return json.dumps(({
		'NEQ' : self.NEQ, 
		'PP' : self.PP,
		'PS' : self.PS,
		'SS' : self.SS,
		'SP' : self.SP,
		'LAY' : self.LAY,
		'LEN' : self.LEN
		}))

class output:
	pass

def read_json(filename):
	try:
		with open(filename, 'r') as infile:
			dat = infile.read()
		json_in = json.loads(dat)
		return json_in
	except Exception as e:
		print('Could not read file '+filename)
		return json.loads('{}')

def create_default_config(filename = _default_file):
	"""Create the default config file, saved as either
	the default filename, or whatever is supplied"""

	h_conf = {}
	h_conf['NEQ'] = 0
	h_conf['PP'] = 4
	h_conf['PS'] = 1
	h_conf['SS'] = 6
	h_conf['SP'] = 2
	h_conf['LAY'] = 1
	h_conf['LEN'] = 1

	o_conf = {}

	conf = {'heuristics': h_conf, 'output':o_conf}

	try:
		with open(filename, 'w') as outfile:
			outfile.write(json.dumps(conf, indent=4, sort_keys=True))
	except Exception as e:
		print('Could not create config ' + str(e))
