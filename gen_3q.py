with open(r"I:\workzone\gotot\yna\test_anatomy_v2.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("cam_obj.location = (0, -1.45, 0.81)", "cam_obj.location = (0.85, -1.25, 0.85)")
code = code.replace("cam_obj.rotation_euler = (math.radians(89), 0, 0)", "cam_obj.rotation_euler = (math.radians(85), 0, math.radians(35))")
code = code.replace("preview_voluptuous_v2.png", "preview_voluptuous_3quarter.png")

with open(r"I:\workzone\gotot\yna\test_anatomy_3q.py", "w", encoding="utf-8") as f:
    f.write(code)
