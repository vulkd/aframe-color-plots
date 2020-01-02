import os, sys, collections, pickle
from PIL import Image, ImageDraw
import cv2
from jinja2 import Template

INFILE = sys.argv[1]
BLENDER_PATH = '/Applications/Blender.app/Contents/MacOS/blender'
DIR_PATH = os.path.dirname(os.path.realpath(__file__))

def rgb_to_lab(inputRGB):
	rgb = [0,0,0]
	for idx, i in enumerate(inputRGB):
		i = float(i) / 255
		if i > 0.04045:
			i = ((i + 0.055) / 1.055) ** 2.4
		else:
			i = i / 12.92
		rgb[idx] = i * 100

	xyz = [0,0,0,]
	x = rgb[0] * 0.4124 + rgb[1] * 0.3576 + rgb[2] * 0.1805
	y = rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722
	z = rgb[0] * 0.0193 + rgb[1] * 0.1192 + rgb[2] * 0.9505
	xyz = [round(i, 4) for i in [x,y,z]]
	xyz[0] = float(xyz[0]) / 95.047  # ref_X = 95.047 Observer = 2°, Illuminant = D65
	xyz[1] = float(xyz[1]) / 100.0   # ref_Y = 100.000
	xyz[2] = float(xyz[2]) / 108.883 # ref_Z = 108.883
	for idx, i in enumerate(xyz):
		if i > 0.008856:
			i = i ** (0.3333333333333333)
		else:
			i = (7.787 * i) + (16/116)
	return xyz

def log_colors(colors, prefix=INFILE):
	# Log colors
	print('logging colors...')
	with open(prefix + '_colors.log', 'w+') as f:
		for color in list(colors):
			f.write(str(color)[1:-1] + '\n')
	with open(prefix + '_colors.pickle', 'wb') as f:
	    pickle.dump(colors, f)

	# Log unique colors
	print('logging unique colors...')
	with open(prefix + '_colors_unique.log', 'w+') as f:
		colors_unique = list(collections.Counter(colors).keys())
		for i in colors_unique:
			f.write(str(i)[1:-1] + '\n')
	with open(prefix + '_colors_unique.pickle', 'wb') as f:
	    pickle.dump(colors_unique, f)

	# Log LAB colors
	print('logging LAB colors...')
	with open(prefix + '_colors_LAB.log', 'w+') as f:
		colors_lab = [list(i) for i in collections.Counter(colors).keys()]
		colors_lab = [rgb_to_lab(i) for i in colors_lab]
		for i in colors_lab:
			f.write(str(i)[1:-1] + '\n')
	with open(prefix + '_colors_LAB.pickle', 'wb') as f:
	    pickle.dump(colors_lab, f)

	# Log unique LAB colors
	print('logging unique LAB colors...')
	with open(prefix + '_colors_unique_LAB.log', 'w+') as f:
		colors_unique = collections.Counter(colors).keys()
		colors_unique_lab = [list(i) for i in collections.Counter(colors_unique).keys()]
		colors_unique_lab = [rgb_to_lab(i) for i in colors_unique_lab]
		for i in colors_unique_lab:
			f.write(str(i)[1:-1] + '\n')
	with open(prefix + '_colors_unique_LAB.pickle', 'wb') as f:
	    pickle.dump(colors_unique_lab, f)

	# Reduce colors list size by every nth item
	# n = 100
	# colors_unique = colors_unique[0::n]
	# colors_unique_lab = colors_unique_lab[0::n]

	# Use occurences of colours to set radius
	print('setting radius of individual points...')
	r_weight = 0.1
	radii = []
	for c in colors_unique:
		radii.append(colors.count(c) * r_weight)

	# Set items dict to be passed to jinja
	print('creating items dict for jinja2...')
	items = [{
		'color': color,
		'position': [(i * 10) for i in colors_unique_lab[idx]],
		'radius': radii[idx]
	} for idx, color in enumerate(colors_unique)]

	# Reduce items list size by every nth item
	# n = 10
	# items = items[0::n]

	with open(prefix + '.pickle', 'wb') as f:
	    pickle.dump(items, f)

def save_image(colors):
	w = h = len(colors)
	im = Image.new('RGB', (int(w), int(h)))
	im_draw = ImageDraw.Draw(im)
	for idx, color in enumerate(colors):
		im_draw.line((idx,0) + (idx, int(h)), fill=color)
	del im_draw
	im.save(INFILE + '_colors.png')

def extract_colors_from_image(filename):
	im = Image.open(filename)
	colors = []
	for idx, color in enumerate(im.getcolors(maxcolors=999999)):
		rgb = color[1] if 'RGB' in im.mode else color[1][:-1]
		rgb = tuple(list(rgb[:-1])) if len(rgb) > 3 else rgb # Ignore alpha channel
		colors.append(rgb)
	print('Extracted', len(colors), 'colors from', filename)
	return colors

def main():
	# Extract colors
	colors = extract_colors_from_image(INFILE)

	# Log colors via pickle/.log files
	log_colors(colors)

	# Save barcode image
	save_image(colors)

	# Create aframe scene
	print('Creating aframe scene...')
	with open(INFILE + '.pickle', 'rb') as f:
		data = pickle.load(f)
	with open(os.path.join(DIR_PATH, 'aframe-template.html'), 'r') as f:
		template = Template(f.read())
		html = template.render({ 'items': data })
	with open(os.path.join(DIR_PATH, INFILE + '.html'), 'w+') as f:
		f.write(html)
	print('aframe scene created.')

	# Run blender script
	os.system('cp ' + INFILE + '.pickle blender_data.pickle')
	os.system(BLENDER_PATH + ' -b -P ./blender_run.py')

if __name__ == '__main__':
	main()
