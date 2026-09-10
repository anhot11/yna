import bpy
import numpy as np
import math
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

def save_image_rgba(name, w, h, rgba_array, path):
    img = bpy.data.images.new(name, width=w, height=h, alpha=True)
    # foreach_set expects float values [0.0, 1.0] in bottom-to-top order
    flat_pixels = rgba_array.reshape(-1)
    img.pixels.foreach_set(flat_pixels.tolist())
    img.filepath_raw = path
    img.file_format = 'PNG'
    img.save()
    print("Saved:", path)
    bpy.data.images.remove(img)

# -------------------------------------------------------------
# 1. Studio Panorama Sky (1024 x 512)
# -------------------------------------------------------------
w, h = 1024, 512
# Equirectangular coordinates:
# y goes from 0 (bottom: latitude -pi/2) to h-1 (top: latitude +pi/2)
y_idx, x_idx = np.mgrid[0:h, 0:w]
phi = (x_idx / w - 0.5) * 2.0 * np.pi # [-pi, pi]
theta = (y_idx / h - 0.5) * np.pi     # [-pi/2, pi/2]

dir_x = np.cos(theta) * np.sin(phi)
dir_y = np.sin(theta)
dir_z = np.cos(theta) * np.cos(phi)

# Base dark luxury studio gradient
bg_r = 0.08 + 0.05 * np.clip(dir_y + 0.4, 0.0, 1.0)
bg_g = 0.07 + 0.04 * np.clip(dir_y + 0.4, 0.0, 1.0)
bg_b = 0.10 + 0.07 * np.clip(dir_y + 0.4, 0.0, 1.0)

sky_r = bg_r.copy()
sky_g = bg_g.copy()
sky_b = bg_b.copy()

def add_softbox(azimuth_deg, elevation_deg, size_deg, col, intensity):
    global sky_r, sky_g, sky_b
    az_rad = math.radians(azimuth_deg)
    el_rad = math.radians(elevation_deg)
    sb_dx = math.cos(el_rad) * math.sin(az_rad)
    sb_dy = math.sin(el_rad)
    sb_dz = math.cos(el_rad) * math.cos(az_rad)
    
    dot = np.clip(dir_x * sb_dx + dir_y * sb_dy + dir_z * sb_dz, -1.0, 1.0)
    angle = np.arccos(dot)
    sigma = math.radians(size_deg) * 0.45
    g = np.exp(- (angle ** 2) / (2.0 * (sigma ** 2)))
    
    sky_r += g * col[0] * intensity
    sky_g += g * col[1] * intensity
    sky_b += g * col[2] * intensity

# Softbox 1: Main Warm Key Softbox (top right rear)
add_softbox(35, 25, 42, (1.0, 0.95, 0.88), 1.5)

# Softbox 2: Cool Rim Strip Box (left rear rim)
add_softbox(-140, 15, 36, (0.85, 0.92, 1.15), 1.2)

# Softbox 3: Top Overhead Diffuser
add_softbox(0, 60, 48, (0.95, 0.92, 0.98), 0.7)

# Softbox 4: Soft Fill
add_softbox(-45, -10, 45, (0.90, 0.85, 0.90), 0.4)

sky_rgba = np.zeros((h, w, 4), dtype=np.float32)
sky_rgba[:, :, 0] = np.clip(sky_r, 0.0, 1.0)
sky_rgba[:, :, 1] = np.clip(sky_g, 0.0, 1.0)
sky_rgba[:, :, 2] = np.clip(sky_b, 0.0, 1.0)
sky_rgba[:, :, 3] = 1.0

out_sky = r"I:\workzone\gotot\yna\SlapSimulator\assets\textures\studio_sky.png"
save_image_rgba("StudioSky", w, h, sky_rgba, out_sky)

# -------------------------------------------------------------
# 2. Micro-Skin Normal Map (512 x 512)
# -------------------------------------------------------------
nw, nh = 512, 512
np.random.seed(42)

# Multi-frequency noise for skin pores
grid_y, grid_x = np.mgrid[0:nh, 0:nw]
f1 = np.sin(grid_x * 0.45) * np.cos(grid_y * 0.45)
f2 = np.sin(grid_x * 0.85 + 1.2) * np.sin(grid_y * 0.95 + 0.7)
f3 = np.cos(grid_x * 1.7 - 0.4) * np.cos(grid_y * 1.6 + 1.1)
noise = np.random.normal(0.0, 0.15, (nh, nw))

# Dermal pore pattern
skin_height = (f1 * 0.25 + f2 * 0.35 + f3 * 0.25 + noise * 0.15)
pores = np.clip((skin_height - 0.2) * 2.5, 0.0, 1.0) ** 2.0
bump = skin_height * 0.6 - pores * 0.4

# Gradients
sobel_x = np.roll(bump, -1, axis=1) - np.roll(bump, 1, axis=1)
sobel_y = np.roll(bump, -1, axis=0) - np.roll(bump, 1, axis=0)

strength = 1.6
nx = -sobel_x * strength
ny = -sobel_y * strength
nz = np.ones_like(nx)
len_n = np.sqrt(nx**2 + ny**2 + nz**2)
nx /= len_n
ny /= len_n
nz /= len_n

norm_rgba = np.zeros((nh, nw, 4), dtype=np.float32)
norm_rgba[:, :, 0] = nx * 0.5 + 0.5
norm_rgba[:, :, 1] = ny * 0.5 + 0.5
norm_rgba[:, :, 2] = nz * 0.5 + 0.5
norm_rgba[:, :, 3] = 1.0

out_norm = r"I:\workzone\gotot\yna\SlapSimulator\assets\textures\skin_normal.png"
save_image_rgba("SkinNormal", nw, nh, norm_rgba, out_norm)

print("All realistic lighting assets generated successfully!")
