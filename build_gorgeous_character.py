import bpy
import bmesh
import math
import numpy as np

bpy.ops.wm.read_factory_settings(use_empty=True)

# -------------------------------------------------------------
# 1. SCULPT ANATOMICAL HOURGLASS LOWER BODY
# -------------------------------------------------------------
# Base root object to ensure clean name "Body"
bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.45, location=(0, 0.03, 0.38))
body_root = bpy.context.active_object
body_root.name = "Body"
body_root.scale = (0.92, 0.68, 1.0)

# Lower Back / Lumbar arch
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(0, 0.01, 0.18))
lumbar = bpy.context.active_object
lumbar.scale = (0.95, 0.74, 0.85)

# Pelvis / Hips (voluptuous widening into hips)
bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.38, location=(0, -0.02, -0.02))
pelvis = bpy.context.active_object
pelvis.scale = (1.0, 0.72, 1.0)

# Left Buttock Cheek (Round, heart-shaped, perky)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.29, location=(-0.185, -0.17, -0.11))
cheek_l = bpy.context.active_object
cheek_l.scale = (1.0, 1.20, 1.08)

# Right Buttock Cheek
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.29, location=(0.185, -0.17, -0.11))
cheek_r = bpy.context.active_object
cheek_r.scale = (1.0, 1.20, 1.08)

# Left Thigh
bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0.16, depth=0.95, location=(-0.21, 0.0, -0.68))
thigh_l = bpy.context.active_object
thigh_l.rotation_euler = (math.radians(-3), math.radians(-3), 0)

# Right Thigh
bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0.16, depth=0.95, location=(0.21, 0.0, -0.68))
thigh_r = bpy.context.active_object
thigh_r.rotation_euler = (math.radians(-3), math.radians(3), 0)

# Join all into body_root
bpy.context.view_layer.objects.active = body_root
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.join()
body = bpy.context.active_object
body.name = "Body"
body.data.name = "BodyMesh"

# Voxel remesh
body.data.remesh_voxel_size = 0.020
bpy.ops.object.voxel_remesh()

# Smooth modifier
smooth_mod = body.modifiers.new(name="Smooth", type='SMOOTH')
smooth_mod.factor = 0.95
smooth_mod.iterations = 16
bpy.ops.object.modifier_apply(modifier="Smooth")

# Indent spinal furrow and deepen cleft
mesh = body.data
for v in mesh.vertices:
    x, y, z = v.co.x, v.co.y, v.co.z
    # Lower back spine furrow
    if z > 0.08 and y < 0:
        cleft_factor = math.exp(-(x**2) / (2 * 0.025**2))
        v.co.y += 0.022 * cleft_factor
    # Gluteal cleft
    if -0.38 < z < 0.06 and y < -0.08:
        cleft_f = math.exp(-(x**2) / (2 * 0.030**2))
        v.co.y += 0.040 * cleft_f

sub = body.modifiers.new(name="Subsurf", type='SUBSURF')
sub.levels = 1
bpy.ops.object.modifier_apply(modifier="Subsurf")

for p in body.data.polygons:
    p.use_smooth = True

print("Refined Body mesh created:", len(body.data.vertices), "vertices, name:", body.name)

# -------------------------------------------------------------
# 2. CREATE PANTY 1: CLASSIC HIPSTER
# -------------------------------------------------------------
p1_mesh = bpy.data.meshes.new("PantyClassicMesh")
p1_verts = []
p1_faces = []
v_map1 = {}
idx1 = 0

for i, v in enumerate(body.data.vertices):
    x, y, z = v.co.x, v.co.y, v.co.z
    is_panty = False
    if -0.30 <= z <= 0.22:
        if z >= -0.12:
            is_panty = True
        else:
            if y < -0.05 or abs(x) < 0.20:
                is_panty = True

    if is_panty:
        offset_co = v.co + v.normal * 0.005
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
# 3. CREATE PANTY 2: SPICY TANGA / THONG
# -------------------------------------------------------------
p2_mesh = bpy.data.meshes.new("PantyThongMesh")
p2_verts = []
p2_faces = []
v_map2 = {}
idx2 = 0

for i, v in enumerate(body.data.vertices):
    x, y, z = v.co.x, v.co.y, v.co.z
    is_thong = False
    
    if 0.12 <= z <= 0.22:
        is_thong = True
    elif -0.36 <= z < 0.12 and y > 0.06:
        t = (z - (-0.36)) / 0.48
        if abs(x) < (0.05 + 0.35 * t):
            is_thong = True
    elif -0.40 <= z < -0.32 and abs(x) < 0.07:
        is_thong = True
    elif -0.38 <= z < 0.12 and y < -0.06:
        if abs(x) < 0.040:
            is_thong = True

    if is_thong:
        offset_co = v.co + v.normal * 0.006
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

print("Panty meshes created. Classic faces:", len(p1_faces), "Thong faces:", len(p2_faces))

# -------------------------------------------------------------
# 4. ARMATURE RIG
# -------------------------------------------------------------
arm_data = bpy.data.armatures.new("Armature")
arm_obj = bpy.data.objects.new("Armature", arm_data)
bpy.context.scene.collection.objects.link(arm_obj)

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')

b_root = arm_data.edit_bones.new("Root")
b_root.head = (0, 0, 0); b_root.tail = (0, 0, 0.2)

b_pelvis = arm_data.edit_bones.new("Pelvis")
b_pelvis.head = (0, -0.05, 0.0); b_pelvis.tail = (0, -0.05, -0.25)
b_pelvis.parent = b_root

b_spine = arm_data.edit_bones.new("Spine")
b_spine.head = (0, 0.04, 0.2); b_spine.tail = (0, 0.04, 0.6)
b_spine.parent = b_root

b_cheek_l = arm_data.edit_bones.new("Cheek_L")
b_cheek_l.head = (-0.185, -0.17, -0.11)
b_cheek_l.tail = (-0.185, -0.33, -0.11)
b_cheek_l.parent = b_pelvis

b_cheek_r = arm_data.edit_bones.new("Cheek_R")
b_cheek_r.head = (0.185, -0.17, -0.11)
b_cheek_r.tail = (0.185, -0.33, -0.11)
b_cheek_r.parent = b_pelvis

b_thigh_l = arm_data.edit_bones.new("Thigh_L")
b_thigh_l.head = (-0.21, 0.0, -0.50); b_thigh_l.tail = (-0.21, 0.0, -1.10)
b_thigh_l.parent = b_pelvis

b_thigh_r = arm_data.edit_bones.new("Thigh_R")
b_thigh_r.head = (0.21, 0.0, -0.50); b_thigh_r.tail = (0.21, 0.0, -1.10)
b_thigh_r.parent = b_pelvis

bpy.ops.object.mode_set(mode='OBJECT')

def assign_weights(obj):
    for name in ["Pelvis", "Spine", "Cheek_L", "Cheek_R", "Thigh_L", "Thigh_R"]:
        obj.vertex_groups.new(name=name)

    for v in obj.data.vertices:
        x, y, z = v.co.x, v.co.y, v.co.z
        dl = math.sqrt((x - (-0.185))**2 + (y - (-0.17))**2 + (z - (-0.11))**2)
        dr = math.sqrt((x - 0.185)**2 + (y - (-0.17))**2 + (z - (-0.11))**2)

        wl = 0.0; wr = 0.0
        if y < 0:
            if dl < 0.35 and x < 0.06:
                wl = math.exp(-(dl**2) / (2 * 0.13**2))
            if dr < 0.35 and x > -0.06:
                wr = math.exp(-(dr**2) / (2 * 0.13**2))

        wt_l = min(1.0, max(0.0, (-z - 0.38) / 0.5)) if (z < -0.38 and x < 0) else 0.0
        wt_r = min(1.0, max(0.0, (-z - 0.38) / 0.5)) if (z < -0.38 and x >= 0) else 0.0
        ws = min(1.0, max(0.0, (z - 0.10) / 0.4)) if z > 0.10 else 0.0

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
# 5. MATERIALS
# -------------------------------------------------------------
mat_skin = bpy.data.materials.new("Mat_Skin")
bsdf_skin = mat_skin.node_tree.nodes.get("Principled BSDF")
bsdf_skin.inputs['Base Color'].default_value = (0.97, 0.79, 0.71, 1.0)
bsdf_skin.inputs['Roughness'].default_value = 0.40
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
# 6. EXPORT GLB
# -------------------------------------------------------------
out_glb = r"I:\workzone\gotot\yna\SlapSimulator\assets\models\character.glb"
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    export_skins=True,
    export_materials='EXPORT',
    use_selection=False
)
print("Character model exported with exact name 'Body' to:", out_glb)
