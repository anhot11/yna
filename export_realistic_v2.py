import bpy
import bmesh
import math
import numpy as np

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=r"I:\workzone\gotot\yna\female_basemesh_v001.blend")

if "eyes" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["eyes"], do_unlink=True)

body = bpy.data.objects["female_basemesh"]
body.name = "Body"
body.data.name = "BodyMesh"

# Apply Multires at level 1 for smooth realistic geometry
m = body.modifiers.get("Multires")
if m:
    m.levels = 1
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier="Multires")

# Bake world transforms into mesh
bpy.context.view_layer.objects.active = body
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)

# Rotate 180 degrees around Z so buttocks face -Y (which exports to glTF +Z, directly towards Godot camera!)
# And Left Cheek is at -X, Right Cheek is at +X
for v in body.data.vertices:
    v.co.x = -v.co.x
    v.co.y = -v.co.y
body.data.update()

for p in body.data.polygons:
    p.use_smooth = True

coords = [v.co for v in body.data.vertices]
print(f"Rotated Body Mesh Vertices: {len(body.data.vertices)}")
print(f"Bounds: X[{min(c.x for c in coords):.2f}, {max(c.x for c in coords):.2f}] Y[{min(c.y for c in coords):.2f}, {max(c.y for c in coords):.2f}] Z[{min(c.z for c in coords):.2f}, {max(c.z for c in coords):.2f}]")

# -------------------------------------------------------------
# 1. CREATE PANTY 1: CLASSIC HIPSTER
# -------------------------------------------------------------
p1_mesh = bpy.data.meshes.new("PantyClassicMesh")
p1_verts = []
p1_faces = []
v_map1 = {}
idx1 = 0

for i, v in enumerate(body.data.vertices):
    x, y, z = v.co.x, v.co.y, v.co.z
    # In rotated space: Rear is y < 0, Front is y > 0
    # Height Z from 0.73 to 0.94
    is_panty = False
    if 0.73 <= z <= 0.94:
        if z >= 0.83:
            is_panty = True
        else:
            # lower part: covers rear cheeks (y < 0.0) and crotch (|x| < 0.09)
            if y < 0.0 or abs(x) < 0.09:
                is_panty = True

    if is_panty:
        offset_co = v.co + v.normal * 0.0032
        p1_verts.append(offset_co)
        v_map1[i] = idx1
        idx1 += 1

for poly in body.data.polygons:
    if all(vid in v_map1 for vid in poly.vertices):
        p1_faces.append([v_map1[vid] for vid in poly.vertices])

p1_mesh.from_pydata([v.to_tuple() for v in p1_verts], [], p1_faces)
p1_mesh.update()
panty1_obj = bpy.data.objects.new("Panty_Classic", p1_mesh)
bpy.context.scene.collection.objects.link(panty1_obj)
for p in p1_mesh.polygons: p.use_smooth = True

# -------------------------------------------------------------
# 2. CREATE PANTY 2: SPICY TANGA / THONG
# -------------------------------------------------------------
p2_mesh = bpy.data.meshes.new("PantyThongMesh")
p2_verts = []
p2_faces = []
v_map2 = {}
idx2 = 0

for i, v in enumerate(body.data.vertices):
    x, y, z = v.co.x, v.co.y, v.co.z
    is_thong = False
    
    # High-cut waistband string (0.88 <= z <= 0.94)
    if 0.88 <= z <= 0.94:
        is_thong = True
    # Front triangular panel (y > 0.01 in rotated space)
    elif 0.73 <= z < 0.88 and y > 0.01:
        t = (z - 0.73) / 0.15
        if abs(x) < (0.025 + 0.14 * t):
            is_thong = True
    # Crotch connector (0.70 <= z < 0.75, |x| < 0.035)
    elif 0.70 <= z < 0.75 and abs(x) < 0.035:
        is_thong = True
    # Narrow T-string along cleft between cheeks (y < -0.01, |x| < 0.014)
    elif 0.73 <= z < 0.88 and y < -0.01:
        if abs(x) < 0.014:
            is_thong = True

    if is_thong:
        offset_co = v.co + v.normal * 0.0038
        p2_verts.append(offset_co)
        v_map2[i] = idx2
        idx2 += 1

for poly in body.data.polygons:
    if all(vid in v_map2 for vid in poly.vertices):
        p2_faces.append([v_map2[vid] for vid in poly.vertices])

p2_mesh.from_pydata([v.to_tuple() for v in p2_verts], [], p2_faces)
p2_mesh.update()
panty2_obj = bpy.data.objects.new("Panty_Thong", p2_mesh)
bpy.context.scene.collection.objects.link(panty2_obj)
for p in p2_mesh.polygons: p.use_smooth = True

print(f"Panty meshes created: Classic={len(p1_faces)} faces, Thong={len(p2_faces)} faces")

# -------------------------------------------------------------
# 3. ARMATURE RIG
# -------------------------------------------------------------
arm_data = bpy.data.armatures.new("Armature")
arm_obj = bpy.data.objects.new("Armature", arm_data)
bpy.context.scene.collection.objects.link(arm_obj)

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')

b_root = arm_data.edit_bones.new("Root")
b_root.head = (0, 0, 0); b_root.tail = (0, 0, 0.2)

b_pelvis = arm_data.edit_bones.new("Pelvis")
b_pelvis.head = (0, -0.02, 0.82); b_pelvis.tail = (0, -0.02, 0.65)
b_pelvis.parent = b_root

b_spine = arm_data.edit_bones.new("Spine")
b_spine.head = (0, 0.01, 0.95); b_spine.tail = (0, 0.01, 1.35)
b_spine.parent = b_root

# Left Cheek (Screen Left, x = -0.09)
b_cheek_l = arm_data.edit_bones.new("Cheek_L")
b_cheek_l.head = (-0.09, -0.07, 0.82); b_cheek_l.tail = (-0.09, -0.17, 0.82)
b_cheek_l.parent = b_pelvis

# Right Cheek (Screen Right, x = +0.09)
b_cheek_r = arm_data.edit_bones.new("Cheek_R")
b_cheek_r.head = (0.09, -0.07, 0.82); b_cheek_r.tail = (0.09, -0.17, 0.82)
b_cheek_r.parent = b_pelvis

b_thigh_l = arm_data.edit_bones.new("Thigh_L")
b_thigh_l.head = (-0.11, 0.0, 0.65); b_thigh_l.tail = (-0.11, 0.0, 0.25)
b_thigh_l.parent = b_pelvis

b_thigh_r = arm_data.edit_bones.new("Thigh_R")
b_thigh_r.head = (0.11, 0.0, 0.65); b_thigh_r.tail = (0.11, 0.0, 0.25)
b_thigh_r.parent = b_pelvis

bpy.ops.object.mode_set(mode='OBJECT')

def assign_weights(obj):
    for name in ["Pelvis", "Spine", "Cheek_L", "Cheek_R", "Thigh_L", "Thigh_R"]:
        obj.vertex_groups.new(name=name)

    for v in obj.data.vertices:
        x, y, z = v.co.x, v.co.y, v.co.z
        dl = math.sqrt((x - (-0.09))**2 + (y - (-0.07))**2 + (z - 0.82)**2)
        dr = math.sqrt((x - 0.09)**2 + (y - (-0.07))**2 + (z - 0.82)**2)

        wl = 0.0; wr = 0.0
        if y < 0: # rear in rotated space
            if dl < 0.22 and x < 0.03:
                wl = math.exp(-(dl**2) / (2 * 0.08**2))
            if dr < 0.22 and x > -0.03:
                wr = math.exp(-(dr**2) / (2 * 0.08**2))

        wt_l = min(1.0, max(0.0, (0.70 - z) / 0.35)) if (z < 0.70 and x < 0) else 0.0
        wt_r = min(1.0, max(0.0, (0.70 - z) / 0.35)) if (z < 0.70 and x >= 0) else 0.0
        ws = min(1.0, max(0.0, (z - 0.90) / 0.35)) if z > 0.90 else 0.0

        total = wl + wr + wt_l + wt_r + ws
        wp = max(0.05, 1.0 - total)
        norm = total + wp
        if norm > 0:
            wl /= norm; wr /= norm; wt_l /= norm; wt_r /= norm; ws /= norm; wp /= norm

        if wl > 0.01: obj.vertex_groups["Cheek_L"].add([v.index], wl, 'REPLACE')
        if wr > 0.01: obj.vertex_groups["Cheek_R"].add([v.index], wr, 'REPLACE')
        if wt_l > 0.01: obj.vertex_groups["Thigh_L"].add([v.index], wt_l, 'REPLACE')
        if wt_r > 0.01: obj.vertex_groups["Thigh_R"].add([v.index], wt_r, 'REPLACE')
        if ws > 0.01: obj.vertex_groups["Spine"].add([v.index], ws, 'REPLACE')
        if wp > 0.01: obj.vertex_groups["Pelvis"].add([v.index], wp, 'REPLACE')

    mod = obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    obj.parent = arm_obj

assign_weights(body)
assign_weights(panty1_obj)
assign_weights(panty2_obj)

# -------------------------------------------------------------
# 4. MATERIALS
# -------------------------------------------------------------
mat_skin = bpy.data.materials.new("Mat_Skin")
bsdf_skin = mat_skin.node_tree.nodes.get("Principled BSDF")
bsdf_skin.inputs['Base Color'].default_value = (0.97, 0.79, 0.71, 1.0)
bsdf_skin.inputs['Roughness'].default_value = 0.40
body.data.materials.clear()
body.data.materials.append(mat_skin)

mat_p1 = bpy.data.materials.new("Mat_PantyClassic")
bsdf_p1 = mat_p1.node_tree.nodes.get("Principled BSDF")
bsdf_p1.inputs['Base Color'].default_value = (1.0, 0.55, 0.72, 1.0)
bsdf_p1.inputs['Roughness'].default_value = 0.35
panty1_obj.data.materials.append(mat_p1)

mat_p2 = bpy.data.materials.new("Mat_PantyThong")
bsdf_p2 = mat_p2.node_tree.nodes.get("Principled BSDF")
bsdf_p2.inputs['Base Color'].default_value = (0.10, 0.03, 0.05, 1.0)
bsdf_p2.inputs['Roughness'].default_value = 0.22
panty2_obj.data.materials.append(mat_p2)

# -------------------------------------------------------------
# 5. EXPORT GLB
# -------------------------------------------------------------
out_glb = r"I:\workzone\gotot\yna\SlapSimulator\assets\models\character.glb"
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    export_skins=True,
    export_materials='EXPORT',
    use_selection=False
)
print("Realistic character v2 successfully exported to:", out_glb)
