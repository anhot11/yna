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

# Multires level 2: 169,360 polygons - silky smooth
m = body.modifiers.get("Multires")
if m:
    m.levels = 2
    bpy.ops.object.modifier_apply(modifier="Multires")

# Apply initial transforms
bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)

# Rotate 180 degrees around Z so buttocks face -Y (facing Godot camera)
body.rotation_euler.z = math.pi
bpy.ops.object.transform_apply(rotation=True)

# Ensure smooth shading
for p in body.data.polygons:
    p.use_smooth = True
body.data.update()

verts = body.data.vertices

# -------------------------------------------------------------
# MASTER ANATOMICAL SCULPT: VOLUPTUOUS, PERKY, REALISTIC BUTT
# -------------------------------------------------------------
for v in verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    
    # A. Bring inner upper thighs closer together to eliminate unnatural gap
    if 0.60 < z < 0.76 and abs(x) < 0.12 and y > -0.06:
        t_gap_factor = math.cos((z - 0.68) / 0.08 * math.pi * 0.5)**2
        # Move inner thigh vertices towards center x = 0
        sign_x = 1.0 if x > 0 else -1.0
        v.co.x -= sign_x * 0.016 * max(0.0, 1.0 - abs(x) / 0.10) * t_gap_factor

    # B. Master Gluteal Volume: Full, round, voluptuous cheeks
    if y < 0.06 and 0.66 < z < 0.98:
        # Cheek apex at |x| = 0.112, z = 0.812
        dx = abs(x) - 0.112
        dz = z - 0.812
        
        # Asymmetrical teardrop falloff: broader above, tighter rounded shelf below
        sz = 0.092 if dz < 0 else 0.125
        sx = 0.095
        
        r = math.sqrt((dx / sx)**2 + (dz / sz)**2)
        if r < 2.2:
            # Smooth cosine-bell curve for organic soft tissue
            vol_factor = math.cos(r / 2.2 * math.pi * 0.5)**2
            
            # 1. Posterior projection: deep, round, gorgeous projection (-Y)
            v.co.y -= 0.096 * vol_factor
            
            # 2. Lateral roundness: cheeks flare out smoothly into hips
            sign_x = 1.0 if x > 0 else -1.0
            v.co.x += sign_x * 0.026 * vol_factor * (abs(x) / 0.12)
            
            # 3. Cheek lift: perky fullness lifting the bottom curve
            if dz < 0:
                lift_f = math.sin((-dz / 0.092) * math.pi)
                v.co.z += 0.015 * vol_factor * lift_f

    # C. Infragluteal Fold (Gluteal Crease / Under-butt shelf)
    if y < -0.01 and 0.69 < z < 0.77 and 0.03 < abs(x) < 0.18:
        crease_center_z = 0.735 - 0.012 * ((abs(x) - 0.10) / 0.07)**2
        dz_c = (z - crease_center_z) / 0.028
        dx_c = (abs(x) - 0.105) / 0.075
        if abs(dz_c) < 1.0 and abs(dx_c) < 1.0:
            c_factor = math.cos(dz_c * math.pi * 0.5)**2 * math.cos(dx_c * math.pi * 0.5)**2
            # Soft natural fold indentation
            v.co.y += 0.016 * c_factor

    # D. Soft Intergluteal Cleft
    if y < -0.03 and 0.72 < z < 0.90:
        cleft_width = 0.024 + 0.012 * max(0.0, (z - 0.76) / 0.14)
        cleft_f = math.exp(-(x**2) / (2 * cleft_width**2))
        v.co.y += 0.032 * cleft_f
        
    # E. Dimples of Venus (Sacral dimples)
    if y < -0.02 and 0.89 < z < 0.95:
        for sx in [-0.042, 0.042]:
            dd = math.sqrt(((x - sx) / 0.018)**2 + ((z - 0.918) / 0.018)**2)
            if dd < 1.5:
                v.co.y += 0.008 * math.cos(dd / 1.5 * math.pi * 0.5)**2

    # F. Hourglass Waist & Curvaceous Hips
    if 0.76 < z < 1.15:
        # Waist cinch at z ~ 1.01
        if 0.95 < z < 1.10:
            w_f = math.sin((z - 0.95) / 0.15 * math.pi)
            if abs(x) > 0.06:
                sign_x = 1.0 if x > 0 else -1.0
                v.co.x -= sign_x * 0.016 * w_f
        # Hip flare at z ~ 0.85
        elif 0.78 < z < 0.94:
            h_f = math.sin((z - 0.78) / 0.16 * math.pi)
            if abs(x) > 0.09:
                sign_x = 1.0 if x > 0 else -1.0
                v.co.x += sign_x * 0.022 * h_f

body.data.update()

# Recalculate normals smoothly
bpy.context.view_layer.objects.active = body
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# -------------------------------------------------------------
# SEAMLESS REAR UV MAPPING (No UDIM seams, zero tiles across rear!)
# -------------------------------------------------------------
# Create a dedicated UV layer "GodotUV" where the entire rear body
# is mapped continuously into [0, 1] without any seams across the buttocks!
uv_godot = body.data.uv_layers.new(name="GodotUV")
body.data.uv_layers.active = uv_godot

# Planar cylindrical / relaxed rear projection centered on buttocks:
# X from -0.32 to +0.32 -> U from 0.05 to 0.95
# Z from 0.55 to 1.35  -> V from 0.05 to 0.95
for poly in body.data.polygons:
    for loop_idx in poly.loop_indices:
        vid = body.data.loops[loop_idx].vertex_index
        vert = body.data.vertices[vid]
        
        # Continuous normalized UV projection for the entire body
        # U based on X and cylindrical angle around body center
        angle = math.atan2(vert.co.x, -vert.co.y) # rear is angle ~ 0
        u_norm = (angle / math.pi) * 0.5 + 0.5
        v_norm = clamp = max(0.0, min(1.0, (vert.co.z - 0.50) / 0.85))
        
        uv_godot.data[loop_idx].uv = (u_norm, v_norm)

print("GodotUV created with 100% continuous seam-free rear mapping!")

# -------------------------------------------------------------
# RENDER PREVIEW
# -------------------------------------------------------------
cam_data = bpy.data.cameras.new(name="Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
# Position camera behind buttocks at perfect portrait perspective
cam_obj.location = (0, -1.45, 0.81)
cam_obj.rotation_euler = (math.radians(89), 0, 0)

# Studio Lights
key_light = bpy.data.lights.new(name="Key", type='SPOT')
key_light.energy = 55.0
key_light.spot_size = math.radians(70)
key_light.spot_blend = 0.55
key_obj = bpy.data.objects.new("Key", key_light)
bpy.context.scene.collection.objects.link(key_obj)
key_obj.location = (0.70, -1.30, 1.25)
key_obj.rotation_euler = (math.radians(48), math.radians(18), math.radians(-32))

rim_light = bpy.data.lights.new(name="Rim", type='SPOT')
rim_light.energy = 70.0
rim_light.spot_size = math.radians(65)
rim_obj = bpy.data.objects.new("Rim", rim_light)
bpy.context.scene.collection.objects.link(rim_obj)
rim_obj.location = (-0.85, 0.40, 1.05)
rim_obj.rotation_euler = (math.radians(-25), math.radians(-40), math.radians(115))

fill_light = bpy.data.lights.new(name="Fill", type='SUN')
fill_light.energy = 0.5
fill_obj = bpy.data.objects.new("Fill", fill_light)
bpy.context.scene.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(65), math.radians(-15), 0)

# Realistic warm skin shader
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
preview_path = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_voluptuous_v2.png"
bpy.context.scene.render.filepath = preview_path
bpy.ops.render.render(write_still=True)
print("Rendered:", preview_path)
