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
body.select_set(True)
bpy.context.view_layer.objects.active = body

# Apply Multires at level 1 for smooth realistic geometry
m = body.modifiers.get("Multires")
if m:
    m.levels = 1
    bpy.ops.object.modifier_apply(modifier="Multires")

# Bake world transforms into mesh
bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)

# Rotate 180 degrees around Z so buttocks face -Y (glTF +Z, directly towards Godot camera!)
# And Left Cheek is at -X, Right Cheek is at +X
for v in body.data.vertices:
    v.co.x = -v.co.x
    v.co.y = -v.co.y
body.data.update()

for p in body.data.polygons:
    p.use_smooth = True

# -------------------------------------------------------------
# Compute Ambient Occlusion via Vertex Dirt Colors
# -------------------------------------------------------------
ca = body.data.color_attributes.new(name='Color', type='BYTE_COLOR', domain='CORNER')
bpy.ops.object.mode_set(mode='VERTEX_PAINT')
bpy.ops.paint.vertex_color_dirt(dirt_angle=math.radians(75), blur_strength=0.8, blur_iterations=2, clean_angle=math.radians(110))
bpy.ops.object.mode_set(mode='OBJECT')
print("Ambient Occlusion vertex colors calculated!")

# -------------------------------------------------------------
# 1. CREATE PANTIES VIA BMESH
# -------------------------------------------------------------
def extract_panty_mesh(body_obj, vids_set, name, offset):
    bm = bmesh.new()
    bm.from_mesh(body_obj.data)
    
    faces_to_remove = [f for f in bm.faces if not all(v.index in vids_set for v in f.verts)]
    bmesh.ops.delete(bm, geom=faces_to_remove, context='FACES_ONLY')
    
    orphan_verts = [v for v in bm.verts if len(v.link_faces) == 0]
    bmesh.ops.delete(bm, geom=orphan_verts, context='VERTS')
    
    for v in bm.verts:
        v.co += v.normal * offset
        
    p_mesh = bpy.data.meshes.new(name + "Mesh")
    bm.to_mesh(p_mesh)
    bm.free()
    
    p_obj = bpy.data.objects.new(name, p_mesh)
    bpy.context.scene.collection.objects.link(p_obj)
    for p in p_mesh.polygons:
        p.use_smooth = True
    return p_obj

# Panty 1: Classic Hipster
classic_vids = set()
for i, v in enumerate(body.data.vertices):
    x, y, z = v.co.x, v.co.y, v.co.z
    if abs(x) > 0.18: continue
    if 0.85 <= z <= 0.93: classic_vids.add(i)
    elif 0.75 <= z < 0.85 and y > 0 and abs(x) < 0.16: classic_vids.add(i)
    elif 0.77 <= z < 0.85 and y <= 0 and abs(x) < 0.17: classic_vids.add(i)
    elif 0.72 <= z < 0.75 and abs(x) < 0.025: classic_vids.add(i)

panty1_obj = extract_panty_mesh(body, classic_vids, "Panty_Classic", 0.0032)
print("Panty 1 (Classic) created with", len(panty1_obj.data.polygons), "faces")

# Panty 2: Spicy Thong / Tanga
thong_vids = set()
for i, v in enumerate(body.data.vertices):
    x, y, z = v.co.x, v.co.y, v.co.z
    if abs(x) > 0.18: continue
    if 0.88 <= z <= 0.93: thong_vids.add(i)
    elif 0.74 <= z < 0.88 and y > 0 and abs(x) < (0.02 + 0.13 * (z - 0.74) / 0.14): thong_vids.add(i)
    elif 0.74 <= z < 0.88 and y <= 0 and abs(x) < 0.012: thong_vids.add(i)
    elif 0.72 <= z < 0.74 and abs(x) < 0.022: thong_vids.add(i)

panty2_obj = extract_panty_mesh(body, thong_vids, "Panty_Thong", 0.0038)
print("Panty 2 (Thong) created with", len(panty2_obj.data.polygons), "faces")

# -------------------------------------------------------------
# 2. ARMATURE RIG
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
        if y < 0: # rear
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
# 3. EXPORT GLB WITH VERTEX COLORS
# -------------------------------------------------------------
out_glb = r"I:\workzone\gotot\yna\SlapSimulator\assets\models\character.glb"
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    export_skins=True,
    
    use_selection=False
)
print("Realistic character with vertex AO successfully exported to:", out_glb)
