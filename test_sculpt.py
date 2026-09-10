import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)

# 1. Torso / Waist
bpy.ops.mesh.primitive_cylinder_add(radius=0.34, depth=0.5, location=(0, 0.02, 0.35))
waist = bpy.context.active_object
waist.scale = (1.0, 0.75, 1.0)

# 2. Pelvis / Hips
bpy.ops.mesh.primitive_cylinder_add(radius=0.46, depth=0.4, location=(0, 0.0, 0.0))
pelvis = bpy.context.active_object
pelvis.scale = (1.0, 0.72, 1.0)

# 3. Left Cheek (Sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(-0.20, -0.16, -0.12))
cheek_l = bpy.context.active_object
cheek_l.scale = (1.0, 1.15, 1.1)

# 4. Right Cheek (Sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(0.20, -0.16, -0.12))
cheek_r = bpy.context.active_object
cheek_r.scale = (1.0, 1.15, 1.1)

# 5. Left Thigh
bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.8, location=(-0.23, 0.0, -0.65))
thigh_l = bpy.context.active_object
thigh_l.rotation_euler = (0, -0.05, 0)

# 6. Right Thigh
bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.8, location=(0.23, 0.0, -0.65))
thigh_r = bpy.context.active_object
thigh_r.rotation_euler = (0, 0.05, 0)

# Select all and join
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.join()
body = bpy.context.active_object
body.name = "Body"

# Voxel remesh
body.data.remesh_voxel_size = 0.025
bpy.ops.object.voxel_remesh()

# Smooth modifier
smooth_mod = body.modifiers.new(name="Smooth", type='SMOOTH')
smooth_mod.factor = 1.0
smooth_mod.iterations = 15
bpy.ops.object.modifier_apply(modifier="Smooth")

# Subdivision
sub = body.modifiers.new(name="Subsurf", type='SUBSURF')
sub.levels = 1
bpy.ops.object.modifier_apply(modifier="Subsurf")

for p in body.data.polygons:
    p.use_smooth = True

print("Voxel remesh successful! Vertices:", len(body.data.vertices))

# Render a preview from behind (-Y)
cam_data = bpy.data.cameras.new(name="Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = (0.0, -2.5, -0.1)
cam_obj.rotation_euler = (math.radians(88), 0, 0)

# Light
light_data = bpy.data.lights.new(name="Sun", type='SUN')
light_obj = bpy.data.objects.new("Sun", light_data)
bpy.context.scene.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(45), math.radians(25), math.radians(-20))

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 1280
bpy.context.scene.render.filepath = r"I:\workzone\gotot\yna\test_sculpt.png"
bpy.ops.render.render(write_still=True)
print("Saved test_sculpt.png")
