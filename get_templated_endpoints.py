""" H Ratcliffe, University of Warwick, December 2018
Create list of "page" endpoints, with template name
"""
from astroid import MANAGER
from hashlib import md5
import flask_route_trees as frt

def generate_multiapp_endpoints(filename):
	"""Parse file, generate tree for each app, and extract endpoints

	Parameters:
	filename -- python file containing list of filenames each of which points to a single Flask app
	"""
	MAN = MANAGER
	with open(filename, 'r') as infile:
		file_list = infile.readlines()

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
	output_name = 'Endpoints_'+filename
	output = open(output_name, 'w')
	for file in file_list:
		#Generate an id from the common parts of all names plus one level down
		parts = file.split('/')
		while '' in parts:
			parts.remove('')
		core_name = parts[i-1]
		parts = "/".join(parts[0:i])
		id_prefix = md5(parts).hexdigest()

		ast = MAN.ast_from_file(file, source=True)
		tree = frt.parse_routing(ast, id_prefix)
		tree[0].set_id(id_prefix)
		tree[0].set_name(core_name)
		header_written = False
		for node in tree[1]:
			try:
				if tree[1][node].type[0] == "page":
					if not header_written:
						output.write(str(file)+'\n')
						header_written = True
					output.write(str(tree[1][node].route[0])+ '\t')
					output.write(str(tree[1][node].name)+ '\t')
					output.write(str(tree[1][node].type[1].value.args[0].value)+'\n')
			except:
				pass
		if header_written: output.write("--------------------\n")
	output.close()

if __name__ == '__main__':

	try: input = raw_input
	except NameError: pass

	filename = input('File containing list of files:')
	generate_multiapp_endpoints(filename)
