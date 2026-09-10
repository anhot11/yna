import bpy
import numpy as np
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

proj_dir = r"I:\workzone\gotot\yna\SlapSimulator"
tex_dir = os.path.join(proj_dir, "assets", "textures")
os.makedirs(tex_dir, exist_ok=True)

def save_image(name, w, h, rgba_array, path):
    img = bpy.data.images.new(name, width=w, height=h, alpha=True)
    flipped = np.flipud(rgba_array)
    flat_pixels = flipped.reshape(-1)
    img.pixels.foreach_set(flat_pixels.tolist())
    img.filepath_raw = path
    img.file_format = 'PNG'
    img.save()
    print("Saved:", path)
    bpy.data.images.remove(img)

w, h = 512, 512
y_grid, x_grid = np.mgrid[0:h, 0:w]
cx = (x_grid - w/2) / (w/2)
cy = (y_grid - h/2) / (h/2)

# -------------------------------------------------------------
# 1. APP ICON (512 x 512)
# -------------------------------------------------------------
icon_rgba = np.zeros((h, w, 4), dtype=np.float32)
squircle = (cx**4 + cy**4) <= (0.82**4)
grad_t = (cx + cy + 1.4) / 2.8
bg_r = 0.95 * grad_t + 0.55 * (1.0 - grad_t)
bg_g = 0.15 * grad_t + 0.10 * (1.0 - grad_t)
bg_b = 0.50 * grad_t + 0.85 * (1.0 - grad_t)

icon_rgba[squircle, 0] = bg_r[squircle]
icon_rgba[squircle, 1] = bg_g[squircle]
icon_rgba[squircle, 2] = bg_b[squircle]
icon_rgba[squircle, 3] = 1.0

# Gloss
gloss = squircle & (cy < -0.05) & (cy > -0.75) & (np.abs(cx) < 0.70)
icon_rgba[gloss, 0] = np.minimum(1.0, icon_rgba[gloss, 0] + 0.20)
icon_rgba[gloss, 1] = np.minimum(1.0, icon_rgba[gloss, 1] + 0.20)
icon_rgba[gloss, 2] = np.minimum(1.0, icon_rgba[gloss, 2] + 0.20)

# Peach / Butt motif
hx = cx * 1.5
hy = -cy * 1.5 - 0.15
heart_eq = (hx**2 + hy**2 - 0.4)**3 - (hx**2) * (hy**3)
heart_mask = heart_eq <= 0.0

icon_rgba[heart_mask, 0] = 1.0
icon_rgba[heart_mask, 1] = 0.65
icon_rgba[heart_mask, 2] = 0.75
icon_rgba[heart_mask, 3] = 1.0

hand_dist = np.sqrt((cx - 0.15)**2 + (cy - 0.05)**2)
hand_mark = hand_dist < 0.18
icon_rgba[heart_mask & hand_mark, 0] = 1.0
icon_rgba[heart_mask & hand_mark, 1] = 0.9
icon_rgba[heart_mask & hand_mark, 2] = 0.3

save_image("icon", w, h, icon_rgba, os.path.join(proj_dir, "icon.png"))

# -------------------------------------------------------------
# 2. PANTY 1: CLASSIC CUTE LACE / STRIPES (512 x 512)
# -------------------------------------------------------------
p1_rgba = np.zeros((h, w, 4), dtype=np.float32)
p1_rgba[:, :, 0] = 0.98
p1_rgba[:, :, 1] = 0.62
p1_rgba[:, :, 2] = 0.78
p1_rgba[:, :, 3] = 1.0

stripe_pattern = ((x_grid + y_grid) // 24) % 2 == 0
p1_rgba[stripe_pattern, 0] = 1.0
p1_rgba[stripe_pattern, 1] = 0.88
p1_rgba[stripe_pattern, 2] = 0.94

border_mask = (y_grid < 40) | (y_grid > h - 40)
p1_rgba[border_mask, 0] = 1.0
p1_rgba[border_mask, 1] = 0.95
p1_rgba[border_mask, 2] = 0.98

save_image("panty_classic", w, h, p1_rgba, os.path.join(tex_dir, "panty_classic.png"))

# -------------------------------------------------------------
# 3. PANTY 2: SPICY BLACK LACE / GOLD TRIM (512 x 512)
# -------------------------------------------------------------
p2_rgba = np.zeros((h, w, 4), dtype=np.float32)
p2_rgba[:, :, 0] = 0.10
p2_rgba[:, :, 1] = 0.04
p2_rgba[:, :, 2] = 0.06
p2_rgba[:, :, 3] = 1.0

lace_pattern = (np.sin(x_grid * 0.15) * np.sin(y_grid * 0.15) + np.sin((x_grid+y_grid)*0.2)) > 0.4
p2_rgba[lace_pattern, 0] = 0.22
p2_rgba[lace_pattern, 1] = 0.08
p2_rgba[lace_pattern, 2] = 0.12

gold_border = (y_grid < 30) | (y_grid > h - 30)
p2_rgba[gold_border, 0] = 0.95
p2_rgba[gold_border, 1] = 0.78
p2_rgba[gold_border, 2] = 0.28

save_image("panty_thong", w, h, p2_rgba, os.path.join(tex_dir, "panty_thong.png"))

# -------------------------------------------------------------
# 4. SLAP MARK (256 x 256)
# -------------------------------------------------------------
w_sm, h_sm = 256, 256
y_sm, x_sm = np.mgrid[0:h_sm, 0:w_sm]
cx_sm = (x_sm - w_sm/2) / (w_sm/2)
cy_sm = (y_sm - h_sm/2) / (h_sm/2)

slap_rgba = np.zeros((h_sm, w_sm, 4), dtype=np.float32)
palm_dist = np.sqrt(cx_sm**2 + (cy_sm + 0.15)**2)
palm_mask = np.clip(1.0 - (palm_dist / 0.45), 0.0, 1.0) ** 1.5

finger_mask = np.zeros((h_sm, w_sm), dtype=np.float32)
for f_idx, fx_offset in enumerate([-0.26, -0.09, 0.09, 0.26]):
    f_len = 0.38 if abs(fx_offset) < 0.2 else 0.32
    f_dist_x = abs(cx_sm - fx_offset) / 0.075
    f_dist_y = np.clip((cy_sm - 0.20) / f_len, 0.0, 1.0)
    f_dist = np.sqrt(f_dist_x**2 + ((cy_sm - 0.20) / f_len)**2)
    finger_mask = np.maximum(finger_mask, np.clip(1.0 - f_dist, 0.0, 1.0))

thumb_dist = np.sqrt(((cx_sm + 0.35) / 0.12)**2 + ((cy_sm + 0.05) / 0.22)**2)
thumb_mask = np.clip(1.0 - thumb_dist, 0.0, 1.0)
total_hand = np.maximum(palm_mask, np.maximum(finger_mask, thumb_mask))

glow = np.clip(1.0 - np.sqrt(cx_sm**2 + cy_sm**2) / 0.85, 0.0, 1.0) ** 2
combined_alpha = np.clip(total_hand * 0.8 + glow * 0.35, 0.0, 1.0)

slap_rgba[:, :, 0] = 0.95
slap_rgba[:, :, 1] = 0.15
slap_rgba[:, :, 2] = 0.25
slap_rgba[:, :, 3] = combined_alpha

save_image("slap_mark", w_sm, h_sm, slap_rgba, os.path.join(tex_dir, "slap_mark.png"))

# -------------------------------------------------------------
# 5. SPARK / STAR PARTICLE (128 x 128)
# -------------------------------------------------------------
w_st, h_st = 128, 128
y_st, x_st = np.mgrid[0:h_st, 0:w_st]
cx_st = (x_st - w_st/2) / (w_st/2)
cy_st = (y_st - h_st/2) / (h_st/2)

star_rgba = np.zeros((h_st, w_st, 4), dtype=np.float32)
alpha_star = np.clip(1.0 - (np.abs(cx_st)**0.5 + np.abs(cy_st)**0.5) / 1.1, 0.0, 1.0)
star_rgba[:, :, 0] = 1.0
star_rgba[:, :, 1] = 0.92
star_rgba[:, :, 2] = 0.40
star_rgba[:, :, 3] = alpha_star

save_image("star", w_st, h_st, star_rgba, os.path.join(tex_dir, "star.png"))

# -------------------------------------------------------------
# 6. HEART PARTICLE (128 x 128)
# -------------------------------------------------------------
heart_rgba = np.zeros((h_st, w_st, 4), dtype=np.float32)
hx_p = cx_st * 1.5
hy_p = -cy_st * 1.5 - 0.15
heart_func = (hx_p**2 + hy_p**2 - 0.4)**3 - (hx_p**2) * (hy_p**3)
h_alpha = np.clip((0.05 - heart_func) * 15.0, 0.0, 1.0)

heart_rgba[:, :, 0] = 1.0
heart_rgba[:, :, 1] = 0.35
heart_rgba[:, :, 2] = 0.60
heart_rgba[:, :, 3] = h_alpha

save_image("heart", w_st, h_st, heart_rgba, os.path.join(tex_dir, "heart.png"))
print("All texture assets generated successfully!")
