import bpy
import bmesh
import math
import numpy as np
import os

# Clear existing scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# -------------------------------------------------------------
# 1. CREATE ANATOMICAL LOWER BODY MESH
# -------------------------------------------------------------
u_res = 64  # around circumference
v_res = 64  # vertical resolution

vertices = []
faces = []
uvs = []

z_levels = np.linspace(0.6, -1.3, v_res)

for vi, z in enumerate(z_levels):
    if z >= 0.1:
        # Waist / lower back
        t = (z - 0.1) / 0.5
        width = 0.38 + 0.06 * t
        depth_front = 0.22 + 0.02 * t
        depth_back = 0.20 + 0.04 * t
        butt_prominence = 0.0
    elif z >= -0.65:
        # Pelvis / Hips / Buttocks
        t = (z - (-0.65)) / 0.75
        peak_factor = math.sin(t * math.pi)
        width = 0.48 + 0.08 * math.sin(t * math.pi * 0.8)
        depth_front = 0.26 + 0.04 * peak_factor
        depth_back = 0.24 + 0.22 * (peak_factor ** 1.3)
        butt_prominence = peak_factor ** 1.2
    else:
        # Upper Thighs
        t = (z - (-1.3)) / 0.65
        width = 0.40 + 0.08 * t
        depth_front = 0.24 + 0.02 * t
        depth_back = 0.24 + 0.04 * t
        butt_prominence = 0.0

    for ui in range(u_res):
        theta = 2.0 * math.pi * (ui / u_res)
        sin_th = math.sin(theta)
        cos_th = math.cos(theta)

        x = width * cos_th
        y = (depth_front if sin_th >= 0 else depth_back) * sin_th

        # Sculpt cheeks on back (sin_th < -0.05)
        if sin_th < -0.05 and butt_prominence > 0.01:
            back_intensity = (-sin_th) ** 1.5
            cheek_center_dist = abs(abs(x) - 0.20)
            cheek_shape = math.exp(-(cheek_center_dist ** 2) / (2 * (0.13 ** 2)))
            cleft = 0.08 * math.exp(-(x ** 2) / (2 * (0.04 ** 2))) * butt_prominence
            y -= (0.18 * butt_prominence * cheek_shape * back_intensity) - cleft

        # Thigh split
        if z < -0.65:
            thigh_split = math.exp(-(x ** 2) / (2 * (0.06 ** 2))) * (1.0 - t)
            if abs(x) < 0.12:
                y *= (1.0 - 0.6 * thigh_split)

        vertices.append((x, y, z))
        uvs.append((ui / u_res, vi / (v_res - 1)))

# Build quad faces
for vi in range(v_res - 1):
    for ui in range(u_res):
        next_ui = (ui + 1) % u_res
        p1 = vi * u_res + ui
        p2 = vi * u_res + next_ui
        p3 = (vi + 1) * u_res + next_ui
        p4 = (vi + 1) * u_res + ui
        faces.append((p1, p2, p3, p4))

mesh = bpy.data.meshes.new("BodyMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update(calc_edges=True)

body_obj = bpy.data.objects.new("Body", mesh)
bpy.context.scene.collection.objects.link(body_obj)

for poly in mesh.polygons:
    poly.use_smooth = True

subsurf = body_obj.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 1
subsurf.render_levels = 1

bpy.context.view_layer.objects.active = body_obj
bpy.ops.object.modifier_apply(modifier="Subsurf")

print("Body mesh generated:", len(body_obj.data.vertices), "vertices")

# -------------------------------------------------------------
# 2. CREATE PANTY 1: CLASSIC HIPSTER
# -------------------------------------------------------------
panty1_mesh = bpy.data.meshes.new("PantyClassicMesh")
p1_verts = []
p1_faces = []
body_mesh = body_obj.data
v_indices = {}
new_idx = 0

for i, v in enumerate(body_mesh.vertices):
    co = v.co
    is_panty = False
    if -0.42 <= co.z <= 0.22:
        if co.z > -0.32:
            is_panty = True
        else:
            if co.y < 0:
                is_panty = True
            elif abs(co.x) < 0.18:
                is_panty = True

    if is_panty:
        offset_co = co + v.normal * 0.006
        p1_verts.append(offset_co)
        v_indices[i] = new_idx
        new_idx += 1

for poly in body_mesh.polygons:
    if all(vid in v_indices for vid in poly.vertices):
        p1_faces.append([v_indices[vid] for vid in poly.vertices])

panty1_mesh.from_pydata([v.to_tuple() for v in p1_verts], [], p1_faces)
panty1_mesh.update()
panty1_obj = bpy.data.objects.new("Panty_Classic", panty1_mesh)
bpy.context.scene.collection.objects.link(panty1_obj)

# -------------------------------------------------------------
# 3. CREATE PANTY 2: SPICY THONG
# -------------------------------------------------------------
panty2_mesh = bpy.data.meshes.new("PantyThongMesh")
p2_verts = []
p2_faces = []
v2_indices = {}
new_idx2 = 0

for i, v in enumerate(body_mesh.vertices):
    co = v.co
    is_thong = False
    if 0.12 <= co.z <= 0.22:
        is_thong = True
    elif -0.40 <= co.z < 0.12 and co.y > 0.05:
        t = (co.z - (-0.40)) / 0.52
        max_x = 0.05 + 0.35 * t
        if abs(co.x) < max_x:
            is_thong = True
    elif -0.48 <= co.z < -0.38 and abs(co.x) < 0.07:
        is_thong = True
    elif -0.45 <= co.z < 0.12 and co.y < -0.05:
        if abs(co.x) < 0.045:
            is_thong = True

    if is_thong:
        offset_co = co + v.normal * 0.007
        p2_verts.append(offset_co)
        v2_indices[i] = new_idx2
        new_idx2 += 1

for poly in body_mesh.polygons:
    if all(vid in v2_indices for vid in poly.vertices):
        p2_faces.append([v2_indices[vid] for vid in poly.vertices])

panty2_mesh.from_pydata([v.to_tuple() for v in p2_verts], [], p2_faces)
panty2_mesh.update()
panty2_obj = bpy.data.objects.new("Panty_Thong", panty2_mesh)
bpy.context.scene.collection.objects.link(panty2_obj)

print("Panty meshes created. Panty1:", len(p1_faces), "Panty2:", len(p2_faces))

# -------------------------------------------------------------
# 4. ARMATURE RIG
# -------------------------------------------------------------
armature_data = bpy.data.armatures.new("Armature")
armature_obj = bpy.data.objects.new("Armature", armature_data)
bpy.context.scene.collection.objects.link(armature_obj)

bpy.context.view_layer.objects.active = armature_obj
bpy.ops.object.mode_set(mode='EDIT')

bone_root = armature_data.edit_bones.new("Root")
bone_root.head = (0.0, 0.0, 0.0)
bone_root.tail = (0.0, 0.0, 0.2)

bone_pelvis = armature_data.edit_bones.new("Pelvis")
bone_pelvis.head = (0.0, -0.05, 0.0)
bone_pelvis.tail = (0.0, -0.05, -0.3)
bone_pelvis.parent = bone_root

bone_spine = armature_data.edit_bones.new("Spine")
bone_spine.head = (0.0, 0.05, 0.2)
bone_spine.tail = (0.0, 0.05, 0.6)
bone_spine.parent = bone_root

bone_cheek_l = armature_data.edit_bones.new("Cheek_L")
bone_cheek_l.head = (-0.20, -0.22, -0.20)
bone_cheek_l.tail = (-0.20, -0.40, -0.20)
bone_cheek_l.parent = bone_pelvis

bone_cheek_r = armature_data.edit_bones.new("Cheek_R")
bone_cheek_r.head = (0.20, -0.22, -0.20)
bone_cheek_r.tail = (0.20, -0.40, -0.20)
bone_cheek_r.parent = bone_pelvis

bone_thigh_l = armature_data.edit_bones.new("Thigh_L")
bone_thigh_l.head = (-0.22, 0.0, -0.60)
bone_thigh_l.tail = (-0.22, 0.0, -1.20)
bone_thigh_l.parent = bone_pelvis

bone_thigh_r = armature_data.edit_bones.new("Thigh_R")
bone_thigh_r.head = (0.22, 0.0, -0.60)
bone_thigh_r.tail = (0.22, 0.0, -1.20)
bone_thigh_r.parent = bone_pelvis

bpy.ops.object.mode_set(mode='OBJECT')

# -------------------------------------------------------------
# 5. VERTEX WEIGHTS
# -------------------------------------------------------------
def assign_weights(obj):
    for bname in ["Pelvis", "Spine", "Cheek_L", "Cheek_R", "Thigh_L", "Thigh_R"]:
        obj.vertex_groups.new(name=bname)

    mesh = obj.data
    for v in mesh.vertices:
        x, y, z = v.co.x, v.co.y, v.co.z
        dl = math.sqrt((x - (-0.20))**2 + (y - (-0.32))**2 + (z - (-0.20))**2)
        dr = math.sqrt((x - 0.20)**2 + (y - (-0.32))**2 + (z - (-0.20))**2)

        wl = 0.0
        wr = 0.0
        if y < 0:
            if dl < 0.35 and x < 0.05:
                wl = math.exp(-(dl**2) / (2 * 0.12**2))
            if dr < 0.35 and x > -0.05:
                wr = math.exp(-(dr**2) / (2 * 0.12**2))

        wt_l = 0.0
        wt_r = 0.0
        if z < -0.55:
            if x < 0:
                wt_l = min(1.0, (-z - 0.55) / 0.5)
            else:
                wt_r = min(1.0, (-z - 0.55) / 0.5)

        ws = max(0.0, min(1.0, (z - 0.05) / 0.4)) if z > 0.0 else 0.0
        total = wl + wr + wt_l + wt_r + ws
        wp = max(0.05, 1.0 - total)

        norm = wl + wr + wt_l + wt_r + ws + wp
        if norm > 0:
            wl /= norm
            wr /= norm
            wt_l /= norm
            wt_r /= norm
            ws /= norm
            wp /= norm

        if wl > 0.01: obj.vertex_groups["Cheek_L"].add([v.index], wl, 'REPLACE')
        if wr > 0.01: obj.vertex_groups["Cheek_R"].add([v.index], wr, 'REPLACE')
        if wt_l > 0.01: obj.vertex_groups["Thigh_L"].add([v.index], wt_l, 'REPLACE')
        if wt_r > 0.01: obj.vertex_groups["Thigh_R"].add([v.index], wt_r, 'REPLACE')
        if ws > 0.01: obj.vertex_groups["Spine"].add([v.index], ws, 'REPLACE')
        if wp > 0.01: obj.vertex_groups["Pelvis"].add([v.index], wp, 'REPLACE')

    mod = obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = armature_obj
    obj.parent = armature_obj

assign_weights(body_obj)
assign_weights(panty1_obj)
assign_weights(panty2_obj)

# -------------------------------------------------------------
# 6. MATERIALS
# -------------------------------------------------------------
mat_skin = bpy.data.materials.new("Mat_Skin")
bsdf_skin = mat_skin.node_tree.nodes.get("Principled BSDF")
bsdf_skin.inputs['Base Color'].default_value = (0.96, 0.78, 0.70, 1.0)
bsdf_skin.inputs['Roughness'].default_value = 0.42
body_obj.data.materials.append(mat_skin)

mat_p1 = bpy.data.materials.new("Mat_PantyClassic")
bsdf_p1 = mat_p1.node_tree.nodes.get("Principled BSDF")
bsdf_p1.inputs['Base Color'].default_value = (1.0, 0.55, 0.72, 1.0)
bsdf_p1.inputs['Roughness'].default_value = 0.35
panty1_obj.data.materials.append(mat_p1)

mat_p2 = bpy.data.materials.new("Mat_PantyThong")
bsdf_p2 = mat_p2.node_tree.nodes.get("Principled BSDF")
bsdf_p2.inputs['Base Color'].default_value = (0.12, 0.03, 0.05, 1.0)
bsdf_p2.inputs['Roughness'].default_value = 0.25
panty2_obj.data.materials.append(mat_p2)

# -------------------------------------------------------------
# 7. EXPORT GLB
# -------------------------------------------------------------
out_glb = r"I:\workzone\gotot\yna\SlapSimulator\assets\models\character.glb"
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    export_skins=True,
    export_materials='EXPORT',
    use_selection=False
)

print("Character model exported successfully to:", out_glb)
