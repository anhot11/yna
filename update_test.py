import os

test_dir = r"I:\workzone\gotot\yna\test_android"
project_godot_path = os.path.join(test_dir, "project.godot")

with open(project_godot_path, "a", encoding="utf-8") as f:
    f.write("\n[rendering]\n\ntextures/vram_compression/import_etc2_astc=true\n")

print("Updated project.godot with ETC2/ASTC setting.")
