import bpy, math
from mathutils import Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=r"I:\workzone\gotot\yna\female_basemesh_v001.blend")

if "eyes" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["eyes"], do_unlink=True)

body = bpy.data.objects["female_basemesh"]
body.name = "Body"
body.data.name = "BodyMesh"

# Apply Multires at level 1
m = body.modifiers.get("Multires")
if m:
    m.levels = 1
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier="Multires")

# Apply rotation matrix
mat = Matrix.Rotation(math.radians(180), 4, 'Z') @ Matrix.Rotation(math.radians(90), 4, 'X')
body.data.transform(mat)
body.data.update()

for p in body.data.polygons:
    p.use_smooth = True

# Add Skin Material
mat_skin = bpy.data.materials.new("Mat_Skin")
bsdf = mat_skin.node_tree.nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.97, 0.79, 0.71, 1.0) # Warm realistic peach skin
bsdf.inputs['Roughness'].default_value = 0.42
body.data.materials.clear()
body.data.materials.append(mat_skin)

# Camera at -Y looking at buttocks (z ~ 0.82)
cam_data = bpy.data.cameras.new(name="Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = (0, -1.75, 0.82)
cam_obj.rotation_euler = (math.radians(88), 0, 0)

# Studio Lights
key_data = bpy.data.lights.new(name="Key", type='SUN')
key_data.energy = 2.2
key_obj = bpy.data.objects.new("Key", key_data)
bpy.context.scene.collection.objects.link(key_obj)
key_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-30))

fill_data = bpy.data.lights.new(name="Fill", type='SUN')
fill_data.energy = 0.8
fill_obj = bpy.data.objects.new("Fill", fill_data)
bpy.context.scene.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(-30), 0, math.radians(45))

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 1280
bpy.context.scene.render.filepath = r"I:\workzone\gotot\yna\test_realistic_perfect.png"
bpy.ops.render.render(write_still=True)
print("Saved test_realistic_perfect.png")
