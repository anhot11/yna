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

# Multires level 2 gives 169,360 polygons - ultra smooth skin, zero facets/cuadros!
m = body.modifiers.get("Multires")
if m:
    m.levels = 2
    bpy.ops.object.modifier_apply(modifier="Multires")

# Apply initial transforms
bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)

# Rotate 180 degrees around Z so buttocks face -Y (which will face Godot camera!)
body.rotation_euler.z = math.pi
bpy.ops.object.transform_apply(rotation=True)

# Ensure smooth shading on all polygons
for p in body.data.polygons:
    p.use_smooth = True
body.data.update()

# Now let's sculpt the gluteal volume and hourglass anatomy
# In current coords:
# Z is height (feet 0.0, crotch ~0.72, buttocks center ~0.82, waist ~1.02, head ~1.64)
# Y is front-back: +Y is front (belly, chest), -Y is rear (back, buttocks)
# X is left-right: -X is left cheek, +X is right cheek

verts = body.data.vertices
for v in verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    
    # 1. Voluptuous Gluteal Fullness
    # Cheeks centered around |x| = 0.105, z = 0.815, y < 0
    if y < 0.05 and 0.68 < z < 0.98:
        # Distance from cheek center
        dx = abs(x) - 0.108
        dz = z - 0.815
        
        # Teardrop / heart-shaped metric: slightly more projection in center-lower cheek
        scale_z = 0.085 if dz < 0 else 0.115
        scale_x = 0.088
        
        r2 = (dx / scale_x)**2 + (dz / scale_z)**2
        if r2 < 3.5:
            # Gaussian projection backwards (-Y)
            proj_factor = math.exp(-r2 * 0.5)
            # Add up to 0.075m (7.5cm) of natural round posterior projection!
            v.co.y -= 0.078 * proj_factor
            
            # Gentle lateral fullness (curving outward)
            if abs(x) > 0.04:
                sign_x = 1.0 if x > 0 else -1.0
                v.co.x += sign_x * 0.022 * proj_factor * (abs(x) / 0.12)
                
            # Subtle lift (upwards curve into perky cheek)
            if dz < 0:
                v.co.z += 0.012 * proj_factor * (-dz / 0.08)

    # 2. Infragluteal Crease Definition (Under-butt curve)
    if y < -0.02 and 0.70 < z < 0.76 and abs(x) < 0.16:
        crease_dz = (z - 0.73) / 0.03
        crease_dx = abs(x) / 0.15
        if abs(crease_dz) < 1.0:
            crease_factor = math.cos(crease_dz * math.pi * 0.5)**2 * (1.0 - crease_dx**2)
            # Indent slightly inward (+Y) to create the natural anatomical fold
            v.co.y += 0.018 * max(0.0, crease_factor)

    # 3. Intergluteal Cleft (Deep, natural, smooth crack)
    if y < -0.04 and 0.72 < z < 0.92:
        cleft_width = 0.026 + 0.010 * max(0.0, (z - 0.78) / 0.14)
        cleft_f = math.exp(-(x**2) / (2 * cleft_width**2))
        # Deepen cleft smoothly into center
        v.co.y += 0.035 * cleft_f
        
    # 4. Dimples of Venus (Sacral dimples at top of buttocks)
    if y < -0.02 and 0.89 < z < 0.95:
        # Two dimples at x = +/- 0.042, z = 0.92
        for sx in [-0.042, 0.042]:
            dd_x = x - sx
            dd_z = z - 0.92
            dd2 = (dd_x / 0.016)**2 + (dd_z / 0.016)**2
            if dd2 < 2.0:
                v.co.y += 0.007 * math.exp(-dd2 * 0.5)

    # 5. Hourglass Waist and Lateral Hip Flare
    # Waist cinch at z ~ 1.02, Hips flare at z ~ 0.85
    if 0.75 < z < 1.15:
        # Waist cinch factor
        if 0.96 < z < 1.10:
            w_factor = math.sin((z - 0.96) / 0.14 * math.pi)
            if abs(x) > 0.06:
                sign_x = 1.0 if x > 0 else -1.0
                # Gentle slimming at waist
                v.co.x -= sign_x * 0.014 * w_factor
        # Hip flare factor
        elif 0.78 < z < 0.92:
            h_factor = math.sin((z - 0.78) / 0.14 * math.pi)
            if abs(x) > 0.10:
                sign_x = 1.0 if x > 0 else -1.0
                v.co.x += sign_x * 0.018 * h_factor

body.data.update()

# Recalculate normals to ensure 100% silky smooth lighting
bpy.context.view_layer.objects.active = body
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

print("Anatomy sculpted successfully! Vertices:", len(body.data.vertices))

# Render high-res test preview
cam_data = bpy.data.cameras.new(name="Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
# Camera behind buttocks looking at -Y
cam_obj.location = (0, -1.60, 0.82)
cam_obj.rotation_euler = (math.radians(88), 0, 0)

# Studio 3-point lighting
key_light = bpy.data.lights.new(name="Key", type='SPOT')
key_light.energy = 45.0
key_light.spot_size = math.radians(65)
key_light.spot_blend = 0.5
key_obj = bpy.data.objects.new("Key", key_light)
bpy.context.scene.collection.objects.link(key_obj)
key_obj.location = (0.75, -1.4, 1.35)
key_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(-30))

rim_light = bpy.data.lights.new(name="Rim", type='SPOT')
rim_light.energy = 60.0
rim_obj = bpy.data.objects.new("Rim", rim_light)
bpy.context.scene.collection.objects.link(rim_obj)
rim_obj.location = (-0.9, 0.5, 1.1)
rim_obj.rotation_euler = (math.radians(-30), math.radians(-45), math.radians(120))

fill_light = bpy.data.lights.new(name="Fill", type='SUN')
fill_light.energy = 0.6
fill_obj = bpy.data.objects.new("Fill", fill_light)
bpy.context.scene.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(60), math.radians(-20), 0)

# Realistic Skin Material for Blender render
mat = bpy.data.materials.new(name="RealisticSkin")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.92, 0.74, 0.66, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.38
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.25
        bsdf.inputs["Subsurface Radius"].default_value = (0.35, 0.15, 0.08)
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.25
        bsdf.inputs["Subsurface Color"].default_value = (0.95, 0.35, 0.25, 1.0)

body.data.materials.append(mat)

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 1280
preview_path = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_voluptuous_realistic.png"
bpy.context.scene.render.filepath = preview_path
bpy.ops.render.render(write_still=True)
print("Rendered:", preview_path)
