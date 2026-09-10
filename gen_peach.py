with open(r"I:\workzone\gotot\yna\test_lattice_v2.py", "r", encoding="utf-8") as f:
    code = f.read()

# Make the cheeks even fuller and rounder in upper-mid
code = code.replace("pt.co_deform.y -= 1.10 * w_weight * (1.0 - y_frac * 0.4)", "pt.co_deform.y -= 1.35 * w_weight * (1.0 - y_frac * 0.35)")
code = code.replace("pt.co_deform.x += sign_u * 0.38 * w_weight", "pt.co_deform.x += sign_u * 0.45 * w_weight")
code = code.replace("pt.co_deform.y -= 0.45 * h_weight", "pt.co_deform.y -= 0.60 * h_weight")
code = code.replace("pt.co_deform.x += sign_u * 0.18 * h_weight", "pt.co_deform.x += sign_u * 0.22 * h_weight")

# Godot camera FOV 42 deg, distance 1.35m
code = code.replace("cam_obj.location = (0, -1.45, 0.81)", "cam_data.lens_unit = 'FOV'; cam_data.angle = math.radians(42); cam_obj.location = (0, -1.35, 0.82)")
code = code.replace("preview_lattice2_rear.png", "preview_peach_rear.png")
code = code.replace("preview_lattice2_3q.png", "preview_peach_3q.png")

with open(r"I:\workzone\gotot\yna\test_peach.py", "w", encoding="utf-8") as f:
    f.write(code)
