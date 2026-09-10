import bpy
import math

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

# Set active and apply initial transforms
bpy.context.view_layer.objects.active = body
body.select_set(True)
bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)

# Rotate 180 degrees around Z so buttocks face -Y
body.rotation_euler.z = math.pi
bpy.ops.object.transform_apply(rotation=True)

for p in body.data.polygons:
    p.use_smooth = True
body.data.update()

verts = body.data.vertices
print("Starting sculpt on", len(verts), "vertices...")
modified_count = 0

for v in verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    
    # 1. Natural Sensual Lumbar Arch (z: 0.86 to 1.15)
    # The lower back spine furrow arches forward (+Y)
    if 0.86 < z < 1.15 and y < 0.02:
        arch_t = math.sin((z - 0.86) / 0.29 * math.pi)
        # Arch depth up to 2.4cm forward
        v.co.y += 0.024 * arch_t * max(0.0, 1.0 - (abs(x) / 0.14)**2)
        modified_count += 1

    # 2. Harmonious Thigh & Hamstring Fullness (z: 0.48 to 0.74)
    if 0.48 < z < 0.74:
        thigh_t = math.sin((z - 0.48) / 0.26 * math.pi)
        # Hamstrings fullness (posterior, y < 0)
        if y < 0.0:
            v.co.y -= 0.020 * thigh_t * max(0.0, 1.0 - ((abs(x) - 0.11) / 0.08)**2)
            modified_count += 1
        # Lateral thigh curves
        if abs(x) > 0.07:
            sign_x = 1.0 if x > 0 else -1.0
            v.co.x += sign_x * 0.015 * thigh_t
            modified_count += 1
        # Bring inner thighs naturally close
        if abs(x) < 0.09 and y > -0.05 and z > 0.62:
            sign_x = 1.0 if x > 0 else -1.0
            v.co.x -= sign_x * 0.012 * math.sin((z - 0.62) / 0.12 * math.pi)
            modified_count += 1

    # 3. Master Voluptuous Gluteal Fullness (z: 0.68 to 0.94, y < 0.02)
    # Full, juicy, round, natural buttocks!
    if y < 0.02 and 0.68 < z < 0.94:
        dx = abs(x) - 0.112
        dz = z - 0.805
        
        sx = 0.100
        sz = 0.095 if dz < 0 else 0.120
        
        r = math.sqrt((dx / sx)**2 + (dz / sz)**2)
        if r < 2.0:
            vol_f = math.cos(r / 2.0 * math.pi * 0.5)**2
            
            # Deep round posterior projection (-Y)
            v.co.y -= 0.088 * vol_f
            
            # Lateral cheek flare
            sign_x = 1.0 if x > 0 else -1.0
            v.co.x += sign_x * 0.024 * vol_f * (abs(x) / 0.11)
            
            # Perky lift
            if dz < 0:
                v.co.z += 0.012 * vol_f * math.sin((-dz / 0.095) * math.pi)
            modified_count += 1

    # 4. Soft Natural Infragluteal Fold (z: 0.70 to 0.75, y < -0.03)
    if y < -0.03 and 0.70 < z < 0.75 and 0.04 < abs(x) < 0.17:
        fold_z = 0.725 - 0.008 * ((abs(x) - 0.11) / 0.06)**2
        dz_f = (z - fold_z) / 0.024
        dx_f = (abs(x) - 0.11) / 0.065
        if abs(dz_f) < 1.0 and abs(dx_f) < 1.0:
            fold_f = math.cos(dz_f * math.pi * 0.5)**2 * math.cos(dx_f * math.pi * 0.5)**2
            v.co.y += 0.012 * fold_f
            modified_count += 1

    # 5. Dimples of Venus (Sacral dimples at z ~ 0.915)
    if y < -0.01 and 0.89 < z < 0.94:
        for sx in [-0.042, 0.042]:
            dd = math.sqrt(((x - sx) / 0.016)**2 + ((z - 0.915) / 0.016)**2)
            if dd < 1.5:
                v.co.y += 0.007 * math.cos(dd / 1.5 * math.pi * 0.5)**2
                modified_count += 1

    # 6. Hourglass Waist & Hips
    if 0.76 < z < 1.12:
        if 0.94 < z < 1.08: # waist cinch
            w_f = math.sin((z - 0.94) / 0.14 * math.pi)
            if abs(x) > 0.05:
                sign_x = 1.0 if x > 0 else -1.0
                v.co.x -= sign_x * 0.016 * w_f
                modified_count += 1
        elif 0.78 < z < 0.92: # hip flare
            h_f = math.sin((z - 0.78) / 0.14 * math.pi)
            if abs(x) > 0.08:
                sign_x = 1.0 if x > 0 else -1.0
                v.co.x += sign_x * 0.022 * h_f
                modified_count += 1

body.data.update()
print("Modified vertices:", modified_count)

# Recalculate smooth normals
bpy.context.view_layer.objects.active = body
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# Setup camera
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

# 1. Render Rear View
cam_obj.location = (0, -1.45, 0.81)
cam_obj.rotation_euler = (math.radians(89), 0, 0)
preview_rear = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_actual_rear.png"
bpy.context.scene.render.filepath = preview_rear
bpy.ops.render.render(write_still=True)
print("Rendered Rear:", preview_rear)

# 2. Render 3/4 Perspective View
cam_obj.location = (0.85, -1.25, 0.83)
cam_obj.rotation_euler = (math.radians(86), 0, math.radians(35))
preview_3q = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_actual_3q.png"
bpy.context.scene.render.filepath = preview_3q
bpy.ops.render.render(write_still=True)
print("Rendered 3Q:", preview_3q)
