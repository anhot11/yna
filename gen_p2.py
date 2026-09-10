with open(r"I:\workzone\gotot\yna\test_perfect_peach.py", "r", encoding="utf-8") as f:
    code = f.read()

# Soften cleft line by bringing cleft forward with the cheeks
code = code.replace("pt.co_deform.y -= 0.55 * w_weight * (1.0 - y_frac * 0.4)", "pt.co_deform.y -= 0.95 * w_weight * (1.0 - y_frac * 0.35)")

# Bring thighs naturally closer together in stance (eliminate unnatural gap)
thigh_chunk = """                # 2. Harmonious Thigh Base (w = 1, 2)
                if (w == 1 or w == 2):
                    h_weight = math.sin((w - 0.2) / 2.8 * math.pi)
                    if u == 1 or u == 3:
                        # Fuller hamstrings for smooth transition
                        pt.co_deform.y -= 0.40 * h_weight
                        # Keep thighs under hips
                        sign_u = -1.0 if u == 1 else 1.0
                        pt.co_deform.x += sign_u * 0.05 * h_weight"""

new_thigh_chunk = """                # 2. Harmonious Thigh Base (w = 0, 1, 2)
                if w <= 2:
                    sign_u = -1.0 if u == 1 else 1.0
                    if u == 1 or u == 3:
                        # Bring thighs closer together naturally
                        pt.co_deform.x -= sign_u * 0.22 * (1.0 - w * 0.3)
                        # Fuller hamstrings
                        pt.co_deform.y -= 0.45 * math.cos(w / 3.0 * math.pi * 0.5)
                    elif u == 0 or u == 4:
                        sign_u0 = -1.0 if u == 0 else 1.0
                        pt.co_deform.x -= sign_u0 * 0.12"""

code = code.replace(thigh_chunk, new_thigh_chunk)
code = code.replace("preview_true_peach_rear.png", "preview_peach_perfect_rear.png")
code = code.replace("preview_true_peach_3q.png", "preview_peach_perfect_3q.png")

with open(r"I:\workzone\gotot\yna\test_perfect_peach_v2.py", "w", encoding="utf-8") as f:
    f.write(code)
