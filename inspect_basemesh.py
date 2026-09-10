import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=r"I:\workzone\gotot\yna\female_basemesh_v001.blend")

print("--- Objects in female_basemesh_v001.blend ---")
for obj in bpy.data.objects:
    print(obj.name, obj.type)

# Render rear preview
cam_data = bpy.data.cameras.new(name="Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
# Position camera behind the character
cam_obj.location = (0, -2.2, 0.9)
cam_obj.rotation_euler = (math.radians(85), 0, 0)

light_data = bpy.data.lights.new(name="Sun", type='SUN')
light_obj = bpy.data.objects.new("Sun", light_data)
bpy.context.scene.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(50), math.radians(20), math.radians(-30))

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 1280
bpy.context.scene.render.filepath = r"I:\workzone\gotot\yna\preview_basemesh.png"
bpy.ops.render.render(write_still=True)
print("Rendered preview_basemesh.png")
