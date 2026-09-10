import os

settings_path = r'I:\workzone\gotot\yna\Godot_v4.7.2-stable_win64.exe\editor_data\editor_settings-4.7.tres'

lines_to_add = [
    'export/android/android_sdk_path = "I:/Apps/AndroidSDK"\n',
    'export/android/java_sdk_path = "I:/Apps/jdk-17"\n',
    'export/android/debug_keystore = "I:/workzone/gotot/yna/debug.keystore"\n',
    'export/android/debug_keystore_user = "androiddebugkey"\n',
    'export/android/debug_keystore_pass = "android"\n'
]

if os.path.exists(settings_path):
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(settings_path, 'a', encoding='utf-8') as f:
        for line in lines_to_add:
            key = line.split('=')[0].strip()
            if key not in content:
                f.write(line)

    print("Editor settings updated successfully.")
else:
    print("File not found:", settings_path)
