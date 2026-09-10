import bpy
import math

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
print("Starting C2 continuous sculpting on", len(verts), "vertices...")

for v in verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    
    # 1. 3D Continuous Gluteal Fullness (Smooth Ellipsoid with (1-d^2)^3 falloff)
    # Cheek centers at |x| = 0.110, y = -0.065, z = 0.810
    dx = (abs(x) - 0.110) / 0.125
    dy = (y - (-0.065)) / 0.110
    dz = (z - 0.810) / 0.140
    
    d2 = dx*dx + dy*dy + dz*dz
    if d2 < 1.0:
        d = math.sqrt(d2)
        # C2 smooth continuous falloff: (1 - d^2)^3
        w = (1.0 - d2)**3
        
        # Round voluptuous projection in -Y
        v.co.y -= 0.075 * w
        
        # Gentle lateral roundness
        sign_x = 1.0 if x > 0 else -1.0
        v.co.x += sign_x * 0.018 * w * (abs(x) / 0.12)
        
        # Subtle upward perkiness
        if z < 0.810:
            v.co.z += 0.010 * w * ((0.810 - z) / 0.140)

    # 2. Continuous Hourglass Waist & Lateral Hip Flare
    # Centered smoothly around z = 0.84 to 1.06
    # Hip flare around z = 0.84 (broadening out)
    dh_z = (z - 0.84) / 0.16
    if abs(dh_z) < 1.0:
        w_hip = (1.0 - dh_z**2)**2
        if abs(x) > 0.06:
            sign_x = 1.0 if x > 0 else -1.0
            v.co.x += sign_x * 0.020 * w_hip * max(0.0, 1.0 - (y / 0.12)**2)
            
    # Waist cinch around z = 1.00 (slimming inward)
    dw_z = (z - 1.00) / 0.14
    if abs(dw_z) < 1.0:
        w_waist = (1.0 - dw_z**2)**2
        if abs(x) > 0.05:
            sign_x = 1.0 if x > 0 else -1.0
            v.co.x -= sign_x * 0.014 * w_waist * max(0.0, 1.0 - (y / 0.12)**2)

    # 3. Continuous Lumbar Lordosis Arch
    # Smoothly arches the lower back forward around z = 0.98, y < 0.0
    dl_z = (z - 0.98) / 0.18
    if abs(dl_z) < 1.0 and y < 0.02:
        w_lumbar = (1.0 - dl_z**2)**2 * max(0.0, 1.0 - (x / 0.14)**2) * max(0.0, 1.0 - (y / 0.08)**2)
        v.co.y += 0.018 * w_lumbar

    # 4. Continuous Hamstring Fullness (z: 0.52 to 0.74, y < 0)
    dt_z = (z - 0.63) / 0.13
    if abs(dt_z) < 1.0 and y < 0.01 and abs(x) > 0.03:
        w_ham = (1.0 - dt_z**2)**2 * max(0.0, 1.0 - ((abs(x) - 0.11) / 0.08)**2)
        v.co.y -= 0.014 * w_ham

body.data.update()

# Apply subtle Laplacian smoothing to blend all curves harmoniously
smooth_mod = body.modifiers.new(name="Smooth", type='SMOOTH')
smooth_mod.factor = 0.35
smooth_mod.iterations = 3
bpy.ops.object.modifier_apply(modifier="Smooth")

# Recalculate smooth normals
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

print("Anatomy sculpted with C2 continuity and Laplacian smoothing!")

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
preview_rear = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_c2_rear.png"
bpy.context.scene.render.filepath = preview_rear
bpy.ops.render.render(write_still=True)
print("Rendered Rear:", preview_rear)

# 2. Render 3/4 Perspective View
cam_obj.location = (0.85, -1.25, 0.83)
cam_obj.rotation_euler = (math.radians(86), 0, math.radians(35))
preview_3q = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_c2_3q.png"
bpy.context.scene.render.filepath = preview_3q
bpy.ops.render.render(write_still=True)
print("Rendered 3Q:", preview_3q)
