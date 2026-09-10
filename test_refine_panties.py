import bpy
import bmesh
import math

print("=== REFINING REAL PHYSICAL BIKINI & THONG ===")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='I:/workzone/gotot/yna/SlapSimulator/assets/models/character.glb')

body = bpy.data.objects.get('Body')
arm = bpy.data.objects.get('Armature')

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

# Render Thong Previews
cam_data = bpy.data.cameras.new('Cam')
cam_obj = bpy.data.objects.new('Cam', cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

light1 = bpy.data.objects.new('L1', bpy.data.lights.new('L1', 'SUN'))
light1.data.energy = 2.2
light1.rotation_euler = (math.radians(25), math.radians(20), 0)
bpy.context.scene.collection.objects.link(light1)

light2 = bpy.data.objects.new('L2', bpy.data.lights.new('L2', 'SUN'))
light2.data.energy = 1.2
light2.rotation_euler = (math.radians(15), math.radians(-40), 0)
bpy.context.scene.collection.objects.link(light2)

mat_skin = bpy.data.materials.new('Skin')
mat_skin.use_nodes = True
mat_skin.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.92, 0.75, 0.68, 1.0)
body.data.materials.clear()
body.data.materials.append(mat_skin)

mat_thong_mat = bpy.data.materials.new('ThongMat')
mat_thong_mat.use_nodes = True
mat_thong_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.10, 0.08, 0.12, 1.0)
mat_thong_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.25
panty_thong.data.materials.clear()
panty_thong.data.materials.append(mat_thong_mat)

bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512

panty_classic.hide_render = True
panty_thong.hide_render = False

cam_obj.location = (0, -1.35, 0.82)
cam_obj.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.render.filepath = 'C:/Users/kiosk/.gemini/antigravity-cli/brain/c69cd41b-33a7-42a9-9d33-a8d52789ab72/test_refined_thong_rear.png'
bpy.ops.render.render(write_still=True)
print("Rendered test_refined_thong_rear.png!")

cam_obj.location = (0.75, -1.15, 0.88)
cam_obj.rotation_euler = (math.radians(85), 0, math.radians(33))
bpy.context.scene.render.filepath = 'C:/Users/kiosk/.gemini/antigravity-cli/brain/c69cd41b-33a7-42a9-9d33-a8d52789ab72/test_refined_thong_3q.png'
bpy.ops.render.render(write_still=True)
print("Rendered test_refined_thong_3q.png!")

