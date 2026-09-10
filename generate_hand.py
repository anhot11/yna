import bpy
import bmesh
import math

bpy.ops.wm.read_factory_settings(use_empty=True)

# Create a stylized slap hand
# Palm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
palm = bpy.context.active_object
palm.name = "Hand"
palm.scale = (0.16, 0.04, 0.20)
bpy.ops.object.transform_apply(scale=True)

bm = bmesh.new()
bm.from_mesh(palm.data)

# Add fingers
finger_widths = [0.035, 0.036, 0.035, 0.032]
finger_lengths = [0.18, 0.21, 0.19, 0.15]
finger_x_positions = [-0.10, -0.03, 0.04, 0.11]

for i in range(4):
    fx = finger_x_positions[i]
    fw = finger_widths[i]
    fl = finger_lengths[i]
    
    # 2 segments per finger for natural cupping
    bmesh.ops.create_cube(bm, size=1.0, matrix=bpy.context.object.matrix_world)
    # Scale and place segment
    for v in bm.verts[-8:]:
        v.co.x = fx + v.co.x * fw
        v.co.y = -0.01 + v.co.y * 0.035 + (0.015 if v.co.z > 0 else 0.0) # slight curve inwards
        v.co.z = 0.20 + (v.co.z + 0.5) * fl

# Add thumb
bmesh.ops.create_cube(bm, size=1.0, matrix=bpy.context.object.matrix_world)
for v in bm.verts[-8:]:
    # Thumb angled outwards
    tx = -0.16 + v.co.x * 0.04
    ty = 0.01 + v.co.y * 0.04
    tz = 0.05 + (v.co.z + 0.5) * 0.12
    # Rotate thumb around Y/Z
    v.co.x = tx - 0.04 * (tz - 0.05)
    v.co.y = ty
    v.co.z = tz

bm.to_mesh(palm.data)
bm.free()

for poly in palm.data.polygons:
    poly.use_smooth = True

# Add subsurf for smooth rounded cartoon/anime hand
sub = palm.modifiers.new(name="Subsurf", type='SUBSURF')
sub.levels = 1
bpy.context.view_layer.objects.active = palm
bpy.ops.object.modifier_apply(modifier="Subsurf")

# Hand material
mat_hand = bpy.data.materials.new("Mat_Hand")
bsdf = mat_hand.node_tree.nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.97, 0.80, 0.72, 1.0)
bsdf.inputs['Roughness'].default_value = 0.5
palm.data.materials.append(mat_hand)

out_glb = r"I:\workzone\gotot\yna\SlapSimulator\assets\models\hand.glb"
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    export_materials='EXPORT',
    use_selection=False
)

print("Hand model exported successfully to:", out_glb)
