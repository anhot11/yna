import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r"I:\workzone\gotot\yna\SlapSimulator\assets\models\character.glb")

# Setup camera
cam_data = bpy.data.cameras.new(name="RenderCam")
cam_obj = bpy.data.objects.new("RenderCam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Camera looking at back of character
cam_obj.location = (0.0, 1.8, -0.2)
cam_obj.rotation_euler = (math.radians(95), 0, math.radians(180))

# Light
light_data = bpy.data.lights.new(name="Light", type='SUN')
light_obj = bpy.data.objects.new("Light", light_data)
bpy.context.scene.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(45), math.radians(30), 0)

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 1280
bpy.context.scene.render.filepath = r"I:\workzone\gotot\yna\preview_render.png"
bpy.ops.render.render(write_still=True)
print("Rendered preview_render.png")
