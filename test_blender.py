import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0))
obj = bpy.context.active_object
obj.name = "TestSphere"

out_path = r"I:\workzone\gotot\yna\test_sphere.glb"
bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB')
print("GLB export test successful!")
