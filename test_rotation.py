import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=r"I:\workzone\gotot\yna\female_basemesh_v001.blend")

if "eyes" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["eyes"], do_unlink=True)

body = bpy.data.objects["female_basemesh"]
body.name = "Body"
body.data.name = "BodyMesh"

# Apply Multires at level 1 for smooth curvature
m = body.modifiers.get("Multires")
if m:
    m.levels = 1
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier="Multires")

# In original mesh:
# Feet are at Y=0, Head is at Y=1.64
# Chest is at +Z, Buttocks are at -Z
# We want:
# Head at +Z (up)
# Front at +Y
# Buttocks at -Y
# Rotating -90 degrees around X:
# Original Y (0 to 1.64) rotates to +Z (0 to 1.64)!
# Original +Z (chest) rotates to -Y?
# Wait: rotation of Vector (0, 0, 1) by -90 around X:
# [ 1   0        0     ] [0]   [ 0]
# [ 0  cos(-90) -sin(-90)] [0] = [ 1] -> +Y (Front/Chest)!
# [ 0  sin(-90)  cos(-90)] [1]   [-0]
# Original -Z (buttocks) rotates to -Y (Rear/Buttocks)!
# That is a mathematically proper 90 degree 3D rotation with determinant +1 (NO reflection, NO flipped normals)!

bpy.context.view_layer.objects.active = body
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)

# Rotate -90 degrees around X
bpy.ops.transform.rotate(value=math.radians(-90), orient_axis='X')
bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)

# Recalculate outside normals
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

for p in body.data.polygons:
    p.use_smooth = True

coords = [v.co for v in body.data.vertices]
print(f"Correctly Rotated Bounds: X[{min(c.x for c in coords):.2f}, {max(c.x for c in coords):.2f}] Y[{min(c.y for c in coords):.2f}, {max(c.y for c in coords):.2f}] Z[{min(c.z for c in coords):.2f}, {max(c.z for c in coords):.2f}]")

# Render rear view (-Y)
cam_data = bpy.data.cameras.new(name="Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
# Position camera behind the buttocks (-Y) looking at +Y
cam_obj.location = (0, -1.8, 0.85)
cam_obj.rotation_euler = (math.radians(88), 0, 0)

# Key Light
light_data = bpy.data.lights.new(name="Sun", type='SUN')
light_data.energy = 2.0
light_obj = bpy.data.objects.new("Sun", light_data)
bpy.context.scene.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-30))

# Fill Light
fill_data = bpy.data.lights.new(name="Fill", type='SUN')
fill_data.energy = 0.8
fill_obj = bpy.data.objects.new("Fill", fill_data)
bpy.context.scene.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(-30), 0, math.radians(45))

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 1280
bpy.context.scene.render.filepath = r"I:\workzone\gotot\yna\test_proper_rotation.png"
bpy.ops.render.render(write_still=True)
print("Saved test_proper_rotation.png")
