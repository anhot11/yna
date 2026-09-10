import bpy
import bmesh
import math
import numpy as np

print("=== EXPORTING MASTER PHOTOREALISTIC CHARACTER V5 ===")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=r"I:\workzone\gotot\yna\female_basemesh_v001.blend")

if "eyes" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["eyes"], do_unlink=True)

body = bpy.data.objects["female_basemesh"]
body.name = "Body"
body.data.name = "BodyMesh"

# 1. APPLY MULTIRES LEVEL 2 (169,360 quads - silky smooth, zero facets/cuadros)
m = body.modifiers.get("Multires")
if m:
    m.levels = 2
    bpy.ops.object.modifier_apply(modifier="Multires")

bpy.context.view_layer.objects.active = body
body.select_set(True)
bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)

# 2. ROTATE 180 DEGREES AROUND Z SO BUTTOCKS FACE -Y (TOWARDS GODOT CAMERA)
body.rotation_euler.z = math.pi
bpy.ops.object.transform_apply(rotation=True)

for p in body.data.polygons:
    p.use_smooth = True
body.data.update()

# 3. NATURAL FEMININE STANCE (Rotate legs slightly inward at hip joints)
hip_l_x = -0.105; hip_r_x = 0.105; hip_z = 0.730
leg_angle = 0.065 # radians (~3.7 degrees)

for v in body.data.vertices:
    if v.co.z < 0.730:
        t = min(1.0, max(0.0, (0.730 - v.co.z) / 0.06))
        ang = leg_angle * t
        ca = math.cos(ang); sa = math.sin(ang)
        
        if v.co.x < 0:
            rel_x = v.co.x - hip_l_x
            rel_z = v.co.z - hip_z
            v.co.x = hip_l_x + (rel_x * ca + rel_z * sa)
            v.co.z = hip_z + (-rel_x * sa + rel_z * ca)
        else:
            rel_x = v.co.x - hip_r_x
            rel_z = v.co.z - hip_z
            v.co.x = hip_r_x + (rel_x * ca - rel_z * sa)
            v.co.z = hip_z + (rel_x * sa + rel_z * ca)

body.data.update()

# 4. TRUE PEACH 🍑 B-SPLINE LATTICE SCULPTING
lat_data = bpy.data.lattices.new("PeachLattice")
lat_data.points_u = 5  # X (left to right)
lat_data.points_v = 5  # Y (rear to front)
lat_data.points_w = 9  # Z (height: thighs to waist)
lat_data.interpolation_type_u = 'KEY_BSPLINE'
lat_data.interpolation_type_v = 'KEY_BSPLINE'
lat_data.interpolation_type_w = 'KEY_BSPLINE'

lat_obj = bpy.data.objects.new("PeachLattice", lat_data)
bpy.context.scene.collection.objects.link(lat_obj)

lat_obj.location = (0.0, -0.015, 0.82)
lat_obj.scale = (0.24, 0.17, 0.30)

for w in range(lat_data.points_w):
    for v in range(lat_data.points_v):
        y_frac = v / (lat_data.points_v - 1)
        for u in range(lat_data.points_u):
            idx = u + v * lat_data.points_u + w * (lat_data.points_u * lat_data.points_v)
            pt = lat_data.points[idx]
            
            if v <= 2:
                # 1. Cheeks (u=1, 3): Voluptuous Peach curves
                if (w == 3 or w == 4 or w == 5):
                    w_weight = math.sin((w - 2.5) / 3.0 * math.pi)
                    if u == 1 or u == 3:
                        pt.co_deform.y -= 1.35 * w_weight * (1.0 - y_frac * 0.35)
                        sign_u = -1.0 if u == 1 else 1.0
                        pt.co_deform.x += sign_u * 0.18 * w_weight
                        if w == 3:
                            pt.co_deform.z += 0.25 * w_weight
                            pt.co_deform.x -= sign_u * 0.08 * w_weight
                    elif u == 2:
                        # Plump cheeks touching softly in center
                        pt.co_deform.y -= 0.85 * w_weight * (1.0 - y_frac * 0.35)

                # 2. Harmonious Thighs
                if w <= 2:
                    sign_u = -1.0 if u == 1 else 1.0
                    if u == 1 or u == 3:
                        pt.co_deform.x -= sign_u * 0.16 * (1.0 - w * 0.3)
                        pt.co_deform.y -= 0.40 * math.cos(w / 3.0 * math.pi * 0.5)

                # 3. Hourglass Waist & Hips
                if (w == 5 or w == 6) and (u == 0 or u == 4):
                    sign_u = -1.0 if u == 0 else 1.0
                    pt.co_deform.x += sign_u * 0.20
                if (w == 7 or w == 8) and (u == 0 or u == 4):
                    sign_u = -1.0 if u == 0 else 1.0
                    pt.co_deform.x -= sign_u * 0.18
                    
                # 4. Sensual Lumbar Lordosis Arch
                if (w == 6 or w == 7) and u == 2 and v <= 1:
                    pt.co_deform.y += 0.35

# Apply lattice
lat_mod = body.modifiers.new(name="Lattice", type='LATTICE')
lat_mod.object = lat_obj
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier="Lattice")
bpy.data.objects.remove(lat_obj, do_unlink=True)

# 5. RECALCULATE NORMALS
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

print("Anatomy sculpting completed successfully!")

# 6. MAKE GODOTUV THE PRIMARY SEAMLESS UV LAYER
# Remove any old multi-tile UV layers so Godot uses clean [0, 1] coordinates
while len(body.data.uv_layers) > 0:
    body.data.uv_layers.remove(body.data.uv_layers[0])

uv_godot = body.data.uv_layers.new(name="UVMap")
for poly in body.data.polygons:
    for loop_idx in poly.loop_indices:
        vid = body.data.loops[loop_idx].vertex_index
        vert = body.data.vertices[vid]
        angle = math.atan2(vert.co.x, -vert.co.y)
        u_norm = (angle / math.pi) * 0.5 + 0.5
        v_norm = max(0.0, min(1.0, (vert.co.z - 0.45) / 0.90))
        uv_godot.data[loop_idx].uv = (u_norm, v_norm)

uv_godot.active_render = True
print("Created clean seamless UVMap in [0, 1] range!")

# 7. SILKY SMOOTH AMBIENT OCCLUSION
ca = body.data.color_attributes.new(name='Color', type='BYTE_COLOR', domain='CORNER')
bpy.ops.object.mode_set(mode='VERTEX_PAINT')
bpy.ops.paint.vertex_color_dirt(dirt_angle=math.radians(70), blur_strength=0.95, blur_iterations=3, clean_angle=math.radians(115))
bpy.ops.object.mode_set(mode='OBJECT')
print("Smooth AO vertex colors calculated!")

# 8. EXTRACT PANTIES WITH SUBDIVIDED SMOOTH BORDERS
def extract_panty(body_obj, vids_set, name, offset):
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
    
    # Subsurf modifier on panty to round out and smooth stepped staircase edges!
    sub = p_obj.modifiers.new(name="Subsurf", type='SUBSURF')
    sub.levels = 1
    bpy.context.view_layer.objects.active = p_obj
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    
    for p in p_obj.data.polygons:
        p.use_smooth = True
    return p_obj

# Panty 1: Classic Hipster Shorts
classic_vids = set()
for i, v in enumerate(body.data.vertices):
    x, y, z = v.co.x, v.co.y, v.co.z
    if abs(x) > 0.20: continue
    if 0.85 <= z <= 0.94: classic_vids.add(i)
    elif 0.75 <= z < 0.85 and y > -0.05 and abs(x) < 0.17: classic_vids.add(i)
    elif 0.77 <= z < 0.85 and y <= -0.05 and abs(x) < 0.19: classic_vids.add(i)
    elif 0.71 <= z < 0.75 and abs(x) < 0.035: classic_vids.add(i)

panty1_obj = extract_panty(body, classic_vids, "Panty_Classic", 0.0030)
print("Panty 1 (Classic) created with smooth edges!")

# Panty 2: Spicy Thong (Tanga)
thong_vids = set()
for i, v in enumerate(body.data.vertices):
    x, y, z = v.co.x, v.co.y, v.co.z
    if abs(x) > 0.20: continue
    if 0.88 <= z <= 0.94: thong_vids.add(i)
    elif 0.73 <= z < 0.88 and y > 0.0 and abs(x) < (0.02 + 0.15 * (z - 0.73) / 0.15): thong_vids.add(i)
    elif 0.73 <= z < 0.88 and y <= 0.0 and abs(x) < 0.015: thong_vids.add(i)
    elif 0.71 <= z < 0.73 and abs(x) < 0.028: thong_vids.add(i)

panty2_obj = extract_panty(body, thong_vids, "Panty_Thong", 0.0035)
print("Panty 2 (Thong) created with smooth edges!")

# 9. BUILD SKELETON ARMATURE RIG WITH GAUSSIAN WEIGHTS
arm_data = bpy.data.armatures.new("Armature")
arm_obj = bpy.data.objects.new("Armature", arm_data)
bpy.context.scene.collection.objects.link(arm_obj)

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')

b_root = arm_data.edit_bones.new("Root")
b_root.head = (0, 0, 0); b_root.tail = (0, 0, 0.2)

b_pelvis = arm_data.edit_bones.new("Pelvis")
b_pelvis.head = (0, 0.02, 0.82); b_pelvis.tail = (0, 0.02, 0.65)
b_pelvis.parent = b_root

b_spine = arm_data.edit_bones.new("Spine")
b_spine.head = (0, 0.03, 0.96); b_spine.tail = (0, 0.03, 1.35)
b_spine.parent = b_root

# Left Cheek (Screen Left, x = -0.110)
b_cheek_l = arm_data.edit_bones.new("Cheek_L")
b_cheek_l.head = (-0.110, -0.09, 0.81); b_cheek_l.tail = (-0.110, -0.19, 0.81)
b_cheek_l.parent = b_pelvis

# Right Cheek (Screen Right, x = +0.110)
b_cheek_r = arm_data.edit_bones.new("Cheek_R")
b_cheek_r.head = (0.110, -0.09, 0.81); b_cheek_r.tail = (0.110, -0.19, 0.81)
b_cheek_r.parent = b_pelvis

b_thigh_l = arm_data.edit_bones.new("Thigh_L")
b_thigh_l.head = (-0.10, 0.0, 0.65); b_thigh_l.tail = (-0.10, 0.0, 0.25)
b_thigh_l.parent = b_pelvis

b_thigh_r = arm_data.edit_bones.new("Thigh_R")
b_thigh_r.head = (0.10, 0.0, 0.65); b_thigh_r.tail = (0.10, 0.0, 0.25)
b_thigh_r.parent = b_pelvis

bpy.ops.object.mode_set(mode='OBJECT')

def assign_smooth_weights(obj):
    for name in ["Pelvis", "Spine", "Cheek_L", "Cheek_R", "Thigh_L", "Thigh_R"]:
        obj.vertex_groups.new(name=name)

    for v in obj.data.vertices:
        x, y, z = v.co.x, v.co.y, v.co.z
        
        # Smooth continuous 3D Gaussian weights
        dl = math.sqrt(((x - (-0.110)) / 0.11)**2 + ((y - (-0.09)) / 0.10)**2 + ((z - 0.81) / 0.12)**2)
        dr = math.sqrt(((x - 0.110) / 0.11)**2 + ((y - (-0.09)) / 0.10)**2 + ((z - 0.81) / 0.12)**2)

        wl = 0.0; wr = 0.0
        if y < 0.02:
            if dl < 2.5:
                cleft_decay = 1.0 if x <= 0.0 else math.exp(-(x / 0.020)**2)
                wl = math.exp(-dl**2 * 0.5) * cleft_decay
            if dr < 2.5:
                cleft_decay = 1.0 if x >= 0.0 else math.exp(-(x / 0.020)**2)
                wr = math.exp(-dr**2 * 0.5) * cleft_decay

        wt_l = math.exp(-((z - 0.55) / 0.22)**2) if (z < 0.72 and x < 0) else 0.0
        wt_r = math.exp(-((z - 0.55) / 0.22)**2) if (z < 0.72 and x >= 0) else 0.0
        ws = math.exp(-((z - 1.10) / 0.20)**2) if z > 0.90 else 0.0

        total = wl + wr + wt_l + wt_r + ws
        wp = max(0.08, 1.0 - total)
        norm = total + wp
        if norm > 0:
            wl /= norm; wr /= norm; wt_l /= norm; wt_r /= norm; ws /= norm; wp /= norm

        if wl > 0.005: obj.vertex_groups["Cheek_L"].add([v.index], wl, 'REPLACE')
        if wr > 0.005: obj.vertex_groups["Cheek_R"].add([v.index], wr, 'REPLACE')
        if wt_l > 0.005: obj.vertex_groups["Thigh_L"].add([v.index], wt_l, 'REPLACE')
        if wt_r > 0.005: obj.vertex_groups["Thigh_R"].add([v.index], wt_r, 'REPLACE')
        if ws > 0.005: obj.vertex_groups["Spine"].add([v.index], ws, 'REPLACE')
        if wp > 0.005: obj.vertex_groups["Pelvis"].add([v.index], wp, 'REPLACE')

    mod = obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    obj.parent = arm_obj

print("Assigning smooth harmonic skinning weights...")
assign_smooth_weights(body)
assign_smooth_weights(panty1_obj)
assign_smooth_weights(panty2_obj)

# 10. EXPORT GLB
out_glb = r"I:\workzone\gotot\yna\SlapSimulator\assets\models\character.glb"
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    export_skins=True,
    use_selection=False
)
print("Master photorealistic character exported successfully to:", out_glb)
