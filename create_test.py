import os, subprocess

test_dir = r"I:\workzone\gotot\yna\test_android"
os.makedirs(test_dir, exist_ok=True)

project_godot = """config_version=5

[application]

config/name="TestAndroid"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.7")

[display]

window/size/viewport_width=720
window/size/viewport_height=1280
window/handheld/orientation=1
"""

with open(os.path.join(test_dir, "project.godot"), "w", encoding="utf-8") as f:
    f.write(project_godot)

main_tscn = """[gd_scene format=3 uid="uid://test12345"]

[node name="Main" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2

[node name="Label" type="Label"]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -100.0
offset_top = -20.0
offset_right = 100.0
offset_bottom = 20.0
grow_horizontal = 2
grow_vertical = 2
text = "Test OK!"
horizontal_alignment = 1
"""

with open(os.path.join(test_dir, "main.tscn"), "w", encoding="utf-8") as f:
    f.write(main_tscn)

export_presets = """[preset.0]

name="Android"
platform="Android"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="I:/workzone/gotot/yna/test_android/test.apk"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.0.options]

custom_template/debug=""
custom_template/release=""
gradle_build/use_gradle_build=false
architectures/arm64-v8a=true
architectures/armeabi-v7a=false
architectures/x86_64=false
architectures/x86=false
package/unique_name="com.antigravity.test"
package/name="Test"
package/signed=true
version/code=1
version/name="1.0"
package/install_location=0
"""

with open(os.path.join(test_dir, "export_presets.cfg"), "w", encoding="utf-8") as f:
    f.write(export_presets)

print("Test project created.")
