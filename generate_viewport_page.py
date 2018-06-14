
import re

def extract_offset(dot_string, root_name):
#This is a horrible hack to extract the bounding box and
#root node location from a known content dot string
#Works only for the very specific strings I have created
	try:
		bounding_box_reg = re.match('.*?(bb="[0-9.]+,[0-9.]+,[0-9.]+,[0-9.]+).*?', repr(dot_string))
		if bounding_box_reg:
			bounding_box_string = bounding_box_reg.groups()[0]
			bounding_box = re.match('.*?([0-9.]+),([0-9.]+),([0-9.]+),([0-9.]+)', bounding_box_string).groups()
		
		else:
			bounding_box = (0, 0, 100, 100)
	except:
		bounding_box = (0, 0, 100, 100)

	try:
		pos_reg = re.match('.*?{}.*?\[.*?([0-9.]+,[0-9.]+).*?'.format(root_name), repr(dot_string))
		if pos_reg:
			pos_string = pos_reg.groups()[0]
			pos = re.match('.*?([0-9.]+),([0-9.]+)', pos_string).groups()
		
		else:
			pos = (0, 0)
	except:
		pos = (0, 0)

	frac = float(pos[0])/(float(bounding_box[2])-float(bounding_box[1]))
	return frac

def generate_page_pieces(offset, name):
#Create a JsonP fragment to correctly set the offset and filename
#Also make a copy of the viewport page, with the correct jsonp include

	jsonp_name = name + '.jsonp'

	outfile = open(jsonp_name, 'w')
	outfile.write("var rootNodeOffset = {0};".format(offset))
	outfile.write("var imgSource = '{0}.png';".format(name))
	outfile.close()

	outfile = open(name+'.html', 'w')
	with open('viewport.html', 'r') as infile:
		for line in infile:
			if 'src="default.jsonp"' in line:
				outfile.write('<script type="text/javascript" src="{0}"></script>'.format(jsonp_name))
			else:
				outfile.write(line)
