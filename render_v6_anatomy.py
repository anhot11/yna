import bpy
import math
import os

print("=== RENDERING V6 HYPER-REALISTIC CHARACTER VERIFICATION ===")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r"I:\workzone\gotot\yna\SlapSimulator\assets\models\character.glb")

# Find body and panties
body = bpy.data.objects.get("Body")
panty_c = bpy.data.objects.get("Panty_Classic")
panty_t = bpy.data.objects.get("Panty_Thong")

if not body:
    print("ERROR: Body not found!")
    quit()

print(f"Body vertices: {len(body.data.vertices)}")
if panty_c: print(f"Panty_Classic vertices: {len(panty_c.data.vertices)}")
if panty_t: print(f"Panty_Thong vertices: {len(panty_t.data.vertices)}")

# Hide panties to see body anatomy
if panty_c: panty_c.hide_render = True; panty_c.hide_viewport = True
if panty_t: panty_t.hide_render = True; panty_t.hide_viewport = True

# Create realistic skin material
mat = bpy.data.materials.new(name="RealisticSkin")
mat.use_nodes = True
tree = mat.node_tree
nodes = tree.nodes
links = tree.links
nodes.clear()

# Principled BSDF
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (0, 0)
bsdf.inputs["Base Color"].default_value = (0.92, 0.72, 0.62, 1.0)
bsdf.inputs["Roughness"].default_value = 0.38
bsdf.inputs["Subsurface Weight"].default_value = 0.15
bsdf.inputs["Subsurface Radius"].default_value = (0.8, 0.3, 0.15)

output = nodes.new("ShaderNodeOutputMaterial")
output.location = (300, 0)
links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

# Vertex color node for anatomical variation
vcol = nodes.new("ShaderNodeVertexColor")
vcol.location = (-400, 0)
vcol.layer_name = "Color"

# Mix RGB node
mix = nodes.new("ShaderNodeMixRGB")
mix.location = (-200, 0)
mix.blend_type = 'MULTIPLY'
mix.inputs["Fac"].default_value = 0.6

# Base color
base_col = nodes.new("ShaderNodeRGB")
base_col.location = (-400, 200)
base_col.outputs[0].default_value = (0.92, 0.72, 0.62, 1.0)

links.new(base_col.outputs[0], mix.inputs["Color1"])
links.new(vcol.outputs["Color"], mix.inputs["Color2"])
links.new(mix.outputs[0], bsdf.inputs["Base Color"])

body.data.materials.clear()
body.data.materials.append(mat)

# Scene setup
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 800
scene.render.resolution_y = 1000
scene.render.film_transparent = True

# Camera setup function
def setup_camera(pos, look_at, name="Camera"):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = 55
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location = pos
    
    from mathutils import Vector
    direction = Vector((look_at[0] - pos[0], look_at[1] - pos[1], look_at[2] - pos[2]))
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    return cam_obj

# Lighting
def add_light(name, pos, energy, color=(1,1,1)):
    light_data = bpy.data.lights.new(name, type='AREA')
    light_data.energy = energy
    light_data.color = color
    light_data.size = 1.5
    light_obj = bpy.data.objects.new(name, light_data)
    bpy.context.scene.collection.objects.link(light_obj)
    light_obj.location = pos
    return light_obj

# Three-point lighting
key = add_light("Key", (0.8, -1.5, 1.3), 120, (1.0, 0.95, 0.90))
fill = add_light("Fill", (-0.6, -1.2, 0.9), 45, (0.85, 0.90, 1.0))
rim = add_light("Rim", (0.0, 0.8, 1.4), 80, (1.0, 0.92, 0.85))
bottom = add_light("Bottom", (0.0, -0.8, 0.4), 30, (0.95, 0.85, 0.80))

out_dir = r"C:\Users\kiosk\.gemini\antigravity-cli\brain\c69cd41b-33a7-42a9-9d33-a8d52789ab72"

# Render 1: Rear view (buttocks)
cam1 = setup_camera((0, -1.3, 0.82), (0, 0, 0.82))
scene.camera = cam1
scene.render.filepath = os.path.join(out_dir, "v6_rear_anatomy")
bpy.ops.render.render(write_still=True)
print("Rendered: v6_rear_anatomy.png")

# Render 2: Bottom-up anatomical view (seeing underneath)
cam2 = setup_camera((0, -0.6, 0.35), (0, 0, 0.75))
scene.camera = cam2
scene.render.filepath = os.path.join(out_dir, "v6_bottom_anatomy")
bpy.ops.render.render(write_still=True)
print("Rendered: v6_bottom_anatomy.png")

# Render 3: 3/4 rear view
cam3 = setup_camera((0.7, -1.1, 0.85), (0, 0, 0.82))
scene.camera = cam3
scene.render.filepath = os.path.join(out_dir, "v6_3q_anatomy")
bpy.ops.render.render(write_still=True)
print("Rendered: v6_3q_anatomy.png")

# Render 4: Close-up gluteal cleft
cam4 = setup_camera((0, -0.8, 0.82), (0, 0, 0.82))
cam4.data.lens = 85  # Tighter crop
scene.camera = cam4
scene.render.filepath = os.path.join(out_dir, "v6_cleft_closeup")
bpy.ops.render.render(write_still=True)
print("Rendered: v6_cleft_closeup.png")

print("=== ALL V6 VERIFICATION RENDERS COMPLETE ===")
