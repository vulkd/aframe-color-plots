# Blender 2.79

import sys, pickle
import bpy
from mathutils import Vector

INFILE = sys.argv[-1]
RENDER_SIZE = 100 # Percentage
TRANSPARENCY = False
ALPHA_VALUE = 0.5

if INFILE.split('.')[-1] is 'py':
	exit()

# Remove default blender items
for obj in ['Cube','Lamp']:
	bpy.data.objects[obj].select = True
	bpy.ops.object.delete()

# Setup camera
CAM = bpy.context.blend_data.objects["Camera"]
# 'head-on' view
# CAM.location = (0, -8, 8)
# CAM.rotation_euler = (-2.3562, 3.1416, 3.1416)
# 'isometric-esque' view
CAM.location = (8, 0, 8)
CAM.rotation_euler = (-2.3562, 3.1416, -1.5708)

# Setup lighting
bpy.data.worlds['World'].light_settings.use_environment_light = True
bpy.data.worlds['World'].light_settings.environment_energy = 0.003

# Get items from pickled list
with open('blender_data.pickle', 'rb') as f:
    items = pickle.load(f)

# Add colors
for idx, i in enumerate(items):
	print('Creating blender object ' + str(idx) + '/' + str(len(items)), end='\r')

	color = list(i['color'])
	pos = list(x / 10 for x in i['position'])

	# Create mesh
	object_name = 'item-' + str(idx)
	bpy.ops.mesh.primitive_uv_sphere_add()
	#bpy.ops.mesh.primitive_cube_add()
	bpy.context.active_object.name = object_name
	OBJ = bpy.data.objects[object_name]

	# Set mesh positiom
	OBJ.delta_location += Vector((pos))

	# Set mesh dimensions
	size = i['radius']
	x,y,z = [i for i in [size, size, size]]
	OBJ.dimensions = (x,y,z)

	# Create material
	MAT_NAME = 'Material.' + object_name
	MAT = bpy.data.materials.new(MAT_NAME)
	MAT.diffuse_color = (color)

	MAT.use_transparency = TRANSPARENCY
	MAT.transparency_method = 'Z_TRANSPARENCY'
	MAT.alpha = ALPHA_VALUE

	# Add material to mesh
	OBJ.data.materials.append(MAT)

	# Save blend file every 1000 iterations incase of crash
	if idx % 1000 == 0:
		bpy.ops.wm.save_as_mainfile(filepath=r'./' + INFILE + '.blend')

# Save and render scene
SCENE = bpy.data.scenes["Scene"]
bpy.ops.wm.save_as_mainfile(filepath=r'./' + INFILE +'.blend')
SCENE.render.filepath = './' + INFILE + '_blender.png'
SCENE.render.resolution_percentage = RENDER_SIZE
bpy.ops.render.render(write_still=True)

exit()
