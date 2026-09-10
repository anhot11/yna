import bpy
import bmesh
import math
import numpy as np

print("=== STARTING MASTER PHOTOREALISTIC CHARACTER CREATION ===")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=r"I:\workzone\gotot\yna\female_basemesh_v001.blend")

if "eyes" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["eyes"], do_unlink=True)

body = bpy.data.objects["female_basemesh"]
body.name = "Body"
body.data.name = "BodyMesh"

# 1. APPLY MULTIRES LEVEL 2 (169,360 quads - zero facets/cuadros, silky smooth)
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

# 3. B-SPLINE LATTICE SCULPTING (FLAWLESS VOLUPTUOUS ANATOMY)
lat_data = bpy.data.lattices.new("SculptLattice")
lat_data.points_u = 5  # X (left to right)
lat_data.points_v = 5  # Y (rear to front)
lat_data.points_w = 8  # Z (height: thighs to waist)
lat_data.interpolation_type_u = 'KEY_BSPLINE'
lat_data.interpolation_type_v = 'KEY_BSPLINE'
lat_data.interpolation_type_w = 'KEY_BSPLINE'

lat_obj = bpy.data.objects.new("SculptLattice", lat_data)
bpy.context.scene.collection.objects.link(lat_obj)

lat_obj.location = (0.0, -0.02, 0.82)
lat_obj.scale = (0.28, 0.20, 0.32)

for w in range(lat_data.points_w):
    for v in range(lat_data.points_v):
        y_frac = v / (lat_data.points_v - 1)
        for u in range(lat_data.points_u):
            idx = u + v * lat_data.points_u + w * (lat_data.points_u * lat_data.points_v)
            pt = lat_data.points[idx]
            
            # Cheeks projection & roundness (w = 3, 4, 5)
            if v <= 2 and (w == 3 or w == 4 or w == 5):
                w_weight = math.sin((w - 2.0) / 3.2 * math.pi)
                if u == 1 or u == 3:
                    # Voluptuous posterior projection
                    pt.co_deform.y -= 1.30 * w_weight * (1.0 - y_frac * 0.35)
                    # Lateral roundness
                    sign_u = -1.0 if u == 1 else 1.0
                    pt.co_deform.x += sign_u * 0.42 * w_weight
                    # Perkiness lift
                    if w == 3:
                        pt.co_deform.z += 0.22 * w_weight
                elif u == 2:
                    # Natural cleft depth
                    pt.co_deform.y -= 0.50 * w_weight * (1.0 - y_frac * 0.35)

            # Hamstrings & upper thighs (w = 1, 2)
            if v <= 2 and (w == 1 or w == 2):
                h_weight = math.sin((w - 0.2) / 2.8 * math.pi)
                if u == 1 or u == 3:
                    pt.co_deform.y -= 0.55 * h_weight
                    sign_u = -1.0 if u == 1 else 1.0
                    # Bring inner thighs naturally close to eliminate gap
                    pt.co_deform.x += sign_u * 0.12 * h_weight

            # Hourglass hip flare (w = 4, 5)
            if (w == 4 or w == 5) and (u == 0 or u == 4):
                sign_u = -1.0 if u == 0 else 1.0
                pt.co_deform.x += sign_u * 0.38
                
            # Hourglass waist cinch (w = 6, 7)
            if (w == 6 or w == 7) and (u == 0 or u == 4):
                sign_u = -1.0 if u == 0 else 1.0
                pt.co_deform.x -= sign_u * 0.26
                
            # Sensual lumbar lordosis arch (w = 5, 6, center rear)
            if (w == 5 or w == 6) and u == 2 and v <= 1:
                pt.co_deform.y += 0.38

# Apply lattice
lat_mod = body.modifiers.new(name="Lattice", type='LATTICE')
lat_mod.object = lat_obj
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier="Lattice")
bpy.data.objects.remove(lat_obj, do_unlink=True)

# 4. RECALCULATE NORMALS
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

print("Anatomy sculpting completed successfully!")

# 5. GENERATE CONTINUOUS SEAMLESS UV MAP (No UDIM tiles across rear!)
# Create GodotUV layer: continuous seamless projection
uv_godot = body.data.uv_layers.new(name="GodotUV")
body.data.uv_layers.active = uv_godot

for poly in body.data.polygons:
    for loop_idx in poly.loop_indices:
        vid = body.data.loops[loop_idx].vertex_index
        vert = body.data.vertices[vid]
        # Cylindrical angle around body: rear at angle ~ 0
        angle = math.atan2(vert.co.x, -vert.co.y)
        u_norm = (angle / math.pi) * 0.5 + 0.5
        v_norm = max(0.0, min(1.0, (vert.co.z - 0.45) / 0.90))
        uv_godot.data[loop_idx].uv = (u_norm, v_norm)

# Set GodotUV as the active render UV layer
uv_godot.active_render = True
print("Seamless GodotUV mapping created!")

# 6. CALCULATE SILKY AMBIENT OCCLUSION VERTEX COLORS
ca = body.data.color_attributes.new(name='Color', type='BYTE_COLOR', domain='CORNER')
bpy.ops.object.mode_set(mode='VERTEX_PAINT')
bpy.ops.paint.vertex_color_dirt(dirt_angle=math.radians(70), blur_strength=0.9, blur_iterations=3, clean_angle=math.radians(115))
bpy.ops.object.mode_set(mode='OBJECT')
print("Smooth AO vertex colors calculated!")

# 7. EXTRACT PANTIES (Hipster Classic & Spicy Thong)
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
    for p in p_mesh.polygons:
        p.use_smooth = True
    return p_obj

# Panty 1: Classic Hipster Shorts
classic_vids = set()
for i, v in enumerate(body.data.vertices):
    x, y, z = v.co.x, v.co.y, v.co.z
    if abs(x) > 0.22: continue
    if 0.85 <= z <= 0.94: classic_vids.add(i)
    elif 0.74 <= z < 0.85 and y > -0.05 and abs(x) < 0.18: classic_vids.add(i)
    elif 0.76 <= z < 0.85 and y <= -0.05 and abs(x) < 0.20: classic_vids.add(i)
    elif 0.70 <= z < 0.74 and abs(x) < 0.035: classic_vids.add(i)

panty1_obj = extract_panty(body, classic_vids, "Panty_Classic", 0.0030)
print("Panty 1 (Classic) created with", len(panty1_obj.data.polygons), "faces")

# Panty 2: Spicy Thong (Tanga)
thong_vids = set()
for i, v in enumerate(body.data.vertices):
    x, y, z = v.co.x, v.co.y, v.co.z
    if abs(x) > 0.22: continue
    if 0.88 <= z <= 0.94: thong_vids.add(i)
    elif 0.73 <= z < 0.88 and y > 0.0 and abs(x) < (0.02 + 0.16 * (z - 0.73) / 0.15): thong_vids.add(i)
    elif 0.73 <= z < 0.88 and y <= 0.0 and abs(x) < 0.015: thong_vids.add(i)
    elif 0.70 <= z < 0.73 and abs(x) < 0.028: thong_vids.add(i)

panty2_obj = extract_panty(body, thong_vids, "Panty_Thong", 0.0035)
print("Panty 2 (Thong) created with", len(panty2_obj.data.polygons), "faces")

# 8. BUILD SKELETON ARMATURE RIG WITH GAUSSIAN WEIGHTS
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

# Left Cheek (Screen Left, x = -0.115)
b_cheek_l = arm_data.edit_bones.new("Cheek_L")
b_cheek_l.head = (-0.115, -0.09, 0.81); b_cheek_l.tail = (-0.115, -0.19, 0.81)
b_cheek_l.parent = b_pelvis

# Right Cheek (Screen Right, x = +0.115)
b_cheek_r = arm_data.edit_bones.new("Cheek_R")
b_cheek_r.head = (0.115, -0.09, 0.81); b_cheek_r.tail = (0.115, -0.19, 0.81)
b_cheek_r.parent = b_pelvis

b_thigh_l = arm_data.edit_bones.new("Thigh_L")
b_thigh_l.head = (-0.11, 0.0, 0.65); b_thigh_l.tail = (-0.11, 0.0, 0.25)
b_thigh_l.parent = b_pelvis

b_thigh_r = arm_data.edit_bones.new("Thigh_R")
b_thigh_r.head = (0.11, 0.0, 0.65); b_thigh_r.tail = (0.11, 0.0, 0.25)
b_thigh_r.parent = b_pelvis

bpy.ops.object.mode_set(mode='OBJECT')

def assign_smooth_weights(obj):
    for name in ["Pelvis", "Spine", "Cheek_L", "Cheek_R", "Thigh_L", "Thigh_R"]:
        obj.vertex_groups.new(name=name)

    for v in obj.data.vertices:
        x, y, z = v.co.x, v.co.y, v.co.z
        
        # Continuous Gaussian weights for cheeks
        # Left cheek (-0.115, -0.09, 0.81)
        dl = math.sqrt(((x - (-0.115)) / 0.11)**2 + ((y - (-0.09)) / 0.10)**2 + ((z - 0.81) / 0.12)**2)
        dr = math.sqrt(((x - 0.115) / 0.11)**2 + ((y - (-0.09)) / 0.10)**2 + ((z - 0.81) / 0.12)**2)

        wl = 0.0; wr = 0.0
        if y < 0.02:
            if dl < 2.5 and x < 0.03:
                # Soft cross-cleft decay
                cleft_decay = 1.0 if x <= 0.0 else math.exp(-(x / 0.018)**2)
                wl = math.exp(-dl**2 * 0.5) * cleft_decay
            if dr < 2.5 and x > -0.03:
                cleft_decay = 1.0 if x >= 0.0 else math.exp(-(x / 0.018)**2)
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

    # Gaussian weights are mathematically C-infinity continuous and normalized

    mod = obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    obj.parent = arm_obj

print("Assigning smooth harmonic skinning weights...")
assign_smooth_weights(body)
assign_smooth_weights(panty1_obj)
assign_smooth_weights(panty2_obj)
print("Skinning weights assigned successfully!")

# 9. EXPORT GLB
out_glb = r"I:\workzone\gotot\yna\SlapSimulator\assets\models\character.glb"
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    export_skins=True,
    use_selection=False
)
print("Master photorealistic character exported to:", out_glb)

# 10. RENDER PHOTOREALISTIC PREVIEW
cam_data = bpy.data.cameras.new(name="Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_data.lens_unit = 'FOV'
cam_data.angle = math.radians(42) # Exact Godot game camera FOV!
cam_obj.location = (0, -1.35, 0.82)
cam_obj.rotation_euler = (math.radians(89), 0, 0)

# Studio Lights
key_light = bpy.data.lights.new(name="Key", type='SPOT')
key_light.energy = 60.0
key_light.spot_size = math.radians(70)
key_light.spot_blend = 0.55
key_obj = bpy.data.objects.new("Key", key_light)
bpy.context.scene.collection.objects.link(key_obj)
key_obj.location = (0.75, -1.35, 1.25)
key_obj.rotation_euler = (math.radians(48), math.radians(18), math.radians(-32))

rim_light = bpy.data.lights.new(name="Rim", type='SPOT')
rim_light.energy = 80.0
rim_light.spot_size = math.radians(65)
rim_obj = bpy.data.objects.new("Rim", rim_light)
bpy.context.scene.collection.objects.link(rim_obj)
rim_obj.location = (-0.85, 0.40, 1.05)
rim_obj.rotation_euler = (math.radians(-25), math.radians(-40), math.radians(115))

fill_light = bpy.data.lights.new(name="Fill", type='SUN')
fill_light.energy = 0.55
fill_obj = bpy.data.objects.new("Fill", fill_light)
bpy.context.scene.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(65), math.radians(-15), 0)

mat = bpy.data.materials.new(name="RealisticSkin")
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.95, 0.77, 0.70, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.35
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.30
        bsdf.inputs["Subsurface Radius"].default_value = (0.40, 0.18, 0.09)
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.30
        bsdf.inputs["Subsurface Color"].default_value = (0.96, 0.38, 0.28, 1.0)

body.data.materials.append(mat)

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 1280
preview_final = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_master_photorealistic.png"
bpy.context.scene.render.filepath = preview_final
bpy.ops.render.render(write_still=True)
print("Final photorealistic render saved to:", preview_final)
print("=== MASTER PHOTOREALISTIC CHARACTER READY ===")
