import bpy
import bmesh
import math

print("=== REBUILDING CHARACTER.GLB WITH REAL PHYSICAL PANTIES ===")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='I:/workzone/gotot/yna/SlapSimulator/assets/models/character.glb')

body = bpy.data.objects.get('Body')
arm_obj = bpy.data.objects.get('Armature')

# Remove old flat paper panties and icospheres
for o in ['Panty_Classic', 'Panty_Thong', 'Icosphere']:
    obj = bpy.data.objects.get(o)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

def build_panty(name, condition_fn, offset_dist=0.0022, thickness=0.0022):
    bm = bmesh.new()
    bm.from_mesh(body.data)
    
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
                
    # Offset along surface normal
    for v in bm.verts:
        v.co += v.normal * offset_dist
        
    mesh = bpy.data.meshes.new(name + "Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    # Solidify: Real physical cloth with thickness!
    sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    sol.thickness = thickness
    sol.offset = 1.0
    sol.use_rim = True
    sol.use_quality_normals = True
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Solidify")
    
    # Bevel on the rims: Rounded elastic hem piping!
    bev = obj.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = 0.0009
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    
    for p in obj.data.polygons:
        p.use_smooth = True
        
    return obj

# 1. Classic Cheeky Bikini
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
        # Sensual Cheeky cut
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

# 2. Seamless Continuous String Thong
def is_thong(v):
    x, y, z = v.co.x, v.co.y, v.co.z
    angle = math.atan2(x, -y)
    s = math.sin(angle)
    
    z_waist = 0.925 + 0.028 * (s * s)
    if z > z_waist:
        return False
    if abs(x) > 0.205:
        return False
        
    # Continuous waist strap band (16mm width)
    if z >= (z_waist - 0.016):
        return True
        
    if y <= 0.0: # Rear
        # Back sacrum triangle
        if z >= 0.860:
            t = (z - 0.860) / (z_waist - 0.860)
            max_w = 0.009 + 0.15 * (t ** 1.1)
            return abs(x) <= max_w
        else:
            # Cleft string
            return z >= 0.718 and abs(x) <= 0.009
    else: # Front
        t = max(0.0, min(1.0, (z - 0.720) / (z_waist - 0.720)))
        max_w = 0.022 + 0.13 * (t ** 1.25)
        return z >= 0.720 and abs(x) <= max_w

panty_classic = build_panty("Panty_Classic", is_classic_bikini, offset_dist=0.0022, thickness=0.0022)
print("Built Panty_Classic:", len(panty_classic.data.vertices), "verts")

panty_thong = build_panty("Panty_Thong", is_thong, offset_dist=0.0024, thickness=0.0024)
print("Built Panty_Thong:", len(panty_thong.data.vertices), "verts")

# Skinning weights assignment
def assign_smooth_weights(obj):
    for name in ["Root", "Pelvis", "Spine", "Cheek_L", "Cheek_R", "Thigh_L", "Thigh_R"]:
        if name not in obj.vertex_groups:
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

print("Assigning smooth harmonic skinning weights to panties...")
assign_smooth_weights(panty_classic)
assign_smooth_weights(panty_thong)

# Create clean UV coordinates for panties
for obj in [panty_classic, panty_thong]:
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

# Recalculate normals
for obj in [body, panty_classic, panty_thong]:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

out_glb = r"I:\workzone\gotot\yna\SlapSimulator\assets\models\character.glb"
print("Exporting updated character.glb to:", out_glb)
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    export_skins=True,
    use_selection=False
)
print("Successfully exported updated character.glb!")
