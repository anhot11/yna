import bpy
import bmesh
import math
import numpy as np

print("=== EXPORTING MASTER HYPER-REALISTIC CHARACTER V6 ===")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=r"I:\workzone\gotot\yna\female_basemesh_v001.blend")

if "eyes" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["eyes"], do_unlink=True)

body = bpy.data.objects["female_basemesh"]
body.name = "Body"
body.data.name = "BodyMesh"

# 1. APPLY MULTIRES LEVEL 2 (169,360 quads - silky smooth, zero facets)
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

# 4. TRUE PEACH B-SPLINE LATTICE SCULPTING
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
                        pt.co_deform.y -= 0.85 * w_weight * (1.0 - y_frac * 0.35)

                if w <= 2:
                    sign_u = -1.0 if u == 1 else 1.0
                    if u == 1 or u == 3:
                        pt.co_deform.x -= sign_u * 0.16 * (1.0 - w * 0.3)
                        pt.co_deform.y -= 0.40 * math.cos(w / 3.0 * math.pi * 0.5)

                if (w == 5 or w == 6) and (u == 0 or u == 4):
                    sign_u = -1.0 if u == 0 else 1.0
                    pt.co_deform.x += sign_u * 0.20
                if (w == 7 or w == 8) and (u == 0 or u == 4):
                    sign_u = -1.0 if u == 0 else 1.0
                    pt.co_deform.x -= sign_u * 0.18
                    
                if (w == 6 or w == 7) and u == 2 and v <= 1:
                    pt.co_deform.y += 0.35

lat_mod = body.modifiers.new(name="Lattice", type='LATTICE')
lat_mod.object = lat_obj
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier="Lattice")
bpy.data.objects.remove(lat_obj, do_unlink=True)

print("Lattice sculpting completed!")

# =====================================================================
# 5. ANATOMICAL DETAIL SCULPTING - Hyper-Realistic Body Features
# =====================================================================
# After lattice shaping, we now sculpt anatomical details using
# vertex displacement with smooth Gaussian falloff fields.
# Coordinate system after 180° Z rotation:
#   X = left/right (symmetric about 0)
#   Y = rear(-)/front(+)  — buttocks protrude toward -Y
#   Z = height
# =====================================================================

bm = bmesh.new()
bm.from_mesh(body.data)
bm.verts.ensure_lookup_table()

def gauss3d(v, cx, cy, cz, sx, sy, sz):
    """3D Gaussian weight centered at (cx,cy,cz) with sigmas (sx,sy,sz)"""
    dx = (v.co.x - cx) / sx
    dy = (v.co.y - cy) / sy
    dz = (v.co.z - cz) / sz
    return math.exp(-0.5 * (dx*dx + dy*dy + dz*dz))

def gauss2d_xz(v, cx, cz, sx, sz):
    """2D Gaussian in X-Z plane"""
    dx = (v.co.x - cx) / sx
    dz = (v.co.z - cz) / sz
    return math.exp(-0.5 * (dx*dx + dz*dz))

print("Sculpting anatomical details...")

for v in bm.verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    total_disp = [0.0, 0.0, 0.0]  # displacement along normal + specific directions
    
    # ---------------------------------------------------------------
    # A. GLUTEAL CLEFT DEEPENING (the crack between cheeks)
    # Run along X≈0 from Z=0.72 to Z=0.92, rear side (Y < 0)
    # Push vertices INWARD (toward +Y, away from camera) to carve the crack
    # ---------------------------------------------------------------
    if abs(x) < 0.06 and y < 0.02 and 0.70 < z < 0.94:
        # X-axis Gaussian: narrow at center, falls off toward cheeks
        gx = math.exp(-0.5 * (x / 0.018)**2)
        
        # Z-axis profile: strongest in middle of crack, tapers at top and bottom
        if z < 0.74:
            gz = math.exp(-0.5 * ((z - 0.74) / 0.025)**2)
        elif z > 0.91:
            gz = math.exp(-0.5 * ((z - 0.91) / 0.020)**2)
        else:
            gz = 1.0
        
        # Y-depth modulation: stronger on rear side
        gy = 1.0 if y < -0.02 else math.exp(-0.5 * ((y + 0.02) / 0.025)**2)
        
        cleft_depth = 0.022 * gx * gz * gy  # Max 22mm inward push
        total_disp[1] += cleft_depth  # Push toward +Y (inward, away from camera)
        
        # Also slightly push vertices together laterally (narrow the cleft)
        if x < 0:
            total_disp[0] += 0.004 * gx * gz * gy  # push right
        else:
            total_disp[0] -= 0.004 * gx * gz * gy  # push left
    
    # ---------------------------------------------------------------
    # B. ANAL DIMPLE / PUCKER
    # Small circular depression centered at X≈0, Y≈-0.045, Z≈0.745
    # ---------------------------------------------------------------
    anal_cx, anal_cy, anal_cz = 0.0, -0.045, 0.745
    d_anal = math.sqrt(((x - anal_cx) / 0.012)**2 + ((y - anal_cy) / 0.012)**2 + ((z - anal_cz) / 0.014)**2)
    if d_anal < 3.0:
        anal_w = math.exp(-0.5 * d_anal**2)
        # Concentric ring pucker: inward push + radial wrinkle texture
        inward = 0.008 * anal_w  # 8mm max depth
        total_disp[1] += inward  # push inward
        
        # Subtle radial wrinkle ridges (6-fold symmetry)
        if d_anal > 0.3:
            angle = math.atan2(z - anal_cz, x - anal_cx)
            wrinkle = math.sin(angle * 6.0) * 0.0012 * anal_w * (1.0 - anal_w * 0.5)
            # Apply wrinkle along normal direction using vertex normal
            total_disp[0] += v.normal.x * wrinkle
            total_disp[1] += v.normal.y * wrinkle
            total_disp[2] += v.normal.z * wrinkle
    
    # ---------------------------------------------------------------
    # C. PERINEUM BRIDGE (between anus and vulva)
    # Smooth raised bridge at X≈0, Y in [-0.03, 0.01], Z≈0.735
    # ---------------------------------------------------------------
    if abs(x) < 0.025 and -0.04 < y < 0.02 and 0.72 < z < 0.75:
        gx_p = math.exp(-0.5 * (x / 0.012)**2)
        gy_p = math.exp(-0.5 * ((y + 0.01) / 0.020)**2)
        gz_p = math.exp(-0.5 * ((z - 0.735) / 0.010)**2)
        perineum_raise = 0.003 * gx_p * gy_p * gz_p
        total_disp[1] -= perineum_raise  # Push outward (toward -Y, toward camera)
    
    # ---------------------------------------------------------------
    # D. VULVA / LABIA MAJORA
    # Two elongated ridges flanking the center at X≈±0.012
    # Y near 0 to +0.02 (front-facing underside), Z from 0.72 to 0.78
    # ---------------------------------------------------------------
    for side in [-1, 1]:
        labia_cx = side * 0.013  # Left/right offset for each labium
        labia_cy = 0.005         # Slightly front-facing
        labia_cz_center = 0.752  # Center Z of vulva region
        
        dx_lab = (x - labia_cx) / 0.008
        dy_lab = (y - labia_cy) / 0.020
        dz_lab = (z - labia_cz_center) / 0.022
        d_lab = math.sqrt(dx_lab**2 + dy_lab**2 + dz_lab**2)
        
        if d_lab < 3.0:
            lab_w = math.exp(-0.5 * d_lab**2)
            # Push outward to form the raised lip/ridge
            total_disp[1] -= 0.004 * lab_w  # Outward protrusion
            total_disp[0] += side * 0.002 * lab_w  # Slight lateral spread
    
    # E. CENTRAL VULVAR CLEFT (slit between labia)
    # A narrow inward groove along X≈0, similar to gluteal cleft but smaller
    if abs(x) < 0.015 and -0.005 < y < 0.025 and 0.73 < z < 0.77:
        gx_vc = math.exp(-0.5 * (x / 0.005)**2)
        gy_vc = math.exp(-0.5 * ((y - 0.008) / 0.015)**2)
        gz_vc = math.exp(-0.5 * ((z - 0.752) / 0.016)**2)
        vulva_groove = 0.004 * gx_vc * gy_vc * gz_vc
        total_disp[1] += vulva_groove  # Push inward to form cleft
    
    # ---------------------------------------------------------------
    # F. UNDER-BUTT CREASE (Infragluteal fold)
    # A subtle horizontal crease where butt meets thigh
    # Z ≈ 0.72, Y < 0 (rear), across full width of cheeks
    # ---------------------------------------------------------------
    if abs(x) < 0.18 and y < 0.01 and 0.70 < z < 0.74:
        gx_uf = math.exp(-0.5 * ((abs(x) - 0.09) / 0.07)**2)  # Peak at cheek centers
        gz_uf = math.exp(-0.5 * ((z - 0.717) / 0.008)**2)       # Very narrow Z band
        gy_uf = 1.0 if y < -0.02 else math.exp(-0.5 * ((y + 0.02) / 0.02)**2)
        crease_depth = 0.005 * gx_uf * gz_uf * gy_uf
        total_disp[1] += crease_depth  # Push inward
    
    # ---------------------------------------------------------------
    # G. SUBTLE DIMPLES (Venus dimples on lower back)
    # Two small dimples at X≈±0.055, Y<0, Z≈0.93
    # ---------------------------------------------------------------
    for side in [-1, 1]:
        dimple_cx = side * 0.055
        dimple_cy = -0.04
        dimple_cz = 0.93
        d_dim = math.sqrt(((x - dimple_cx) / 0.012)**2 + ((y - dimple_cy) / 0.010)**2 + ((z - dimple_cz) / 0.010)**2)
        if d_dim < 2.5:
            dim_w = math.exp(-0.5 * d_dim**2)
            total_disp[1] += 0.003 * dim_w  # Small inward push
    
    # Apply accumulated displacement
    v.co.x += total_disp[0]
    v.co.y += total_disp[1]
    v.co.z += total_disp[2]

bm.to_mesh(body.data)
bm.free()
body.data.update()

print("Anatomical detail sculpting completed!")

# 5b. RECALCULATE NORMALS after sculpting
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

print("Normals recalculated!")

# =====================================================================
# 6. MAKE GODOTUV THE PRIMARY SEAMLESS UV LAYER
# =====================================================================
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
print("Created clean seamless UVMap!")

# =====================================================================
# 7. ANATOMICAL VERTEX COLOR VARIATION
# =====================================================================
# Instead of uniform skin tone, we paint vertex colors that encode
# anatomical color variation: darker in cleft/intimate areas,
# pinker in vulva region, warmer on inner thighs.
# The shader will read these and blend with the base skin color.
# We use the Color attribute to store: R = skin_tone_factor, G = warmth, B = intimacy
# =====================================================================

# Remove existing color attributes
while len(body.data.color_attributes) > 0:
    body.data.color_attributes.remove(body.data.color_attributes[0])

# Create vertex color layer for anatomical variation
ca = body.data.color_attributes.new(name='Color', type='BYTE_COLOR', domain='CORNER')

# First do AO bake for ambient occlusion
bpy.ops.object.mode_set(mode='VERTEX_PAINT')
bpy.ops.paint.vertex_color_dirt(dirt_angle=math.radians(70), blur_strength=0.95, blur_iterations=3, clean_angle=math.radians(115))
bpy.ops.object.mode_set(mode='OBJECT')

# Now modify vertex colors to add anatomical variation
# The AO is already in R channel. We'll encode:
# R = AO * skin_darkening_factor (0.65-1.0, darker in intimate areas)
# G = warmth channel (how much to shift toward warm/pink tones)
# B = reserved (keep AO value)
for poly in body.data.polygons:
    for loop_idx in poly.loop_indices:
        vid = body.data.loops[loop_idx].vertex_index
        vert = body.data.vertices[vid]
        x, y, z = vert.co.x, vert.co.y, vert.co.z
        
        # Read current AO value
        ao = ca.data[loop_idx].color[0]  # R channel from dirt map
        
        # Calculate anatomical darkening
        darkening = 1.0
        warmth = 0.0
        
        # Gluteal cleft darkening
        if abs(x) < 0.04 and y < 0.01 and 0.72 < z < 0.92:
            gx = math.exp(-0.5 * (x / 0.015)**2)
            gy = 1.0 if y < -0.01 else math.exp(-0.5 * ((y + 0.01) / 0.02)**2)
            cleft_dark = 0.22 * gx * gy
            darkening -= cleft_dark
            warmth += 0.15 * gx * gy
        
        # Anal region darkening
        d_anal = math.sqrt((x / 0.015)**2 + ((y + 0.045) / 0.015)**2 + ((z - 0.745) / 0.018)**2)
        if d_anal < 3.0:
            anal_dark = 0.28 * math.exp(-0.5 * d_anal**2)
            darkening -= anal_dark
            warmth += 0.25 * math.exp(-0.5 * d_anal**2)
        
        # Vulva region (pinker, slightly darker)
        if abs(x) < 0.03 and -0.01 < y < 0.03 and 0.73 < z < 0.77:
            gx_v = math.exp(-0.5 * (x / 0.015)**2)
            gy_v = math.exp(-0.5 * ((y - 0.008) / 0.018)**2)
            gz_v = math.exp(-0.5 * ((z - 0.752) / 0.018)**2)
            vulva_factor = gx_v * gy_v * gz_v
            darkening -= 0.18 * vulva_factor
            warmth += 0.40 * vulva_factor  # Much pinker
        
        # Inner thigh warmth
        if z < 0.73 and abs(x) < 0.12:
            thigh_warmth = math.exp(-0.5 * ((z - 0.70) / 0.04)**2) * math.exp(-0.5 * (x / 0.08)**2)
            warmth += 0.12 * thigh_warmth
        
        # Under-butt crease darkening (infragluteal fold)
        if abs(x) < 0.16 and y < 0.01 and 0.70 < z < 0.74:
            gz_c = math.exp(-0.5 * ((z - 0.717) / 0.010)**2)
            crease_dark = 0.12 * gz_c
            darkening -= crease_dark
        
        darkening = max(0.65, min(1.0, darkening))
        warmth = max(0.0, min(1.0, warmth))
        
        # Encode: R = AO * darkening, G = warmth, B = original AO
        ca.data[loop_idx].color = (
            max(0.0, min(1.0, ao * darkening)),  # R: darkened AO
            max(0.0, min(1.0, warmth)),            # G: warmth/pinkness
            ao,                                     # B: clean AO
            1.0                                     # A: full opacity
        )

print("Anatomical vertex color variation painted!")

# =====================================================================
# 8. EXTRACT PANTIES WITH SUBDIVIDED SMOOTH BORDERS
# =====================================================================
def extract_panty(body_obj, condition_fn, name, offset):
    bm = bmesh.new()
    bm.from_mesh(body_obj.data)
    
    valid_verts = set(v for v in bm.verts if condition_fn(v))
    faces_to_keep = [f for f in bm.faces if all(v in valid_verts for v in f.verts)]
    faces_to_delete = [f for f in bm.faces if f not in faces_to_keep]
    bmesh.ops.delete(bm, geom=faces_to_delete, context='FACES_ONLY')
    
    orphan_verts = [v for v in bm.verts if len(v.link_faces) == 0]
    bmesh.ops.delete(bm, geom=orphan_verts, context='VERTS')
    
    # Smooth boundary edges for organic curve
    boundary_verts = [v for v in bm.verts if any(e.is_boundary for e in v.link_edges)]
    for _ in range(5):
        for v in boundary_verts:
            neighbors = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in boundary_verts]
            if len(neighbors) == 2:
                mid = (neighbors[0].co + neighbors[1].co) * 0.5
                v.co = v.co * 0.45 + mid * 0.55
    
    for v in bm.verts:
        v.co += v.normal * offset
        
    p_mesh = bpy.data.meshes.new(name + "Mesh")
    bm.to_mesh(p_mesh)
    bm.free()
    
    p_obj = bpy.data.objects.new(name, p_mesh)
    bpy.context.scene.collection.objects.link(p_obj)
    
    # Solidify: Real physical cloth with thickness
    sol = p_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    sol.thickness = 0.0022
    sol.offset = 1.0
    sol.use_rim = True
    sol.use_quality_normals = True
    bpy.context.view_layer.objects.active = p_obj
    bpy.ops.object.modifier_apply(modifier="Solidify")
    
    # Bevel on rims: Rounded elastic hem piping
    bev = p_obj.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = 0.0009
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    
    for p in p_obj.data.polygons:
        p.use_smooth = True
    return p_obj

# Panty 1: Classic Cheeky Bikini
def is_classic_bikini(v):
    x, y, z = v.co.x, v.co.y, v.co.z
    angle = math.atan2(x, -y)
    s = math.sin(angle)
    c = math.cos(angle)
    
    z_waist = 0.922 + 0.028 * (s * s) - 0.010 * c
    if z > z_waist:
        return False
    if abs(x) > 0.210:
        return False
        
    if y <= 0.0:
        norm_x = min(1.0, abs(x) / 0.178)
        z_leg = 0.728 + 0.168 * (norm_x ** 1.38)
        if z < z_leg:
            return False
    else:
        norm_x = min(1.0, abs(x) / 0.165)
        z_leg = 0.722 + 0.178 * (norm_x ** 1.25)
        if z < z_leg:
            return False
    return True

# Panty 2: Seamless String Thong
def is_thong(v):
    x, y, z = v.co.x, v.co.y, v.co.z
    angle = math.atan2(x, -y)
    s = math.sin(angle)
    
    z_waist = 0.925 + 0.028 * (s * s)
    if z > z_waist:
        return False
    if abs(x) > 0.205:
        return False
        
    if z >= (z_waist - 0.016):
        return True
        
    if y <= 0.0:
        if z >= 0.860:
            t = (z - 0.860) / (z_waist - 0.860)
            max_w = 0.009 + 0.15 * (t ** 1.1)
            return abs(x) <= max_w
        else:
            return z >= 0.718 and abs(x) <= 0.009
    else:
        t = max(0.0, min(1.0, (z - 0.720) / (z_waist - 0.720)))
        max_w = 0.022 + 0.13 * (t ** 1.25)
        return z >= 0.720 and abs(x) <= max_w

panty1_obj = extract_panty(body, is_classic_bikini, "Panty_Classic", 0.0030)
print("Panty 1 (Classic) created!")

panty2_obj = extract_panty(body, is_thong, "Panty_Thong", 0.0035)
print("Panty 2 (Thong) created!")

# Create clean UV coordinates for panties
for obj in [panty1_obj, panty2_obj]:
    while len(obj.data.uv_layers) > 0:
        obj.data.uv_layers.remove(obj.data.uv_layers[0])
    uv_layer = obj.data.uv_layers.new(name="UVMap")
    for poly in obj.data.polygons:
        for loop_idx in poly.loop_indices:
            vid = obj.data.loops[loop_idx].vertex_index
            vert = obj.data.vertices[vid]
            angle = math.atan2(vert.co.x, -vert.co.y)
            u_norm = (angle / math.pi) * 0.5 + 0.5
            v_norm = max(0.0, min(1.0, (vert.co.z - 0.70) / 0.30))
            uv_layer.data[loop_idx].uv = (u_norm, v_norm)
    uv_layer.active_render = True

# =====================================================================
# 9. BUILD SKELETON ARMATURE RIG WITH GAUSSIAN WEIGHTS
# =====================================================================
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

b_cheek_l = arm_data.edit_bones.new("Cheek_L")
b_cheek_l.head = (-0.110, -0.09, 0.81); b_cheek_l.tail = (-0.110, -0.19, 0.81)
b_cheek_l.parent = b_pelvis

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

# =====================================================================
# 10. FINAL NORMAL RECALCULATION FOR ALL MESHES
# =====================================================================
for obj in [body, panty1_obj, panty2_obj]:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

# =====================================================================
# 11. EXPORT GLB
# =====================================================================
out_glb = r"I:\workzone\gotot\yna\SlapSimulator\assets\models\character.glb"
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    export_skins=True,
    use_selection=False
)
print("=== MASTER HYPER-REALISTIC CHARACTER V6 EXPORTED ===")
print("Output:", out_glb)
