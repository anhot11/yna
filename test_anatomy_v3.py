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

# Multires level 2: 169,360 polygons - ultra smooth
m = body.modifiers.get("Multires")
if m:
    m.levels = 2
    bpy.ops.object.modifier_apply(modifier="Multires")

bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)

# Rotate 180 degrees around Z so buttocks face -Y (facing Godot camera)
body.rotation_euler.z = math.pi
bpy.ops.object.transform_apply(rotation=True)

for p in body.data.polygons:
    p.use_smooth = True
body.data.update()

verts = body.data.vertices

# -------------------------------------------------------------
# MASTER FEMININE POSTURE & VOLUPTUOUS ANATOMY
# -------------------------------------------------------------
for v in verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    
    # 1. Natural Sensual Lumbar Arch (Lordosis curve)
    # The lower spine (z: 0.88 to 1.15) arches gently forward (+Y)
    if 0.82 < z < 1.20:
        arch_t = math.sin((z - 0.82) / 0.38 * math.pi)
        # Arch depth up to 2.8cm forward
        v.co.y += 0.028 * arch_t * max(0.0, 1.0 - (abs(x) / 0.16)**2)

    # 2. Harmonious Thigh & Hamstring Fullness (z: 0.45 to 0.75)
    # Give the posterior thighs (hamstrings) and inner thighs natural soft volume
    if 0.45 < z < 0.76:
        thigh_t = math.sin((z - 0.45) / 0.31 * math.pi)
        # Hamstring posterior fullness
        if y < 0.02 and abs(x) > 0.03:
            v.co.y -= 0.022 * thigh_t * max(0.0, 1.0 - ((abs(x) - 0.11) / 0.08)**2)
        # Lateral thigh sweep
        if abs(x) > 0.08:
            sign_x = 1.0 if x > 0 else -1.0
            v.co.x += sign_x * 0.016 * thigh_t
        # Bring inner thighs comfortably together near crotch
        if abs(x) < 0.10 and y > -0.04 and z > 0.62:
            sign_x = 1.0 if x > 0 else -1.0
            v.co.x -= sign_x * 0.012 * math.sin((z - 0.62) / 0.14 * math.pi)

    # 3. Master Voluptuous Gluteal Fullness (z: 0.68 to 0.96, y < 0.05)
    # Round, heart-shaped, juicy, authentic peach curves!
    if y < 0.06 and 0.67 < z < 0.98:
        # Apex at |x| = 0.115, z = 0.810
        dx = abs(x) - 0.115
        dz = z - 0.810
        
        # Soft anatomical ellipsoid
        sx = 0.105
        sz = 0.098 if dz < 0 else 0.135
        
        r = math.sqrt((dx / sx)**2 + (dz / sz)**2)
        if r < 2.3:
            vol_f = math.cos(r / 2.3 * math.pi * 0.5)**2
            
            # Deep round posterior projection (-Y)
            v.co.y -= 0.108 * vol_f
            
            # Lateral flare (curving voluptuously into the hips)
            sign_x = 1.0 if x > 0 else -1.0
            v.co.x += sign_x * 0.028 * vol_f * (abs(x) / 0.12)
            
            # Gentle vertical perkiness
            if dz < 0:
                v.co.z += 0.014 * vol_f * math.sin((-dz / 0.098) * math.pi)

    # 4. Soft Natural Infragluteal Fold (Under-butt curve)
    # Blend smoothly with the newly-filled hamstrings so there is NO harsh shelf
    if y < -0.01 and 0.70 < z < 0.76 and 0.04 < abs(x) < 0.18:
        fold_z = 0.730 - 0.010 * ((abs(x) - 0.11) / 0.07)**2
        dz_f = (z - fold_z) / 0.026
        dx_f = (abs(x) - 0.11) / 0.075
        if abs(dz_f) < 1.0 and abs(dx_f) < 1.0:
            fold_f = math.cos(dz_f * math.pi * 0.5)**2 * math.cos(dx_f * math.pi * 0.5)**2
            v.co.y += 0.010 * fold_f # subtle crease, not a deep canyon!

    # 5. Smooth, Soft Cleft (eliminates the sharp center crease)
    if y < -0.04 and 0.72 < z < 0.90:
        # If vertex is in the center crevice, push it slightly back out to soften
        cleft_w = 0.028 + 0.014 * max(0.0, (z - 0.76) / 0.14)
        dist_center = abs(x) / cleft_w
        if dist_center < 1.0:
            soften_f = math.cos(dist_center * math.pi * 0.5)**2
            # Gently pull forward (+Y) to soften the crease
            v.co.y += 0.015 * soften_f

    # 6. Dimples of Venus (Sacral dimples)
    if y < -0.01 and 0.89 < z < 0.95:
        for sx in [-0.042, 0.042]:
            dd = math.sqrt(((x - sx) / 0.018)**2 + ((z - 0.918) / 0.018)**2)
            if dd < 1.5:
                v.co.y += 0.007 * math.cos(dd / 1.5 * math.pi * 0.5)**2

    # 7. Curvaceous Hourglass Hips & Waist
    if 0.76 < z < 1.15:
        if 0.95 < z < 1.10: # waist
            w_f = math.sin((z - 0.95) / 0.15 * math.pi)
            if abs(x) > 0.06:
                sign_x = 1.0 if x > 0 else -1.0
                v.co.x -= sign_x * 0.018 * w_f
        elif 0.78 < z < 0.94: # hips
            h_f = math.sin((z - 0.78) / 0.16 * math.pi)
            if abs(x) > 0.09:
                sign_x = 1.0 if x > 0 else -1.0
                v.co.x += sign_x * 0.026 * h_f

body.data.update()

# Recalculate normals
bpy.context.view_layer.objects.active = body
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# GodotUV: clean, continuous rear UV mapping
uv_godot = body.data.uv_layers.new(name="GodotUV")
body.data.uv_layers.active = uv_godot

for poly in body.data.polygons:
    for loop_idx in poly.loop_indices:
        vid = body.data.loops[loop_idx].vertex_index
        vert = body.data.vertices[vid]
        angle = math.atan2(vert.co.x, -vert.co.y)
        u_norm = (angle / math.pi) * 0.5 + 0.5
        v_norm = max(0.0, min(1.0, (vert.co.z - 0.50) / 0.85))
        uv_godot.data[loop_idx].uv = (u_norm, v_norm)

# -------------------------------------------------------------
# CAMERA & LIGHTING FOR PHOTO PREVIEWS
# -------------------------------------------------------------
cam_data = bpy.data.cameras.new(name="Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Studio Lights
key_light = bpy.data.lights.new(name="Key", type='SPOT')
key_light.energy = 55.0
key_light.spot_size = math.radians(70)
key_light.spot_blend = 0.55
key_obj = bpy.data.objects.new("Key", key_light)
bpy.context.scene.collection.objects.link(key_obj)
key_obj.location = (0.75, -1.35, 1.25)
key_obj.rotation_euler = (math.radians(48), math.radians(18), math.radians(-32))

rim_light = bpy.data.lights.new(name="Rim", type='SPOT')
rim_light.energy = 75.0
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
    bsdf.inputs["Base Color"].default_value = (0.94, 0.77, 0.70, 1.0)
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

# 1. Render Rear View
cam_obj.location = (0, -1.45, 0.81)
cam_obj.rotation_euler = (math.radians(89), 0, 0)
preview_rear = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_voluptuous_rear_v3.png"
bpy.context.scene.render.filepath = preview_rear
bpy.ops.render.render(write_still=True)
print("Rendered Rear:", preview_rear)

# 2. Render 3/4 Perspective View
cam_obj.location = (0.80, -1.25, 0.83)
cam_obj.rotation_euler = (math.radians(86), 0, math.radians(33))
preview_3q = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_voluptuous_3q_v3.png"
bpy.context.scene.render.filepath = preview_3q
bpy.ops.render.render(write_still=True)
print("Rendered 3Q:", preview_3q)
