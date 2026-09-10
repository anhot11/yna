with open(r"I:\workzone\gotot\yna\build_photorealistic_character.py", "r", encoding="utf-8") as f:
    code = f.read()

# Make Panty_Classic hidden, Panty_Thong visible
code = code.replace("bpy.context.scene.render.filepath = preview_final", 
"""# Render 1: Thong
if "Panty_Classic" in bpy.data.objects:
    bpy.data.objects["Panty_Classic"].hide_render = True
if "Panty_Thong" in bpy.data.objects:
    bpy.data.objects["Panty_Thong"].hide_render = False

bpy.context.scene.render.filepath = r"C:\\Users\\kiosk\\.gemini\\antigravity-cli\\brain\\c69cd41b-33a7-42a9-9d33-a8d52789ab72\\preview_thong.png"
bpy.ops.render.render(write_still=True)

# Render 2: Natural Bare Sculpt (No panties)
if "Panty_Thong" in bpy.data.objects:
    bpy.data.objects["Panty_Thong"].hide_render = True

bpy.context.scene.render.filepath = r"C:\\Users\\kiosk\\.gemini\\antigravity-cli\\brain\\c69cd41b-33a7-42a9-9d33-a8d52789ab72\\preview_bare.png"
bpy.ops.render.render(write_still=True)
print("Rendered thong and bare previews!")
""")

with open(r"I:\workzone\gotot\yna\render_thong_and_bare.py", "w", encoding="utf-8") as f:
    f.write(code)
