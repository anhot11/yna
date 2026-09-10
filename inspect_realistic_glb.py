import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r"I:\workzone\gotot\yna\SlapSimulator\assets\models\character.glb")

cam_data = bpy.data.cameras.new(name="Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
# Camera behind the buttocks looking at hips (in Blender, rear is -Y)
cam_obj.location = (0, -1.35, 0.85)
cam_obj.rotation_euler = (math.radians(88), 0, 0)

light_data = bpy.data.lights.new(name="Sun", type='SUN')
light_data.energy = 2.2
light_obj = bpy.data.objects.new("Sun", light_data)
bpy.context.scene.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-30))

# Fill light
fill_data = bpy.data.lights.new(name="Fill", type='SUN')
fill_data.energy = 0.8
fill_obj = bpy.data.objects.new("Fill", fill_data)
bpy.context.scene.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(-30), 0, math.radians(45))

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 1280
bpy.context.scene.render.filepath = r"I:\workzone\gotot\yna\preview_realistic_glb.png"
bpy.ops.render.render(write_still=True)
print("Saved preview_realistic_glb.png")
