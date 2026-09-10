with open(r"I:\workzone\gotot\yna\build_photorealistic_character.py", "r", encoding="utf-8") as f:
    code = f.read()

# Remove the bpy.ops.object.vertex_group_smooth call
old_chunk = """    # Apply Vertex Group Smooth to ensure 100% harmonious Laplacian weight field
    bpy.context.view_layer.objects.active = obj
    for name in ["Cheek_L", "Cheek_R", "Pelvis", "Thigh_L", "Thigh_R", "Spine"]:
        vg = obj.vertex_groups.get(name)
        if vg:
            obj.vertex_groups.active_index = vg.index
            bpy.ops.object.vertex_group_smooth(factor=0.6, repeat=3)"""

new_chunk = """    # Gaussian weights are mathematically C-infinity continuous and normalized"""

code = code.replace(old_chunk, new_chunk)

with open(r"I:\workzone\gotot\yna\build_photorealistic_character.py", "w", encoding="utf-8") as f:
    f.write(code)

