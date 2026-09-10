import bpy
import bmesh
import math
import numpy as np

print("=== GENERATING REAL PHYSICAL BIKINI & THONG IN BLENDER ===")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='I:/workzone/gotot/yna/SlapSimulator/assets/models/character.glb')

body = bpy.data.objects.get('Body')
arm = bpy.data.objects.get('Armature')

# Remove old flat panties
for o in ['Panty_Classic', 'Panty_Thong', 'Icosphere']:
    obj = bpy.data.objects.get(o)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

def build_panty_from_condition(name, condition_fn, offset_dist=0.0022, thickness=0.0020):
    bm = bmesh.new()
    bm.from_mesh(body.data)
    
    # Identify faces whose vertices all satisfy condition_fn
    valid_verts = set(v for v in bm.verts if condition_fn(v))
    faces_to_keep = [f for f in bm.faces if all(v in valid_verts for v in f.verts)]
    
    faces_to_delete = [f for f in bm.faces if f not in faces_to_keep]
    bmesh.ops.delete(bm, geom=faces_to_delete, context='FACES_ONLY')
    
    orphan_verts = [v for v in bm.verts if len(v.link_faces) == 0]
    bmesh.ops.delete(bm, geom=orphan_verts, context='VERTS')
    
    # Smooth boundary edges slightly to remove any staircase stepping
    boundary_verts = [v for v in bm.verts if any(e.is_boundary for e in v.link_edges)]
    for _ in range(4):
        for v in boundary_verts:
            neighbors = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in boundary_verts]
            if len(neighbors) == 2:
                mid = (neighbors[0].co + neighbors[1].co) * 0.5
                v.co = v.co * 0.5 + mid * 0.5
                
    # Offset along normal off the skin
    for v in bm.verts:
        v.co += v.normal * offset_dist
        
    mesh = bpy.data.meshes.new(name + "Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    # Apply Solidify Modifier to make it REAL PHYSICAL CLOTH WITH THICKNESS!
    sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    sol.thickness = thickness
    sol.offset = 1.0 # Outward from skin
    sol.use_rim = True
    sol.use_quality_normals = True
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Solidify")
    
    # Subtle Bevel modifier on the rim for realistic rolled elastic hem
    bev = obj.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = 0.0008
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(40)
    bpy.ops.object.modifier_apply(modifier="Bevel")
    
    for p in obj.data.polygons:
        p.use_smooth = True
        
    return obj

# Condition 1: Sexy Cheeky Bikini (Classic)
def is_classic_bikini(v):
    x, y, z = v.co.x, v.co.y, v.co.z
    angle = math.atan2(x, -y) # 0 = rear cleft, pi = front belly
    s = math.sin(angle)
    c = math.cos(angle)
    
    # Waistline: graceful curve sitting on hips, V-dip in front & back
    z_waist = 0.920 + 0.030 * (s * s) - 0.010 * c
    if z > z_waist:
        return False
        
    if abs(x) > 0.21:
        return False
        
    # Rear leg opening (Cheeky cut: curves up across the cheek)
    if y <= 0.0:
        norm_x = min(1.0, abs(x) / 0.175)
        # Sweeps from crotch 0.725 up to hip 0.900
        z_leg = 0.725 + 0.175 * (norm_x ** 1.35)
        if z < z_leg:
            return False
    else:
        # Front leg opening
        norm_x = min(1.0, abs(x) / 0.165)
        z_leg = 0.722 + 0.178 * (norm_x ** 1.25)
        if z < z_leg:
            return False
            
    return True

# Condition 2: Seductive String Thong
def is_thong(v):
    x, y, z = v.co.x, v.co.y, v.co.z
    angle = math.atan2(x, -y)
    s = math.sin(angle)
    c = math.cos(angle)
    
    # High-rise waistline
    z_waist = 0.925 + 0.028 * (s * s)
    if z > z_waist:
        return False
        
    if abs(x) > 0.205:
        return False
        
    # Hip string band (thin horizontal band at the hips)
    if abs(x) > 0.14:
        # Hip strap: width of about 1.8cm
        return z >= (z_waist - 0.022)
        
    if y <= 0.0: # Rear side
        # Back sacrum triangle: from waist down to ~0.87
        if z >= 0.865:
            # Triangle width tapers down from hip strap to center
            t_tri = (z - 0.865) / (z_waist - 0.865)
            max_w = 0.008 + 0.13 * (t_tri ** 1.4)
            return abs(x) <= max_w
        else:
            # Cleft string: narrow, centered ribbon (8-10mm wide)
            return z >= 0.718 and abs(x) <= 0.0085
    else: # Front side
        # Front V-panel
        t_front = max(0.0, min(1.0, (z - 0.720) / (z_waist - 0.720)))
        max_w = 0.022 + 0.12 * (t_front ** 1.3)
        return z >= 0.720 and abs(x) <= max_w

panty_classic = build_panty_from_condition("Panty_Classic", is_classic_bikini, offset_dist=0.0022, thickness=0.0022)
print("Built Panty_Classic:", len(panty_classic.data.vertices), "verts")

panty_thong = build_panty_from_condition("Panty_Thong", is_thong, offset_dist=0.0022, thickness=0.0025)
print("Built Panty_Thong:", len(panty_thong.data.vertices), "verts")

# Render Previews
cam_data = bpy.data.cameras.new('Cam')
cam_obj = bpy.data.objects.new('Cam', cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = (0, -1.35, 0.82)
cam_obj.rotation_euler = (math.radians(90), 0, 0)

light1 = bpy.data.objects.new('L1', bpy.data.lights.new('L1', 'SUN'))
light1.data.energy = 2.2
light1.rotation_euler = (math.radians(25), math.radians(20), 0)
bpy.context.scene.collection.objects.link(light1)

light2 = bpy.data.objects.new('L2', bpy.data.lights.new('L2', 'SUN'))
light2.data.energy = 1.2
light2.rotation_euler = (math.radians(15), math.radians(-40), 0)
bpy.context.scene.collection.objects.link(light2)

# Set realistic materials
mat_skin = bpy.data.materials.new('Skin')
mat_skin.use_nodes = True
mat_skin.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.92, 0.75, 0.68, 1.0)
body.data.materials.clear()
body.data.materials.append(mat_skin)

mat_classic = bpy.data.materials.new('ClassicMat')
mat_classic.use_nodes = True
mat_classic.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.95, 0.40, 0.60, 1.0) # Vibrant rose pink
mat_classic.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.35
panty_classic.data.materials.clear()
panty_classic.data.materials.append(mat_classic)

mat_thong_mat = bpy.data.materials.new('ThongMat')
mat_thong_mat.use_nodes = True
mat_thong_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.10, 0.08, 0.12, 1.0) # Sleek satin black
mat_thong_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.25
panty_thong.data.materials.clear()
panty_thong.data.materials.append(mat_thong_mat)

bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512

# 1. Render Classic Bikini Rear
panty_thong.hide_render = True
panty_classic.hide_render = False
bpy.context.scene.render.filepath = 'C:/Users/kiosk/.gemini/antigravity-cli/brain/c69cd41b-33a7-42a9-9d33-a8d52789ab72/test_real_classic_rear.png'
bpy.ops.render.render(write_still=True)
print("Rendered test_real_classic_rear.png!")

# 2. Render Classic Bikini 3/4 Perspective
cam_obj.location = (0.75, -1.15, 0.88)
cam_obj.rotation_euler = (math.radians(85), 0, math.radians(33))
bpy.context.scene.render.filepath = 'C:/Users/kiosk/.gemini/antigravity-cli/brain/c69cd41b-33a7-42a9-9d33-a8d52789ab72/test_real_classic_3q.png'
bpy.ops.render.render(write_still=True)
print("Rendered test_real_classic_3q.png!")

# 3. Render Thong Rear
cam_obj.location = (0, -1.35, 0.82)
cam_obj.rotation_euler = (math.radians(90), 0, 0)
panty_classic.hide_render = True
panty_thong.hide_render = False
bpy.context.scene.render.filepath = 'C:/Users/kiosk/.gemini/antigravity-cli/brain/c69cd41b-33a7-42a9-9d33-a8d52789ab72/test_real_thong_rear.png'
bpy.ops.render.render(write_still=True)
print("Rendered test_real_thong_rear.png!")

# 4. Render Thong 3/4 Perspective
cam_obj.location = (0.75, -1.15, 0.88)
cam_obj.rotation_euler = (math.radians(85), 0, math.radians(33))
bpy.context.scene.render.filepath = 'C:/Users/kiosk/.gemini/antigravity-cli/brain/c69cd41b-33a7-42a9-9d33-a8d52789ab72/test_real_thong_3q.png'
bpy.ops.render.render(write_still=True)
print("Rendered test_real_thong_3q.png!")

