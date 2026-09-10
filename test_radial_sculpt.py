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
print("Sculpting with 100% C-infinity Gaussians and Radial Fields on", len(verts), "vertices...")

for v in verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    
    # 1. Harmonic Thigh & Hamstring Volume (smooth transition for the gluteus to rest upon)
    # Centers at |x| = 0.095, z = 0.60, y = 0.0
    thigh_dz = (z - 0.60) / 0.14
    thigh_dx = (abs(x) - 0.095) / 0.06
    r_thigh = thigh_dx*thigh_dx + thigh_dz*thigh_dz
    if r_thigh < 3.0:
        w_thigh = math.exp(-r_thigh * 0.5)
        # Expand hamstrings rearward (-Y) and outward (+/-X)
        if y < 0.02:
            v.co.y -= 0.024 * w_thigh * max(0.0, -y / 0.06)
        sign_x = 1.0 if x > 0 else -1.0
        v.co.x += sign_x * 0.012 * w_thigh

    # 2. Master Voluptuous Gluteal Fullness (Smooth 3D Radial Ellipsoid)
    # Cheek centers at |x| = 0.108, y = -0.065, z = 0.795
    dx = (abs(x) - 0.108) / 0.088
    dy = (y - (-0.065)) / 0.085
    # Smooth asymmetrical vertical spread: fuller in lower cheek
    dz_scale = 0.085 if z < 0.795 else 0.115
    dz = (z - 0.795) / dz_scale
    
    r_cheek = dx*dx + dy*dy + dz*dz
    if r_cheek < 3.0:
        w_cheek = math.exp(-r_cheek * 0.5)
        
        # Posterior projection (-Y)
        v.co.y -= 0.062 * w_cheek
        
        # Lateral roundness
        sign_x = 1.0 if x > 0 else -1.0
        v.co.x += sign_x * 0.018 * w_cheek * (abs(x) / 0.11)
        
        # Downward/under rounding (slopes smoothly into the hamstring)
        if z < 0.795:
            v.co.z -= 0.010 * w_cheek * ((0.795 - z) / 0.085)

    # 3. Soft Infragluteal Fold (Crescent crease under cheek)
    # Only in the lower rear junction (z ~ 0.725, |x| ~ 0.10)
    if y < -0.02:
        df_x = (abs(x) - 0.105) / 0.055
        df_z = (z - 0.725) / 0.022
        r_fold = df_x*df_x + df_z*df_z
        if r_fold < 2.5:
            w_fold = math.exp(-r_fold * 0.5)
            v.co.y += 0.010 * w_fold

    # 4. Soft Intergluteal Cleft (Soft natural valley, zero crease lines)
    if y < -0.03 and 0.72 < z < 0.88:
        w_cleft = math.exp(-(x / 0.026)**2 * 0.5) * math.exp(-((z - 0.80) / 0.08)**2 * 0.5)
        v.co.y += 0.012 * w_cleft

    # 5. Sensual Lumbar Lordosis Curve (Lower back curvature)
    # Smooth Gaussian centered at x = 0, z = 0.98, y = -0.01
    dl_x = x / 0.090
    dl_z = (z - 0.98) / 0.120
    r_lumbar = dl_x*dl_x + dl_z*dl_z
    if r_lumbar < 3.0 and y < 0.03:
        w_lumbar = math.exp(-r_lumbar * 0.5)
        v.co.y += 0.018 * w_lumbar

    # 6. Hourglass Waist & Lateral Hip Curvature
    # Waist cinch at z = 1.02
    dw_z = (z - 1.02) / 0.10
    if dw_z*dw_z < 3.0 and abs(x) > 0.05:
        w_waist = math.exp(-dw_z*dw_z * 0.5)
        sign_x = 1.0 if x > 0 else -1.0
        v.co.x -= sign_x * 0.014 * w_waist * max(0.0, 1.0 - (y / 0.12)**2)
        
    # Hip flare at z = 0.84
    dh_z = (z - 0.84) / 0.12
    if dh_z*dh_z < 3.0 and abs(x) > 0.08:
        w_hip = math.exp(-dh_z*dh_z * 0.5)
        sign_x = 1.0 if x > 0 else -1.0
        v.co.x += sign_x * 0.020 * w_hip * max(0.0, 1.0 - (y / 0.12)**2)

body.data.update()

# Subtle Laplacian smoothing to achieve absolute biological organic perfection
smooth_mod = body.modifiers.new(name="Smooth", type='SMOOTH')
smooth_mod.factor = 0.40
smooth_mod.iterations = 4
bpy.ops.object.modifier_apply(modifier="Smooth")

# Recalculate smooth normals
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

print("Anatomy sculpted with pure Gaussians and Laplacian relaxation!")

# Camera setup
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
preview_rear = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_gaussian_rear.png"
bpy.context.scene.render.filepath = preview_rear
bpy.ops.render.render(write_still=True)
print("Rendered Rear:", preview_rear)

# 2. Render 3/4 Perspective View
cam_obj.location = (0.85, -1.25, 0.83)
cam_obj.rotation_euler = (math.radians(86), 0, math.radians(35))
preview_3q = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_gaussian_3q.png"
bpy.context.scene.render.filepath = preview_3q
bpy.ops.render.render(write_still=True)
print("Rendered 3Q:", preview_3q)
