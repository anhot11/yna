import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=r"I:\workzone\gotot\yna\female_basemesh_v001.blend")

body = bpy.data.objects["female_basemesh"]

# Check center vertices around x = 0
center_verts = [v for v in body.data.vertices if abs(v.co.x) < 0.005]
print(f"Center verts count: {len(center_verts)}")

# Check if there are duplicate vertices
print(f"Total vertices: {len(body.data.vertices)}")
