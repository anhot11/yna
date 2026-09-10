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

# -------------------------------------------------------------
# CREATE VOLUPTUOUS B-SPLINE LATTICE
# -------------------------------------------------------------
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
            
            # 1. VOLUPTUOUS BUTTOCK PROJECTION & ROUNDNESS
            # w = 3, 4, 5 (z ~ 0.76 - 0.90)
            if v <= 2 and (w == 3 or w == 4 or w == 5):
                w_weight = math.sin((w - 2.0) / 3.2 * math.pi)
                # Cheeks at u = 1 and u = 3
                if u == 1 or u == 3:
                    # Deep, luscious posterior projection
                    pt.co_deform.y -= 1.10 * w_weight * (1.0 - y_frac * 0.4)
                    # Round lateral curves
                    sign_u = -1.0 if u == 1 else 1.0
                    pt.co_deform.x += sign_u * 0.38 * w_weight
                    # Perkiness lift
                    if w == 3:
                        pt.co_deform.z += 0.20 * w_weight
                elif u == 2:
                    # Natural cleft depth
                    pt.co_deform.y -= 0.45 * w_weight * (1.0 - y_frac * 0.4)

            # 2. HAMSTRING & UPPER THIGH FULLNESS (Harmonious base)
            if v <= 2 and (w == 1 or w == 2):
                h_weight = math.sin((w - 0.2) / 2.8 * math.pi)
                if u == 1 or u == 3:
                    pt.co_deform.y -= 0.45 * h_weight
                    sign_u = -1.0 if u == 1 else 1.0
                    pt.co_deform.x += sign_u * 0.18 * h_weight

            # 3. HOURGLASS WAIST & HIP FLARE
            # Hip flare at w = 4, 5
            if (w == 4 or w == 5) and (u == 0 or u == 4):
                sign_u = -1.0 if u == 0 else 1.0
                pt.co_deform.x += sign_u * 0.35
            # Waist cinch at w = 6, 7
            if (w == 6 or w == 7) and (u == 0 or u == 4):
                sign_u = -1.0 if u == 0 else 1.0
                pt.co_deform.x -= sign_u * 0.25
                
            # 4. SENSUAL LUMBAR ARCH
            if (w == 5 or w == 6) and u == 2 and v <= 1:
                pt.co_deform.y += 0.35

# Bind and apply lattice modifier
lat_mod = body.modifiers.new(name="Lattice", type='LATTICE')
lat_mod.object = lat_obj
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier="Lattice")
bpy.data.objects.remove(lat_obj, do_unlink=True)

# Recalculate smooth normals
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

print("Voluptuous B-spline Lattice sculpt completed!")

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
preview_rear = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_lattice2_rear.png"
bpy.context.scene.render.filepath = preview_rear
bpy.ops.render.render(write_still=True)
print("Rendered Rear:", preview_rear)

# 2. Render 3/4 Perspective View
cam_obj.location = (0.85, -1.25, 0.83)
cam_obj.rotation_euler = (math.radians(86), 0, math.radians(35))
preview_3q = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72\preview_lattice2_3q.png"
bpy.context.scene.render.filepath = preview_3q
bpy.ops.render.render(write_still=True)
print("Rendered 3Q:", preview_3q)
