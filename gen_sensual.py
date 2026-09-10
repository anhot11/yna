with open(r"I:\workzone\gotot\yna\test_perfect_peach.py", "r", encoding="utf-8") as f:
    code = f.read()

leg_rotation_code = """
# Rotate legs inward at hip joints to achieve natural feminine standing stance
hip_l_x = -0.105; hip_r_x = 0.105; hip_z = 0.730
leg_angle = 0.065 # radians (~3.7 degrees)

for v in body.data.vertices:
    if v.co.z < 0.730:
        t = min(1.0, max(0.0, (0.730 - v.co.z) / 0.06))
        ang = leg_angle * t
        ca = math.cos(ang); sa = math.sin(ang)
        
        if v.co.x < 0:
            rel_x = v.co.x - hip_l_x
            rel_z = v.co.z - hip_z
            v.co.x = hip_l_x + (rel_x * ca + rel_z * sa)
            v.co.z = hip_z + (-rel_x * sa + rel_z * ca)
        else:
            rel_x = v.co.x - hip_r_x
            rel_z = v.co.z - hip_z
            v.co.x = hip_r_x + (rel_x * ca - rel_z * sa)
            v.co.z = hip_z + (rel_x * sa + rel_z * ca)

body.data.update()
"""

code = code.replace("# -------------------------------------------------------------\n# CREATE TRUE PEACH", leg_rotation_code + "\n# -------------------------------------------------------------\n# CREATE TRUE PEACH")
code = code.replace("preview_true_peach_rear.png", "preview_sensual_rear.png")
code = code.replace("preview_true_peach_3q.png", "preview_sensual_3q.png")

with open(r"I:\workzone\gotot\yna\test_sensual_stance.py", "w", encoding="utf-8") as f:
    f.write(code)
