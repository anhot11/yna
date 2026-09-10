import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r"I:\workzone\gotot\yna\SlapSimulator\assets\models\character.glb")

# Setup camera exactly matching our CameraRig default position
cam_data = bpy.data.cameras.new(name="RenderCam")
cam_obj = bpy.data.objects.new("RenderCam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Distance = 2.15, elevated slightly looking at buttocks
cam_obj.location = (0.0, -2.15, 0.05)
cam_obj.rotation_euler = (math.radians(85), 0, 0)

# Key Light (Upper right back)
light_key = bpy.data.lights.new(name="KeyLight", type='SUN')
light_key.energy = 2.2
key_obj = bpy.data.objects.new("KeyLight", light_key)
bpy.context.scene.collection.objects.link(key_obj)
key_obj.rotation_euler = (math.radians(45), math.radians(25), math.radians(-25))

# Fill Light (Lower left front to soften shadows)
light_fill = bpy.data.lights.new(name="FillLight", type='SUN')
light_fill.energy = 0.8
fill_obj = bpy.data.objects.new("FillLight", light_fill)
bpy.context.scene.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(-30), math.radians(-40), math.radians(60))

# Rim Light (Top back to create luscious silhouette rim)
light_rim = bpy.data.lights.new(name="RimLight", type='SUN')
light_rim.energy = 1.5
rim_obj = bpy.data.objects.new("RimLight", light_rim)
bpy.context.scene.collection.objects.link(rim_obj)
rim_obj.rotation_euler = (math.radians(75), 0, math.radians(180))

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 1280
bpy.context.scene.render.filepath = r"I:\workzone\gotot\yna\preview_studio.png"
bpy.ops.render.render(write_still=True)
print("Saved preview_studio.png")
