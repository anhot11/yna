import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=r"I:\workzone\gotot\yna\female_basemesh_v001.blend")

# Camera behind the back (+Y looking at -Y)
cam_data = bpy.data.cameras.new(name="Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
# Position camera behind the back looking at buttocks/hips
cam_obj.location = (0, 1.85, 0.85)
cam_obj.rotation_euler = (math.radians(94), 0, math.radians(180))

light_data = bpy.data.lights.new(name="Sun", type='SUN')
light_data.energy = 2.0
light_obj = bpy.data.objects.new("Sun", light_data)
bpy.context.scene.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(45), math.radians(-25), math.radians(150))

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 1280
bpy.context.scene.render.filepath = r"I:\workzone\gotot\yna\preview_basemesh_rear.png"
bpy.ops.render.render(write_still=True)
print("Rendered preview_basemesh_rear.png")
