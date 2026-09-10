extends Node3D
class_name CharacterController

var skeleton: Skeleton3D
var body_mesh: MeshInstance3D
var panty_classic: MeshInstance3D
var panty_thong: MeshInstance3D

var skin_shader: Shader = preload("res://shaders/skin_slap.gdshader")
var panty_shader: Shader = preload("res://shaders/panty.gdshader")
var tex_panty_classic: Texture2D = preload("res://assets/textures/panty_classic.png")
var tex_panty_thong: Texture2D = preload("res://assets/textures/panty_thong.png")
var tex_skin_normal: Texture2D = preload("res://assets/textures/skin_normal.png")

var skin_mat: ShaderMaterial
var panty_classic_mat: ShaderMaterial
var panty_thong_mat: ShaderMaterial

# Bone indices
var bone_cheek_l: int = -1
var bone_cheek_r: int = -1
var rest_pos_l: Vector3 = Vector3.ZERO
var rest_pos_r: Vector3 = Vector3.ZERO
var rest_rot_l: Quaternion = Quaternion.IDENTITY
var rest_rot_r: Quaternion = Quaternion.IDENTITY

# Soft-Tissue State for Left Cheek (World coordinates: X=left/right, Y=up/down, Z=rearward)
var pos_l: Vector3 = Vector3.ZERO
var vel_l: Vector3 = Vector3.ZERO
var squash_l: float = 0.0
var squash_vel_l: float = 0.0
var rot_l: Vector3 = Vector3.ZERO
var rot_vel_l: Vector3 = Vector3.ZERO
var ripple_amp_l: float = 0.0

# Soft-Tissue State for Right Cheek
var pos_r: Vector3 = Vector3.ZERO
var vel_r: Vector3 = Vector3.ZERO
var squash_r: float = 0.0
var squash_vel_r: float = 0.0
var rot_r: Vector3 = Vector3.ZERO
var rot_vel_r: Vector3 = Vector3.ZERO
var ripple_amp_r: float = 0.0

# Physical simulation parameters
var omega_bounce: float = 14.5      # Natural frequency of primary bounce (~2.3 Hz)
var zeta_bounce: float = 0.22       # Damping ratio (0.22 gives 5-6 lush, juicy oscillations)
var omega_squash: float = 19.0      # Natural frequency of squash & stretch
var zeta_squash: float = 0.26       # Damping of squash
var omega_rot: float = 16.0         # Natural frequency of angular wobble
var zeta_rot: float = 0.24          # Damping of angular wobble
var cleft_coupling: float = 14.0    # Elastic shear transfer between cheeks

# GPU Shader Ripple Shockwave State
var shock_time: float = 99.0
var shock_amp: float = 0.0
var shock_pos: Vector3 = Vector3(0.0, 0.81, 0.09)

# Real-time Touch Poke & Drag State
var is_touching: bool = false
var touch_is_left: bool = true
var touch_depth: float = 0.0
var touch_pos_local: Vector3 = Vector3(0.0, 0.81, 0.09)
var touch_drag_target: Vector3 = Vector3.ZERO

# Blush / Redness State
var blush_l: float = 0.0
var blush_r: float = 0.0
var cool_rate: float = 0.06

# Idle breathing motion
var breath_time: float = 0.0

func _resolve_nodes() -> void:
	if not skeleton: skeleton = find_child("Skeleton3D", true, false)
	if not body_mesh: body_mesh = find_child("Body", true, false)
	if not panty_classic: panty_classic = find_child("Panty_Classic", true, false)
	if not panty_thong: panty_thong = find_child("Panty_Thong", true, false)

func _ready() -> void:
	_resolve_nodes()
	_setup_materials()
	_setup_bones()
	set_panty(1) # Default to Tanga Sexy

func _setup_materials() -> void:
	skin_mat = ShaderMaterial.new()
	skin_mat.shader = skin_shader
	skin_mat.set_shader_parameter("skin_color", Color(0.95, 0.77, 0.70, 1.0))
	skin_mat.set_shader_parameter("blush_color", Color(0.96, 0.20, 0.26, 1.0))
	skin_mat.set_shader_parameter("normal_map", tex_skin_normal)
	skin_mat.set_shader_parameter("normal_strength", 0.26)
	skin_mat.set_shader_parameter("normal_scale", Vector2(18.0, 18.0))
	skin_mat.set_shader_parameter("roughness", 0.35)
	skin_mat.set_shader_parameter("specular", 0.52)
	skin_mat.set_shader_parameter("blush_left", 0.0)
	skin_mat.set_shader_parameter("blush_right", 0.0)
	if body_mesh:
		body_mesh.material_override = skin_mat
		
	panty_classic_mat = ShaderMaterial.new()
	panty_classic_mat.shader = panty_shader
	panty_classic_mat.set_shader_parameter("texture_albedo", tex_panty_classic)
	panty_classic_mat.set_shader_parameter("color_tint", Color(1.0, 1.0, 1.0, 1.0))
	panty_classic_mat.set_shader_parameter("roughness", 0.35)
	if panty_classic:
		panty_classic.material_override = panty_classic_mat

	panty_thong_mat = ShaderMaterial.new()
	panty_thong_mat.shader = panty_shader
	panty_thong_mat.set_shader_parameter("texture_albedo", tex_panty_thong)
	panty_thong_mat.set_shader_parameter("color_tint", Color(1.0, 1.0, 1.0, 1.0))
	panty_thong_mat.set_shader_parameter("roughness", 0.22)
	panty_thong_mat.set_shader_parameter("metallic", 0.15)
	if panty_thong:
		panty_thong.material_override = panty_thong_mat

func _setup_bones() -> void:
	if not skeleton:
		return
	bone_cheek_l = skeleton.find_bone("Cheek_L")
	bone_cheek_r = skeleton.find_bone("Cheek_R")
	
	if bone_cheek_l != -1:
		rest_pos_l = skeleton.get_bone_rest(bone_cheek_l).origin
		rest_rot_l = skeleton.get_bone_rest(bone_cheek_l).basis.get_rotation_quaternion()
	if bone_cheek_r != -1:
		rest_pos_r = skeleton.get_bone_rest(bone_cheek_r).origin
		rest_rot_r = skeleton.get_bone_rest(bone_cheek_r).basis.get_rotation_quaternion()

func _process(delta: float) -> void:
	var dt = clamp(delta, 0.001, 0.033)
	
	# 1. Idle breathing sway (sensual organic rhythm)
	breath_time += dt * 2.2
	var breath_sway_l = Vector3(
		sin(breath_time * 0.7) * 0.0008,
		sin(breath_time) * 0.0022,
		cos(breath_time * 0.5) * 0.0016
	)
	var breath_sway_r = Vector3(
		-sin(breath_time * 0.7) * 0.0008,
		sin(breath_time) * 0.0022,
		cos(breath_time * 0.5) * 0.0016
	)

	# 2. Interactive Touch Drag Pull
	if is_touching:
		var touch_target = touch_drag_target
		if touch_is_left:
			vel_l += (touch_target - pos_l) * 45.0 * dt
			squash_vel_l += (0.35 - squash_l) * 40.0 * dt
		else:
			vel_r += (touch_target - pos_r) * 45.0 * dt
			squash_vel_r += (0.35 - squash_r) * 40.0 * dt

	# 3. Left Cheek Harmonic Springs
	var d_bounce = 2.0 * zeta_bounce * omega_bounce
	var acc_l = - (omega_bounce * omega_bounce) * pos_l - d_bounce * vel_l
	# Inter-cheek cleft elastic shear
	acc_l += (pos_r - pos_l) * cleft_coupling
	vel_l += acc_l * dt
	pos_l += vel_l * dt
	
	# Left Squash & Stretch
	var acc_sq_l = - (omega_squash * omega_squash) * squash_l - (2.0 * zeta_squash * omega_squash) * squash_vel_l
	squash_vel_l += acc_sq_l * dt
	squash_l += squash_vel_l * dt
	
	# Left Angular Tilt
	var acc_rot_l = - (omega_rot * omega_rot) * rot_l - (2.0 * zeta_rot * omega_rot) * rot_vel_l
	rot_vel_l += acc_rot_l * dt
	rot_l += rot_vel_l * dt

	# 4. Right Cheek Harmonic Springs
	var acc_r = - (omega_bounce * omega_bounce) * pos_r - d_bounce * vel_r
	acc_r += (pos_l - pos_r) * cleft_coupling
	vel_r += acc_r * dt
	pos_r += vel_r * dt
	
	var acc_sq_r = - (omega_squash * omega_squash) * squash_r - (2.0 * zeta_squash * omega_squash) * squash_vel_r
	squash_vel_r += acc_sq_r * dt
	squash_r += squash_vel_r * dt
	
	var acc_rot_r = - (omega_rot * omega_rot) * rot_r - (2.0 * zeta_rot * omega_rot) * rot_vel_r
	rot_vel_r += acc_rot_r * dt
	rot_r += rot_vel_r * dt

	# 5. Secondary High-Frequency Jelly Shimmer Wobble (34 rad/s)
	ripple_amp_l = max(0.0, ripple_amp_l - 4.5 * dt)
	ripple_amp_r = max(0.0, ripple_amp_r - 4.5 * dt)
	var shimmer_l = sin(breath_time * 15.0) * (ripple_amp_l * 0.007)
	var shimmer_r = sin(breath_time * 15.0 + 1.2) * (ripple_amp_r * 0.007)

	# 6. Apply Transforms to Skeleton3D Bones
	if skeleton:
		# Convert world displacement (X=right, Y=up, Z=rearward) to Pelvis bone space:
		# Pelvis X = +world_x, Pelvis Y = -world_y, Pelvis Z = -world_z
		if bone_cheek_l != -1:
			var total_disp_l = pos_l + breath_sway_l + Vector3(0.0, shimmer_l, shimmer_l)
			var pos_pelvis_l = Vector3(total_disp_l.x, -total_disp_l.y, -total_disp_l.z)
			skeleton.set_bone_pose_position(bone_cheek_l, rest_pos_l + pos_pelvis_l)
			
			# Volume-Preserving Squash & Stretch Scale:
			var sq_l = clamp(squash_l, -0.4, 0.6)
			var sx_l = 1.0 + sq_l * 0.38
			var sy_l = 1.0 + sq_l * 0.38
			var sz_l = clamp(1.0 / (sx_l * sy_l), 0.6, 1.4)
			skeleton.set_bone_pose_scale(bone_cheek_l, Vector3(sx_l, sy_l, sz_l))
			
			# Angular Wobble Rotation:
			var q_tilt_l = Quaternion.from_euler(Vector3(rot_l.x, -rot_l.y, -rot_l.z))
			skeleton.set_bone_pose_rotation(bone_cheek_l, rest_rot_l * q_tilt_l)

		if bone_cheek_r != -1:
			var total_disp_r = pos_r + breath_sway_r + Vector3(0.0, shimmer_r, shimmer_r)
			var pos_pelvis_r = Vector3(total_disp_r.x, -total_disp_r.y, -total_disp_r.z)
			skeleton.set_bone_pose_position(bone_cheek_r, rest_pos_r + pos_pelvis_r)
			
			var sq_r = clamp(squash_r, -0.4, 0.6)
			var sx_r = 1.0 + sq_r * 0.38
			var sy_r = 1.0 + sq_r * 0.38
			var sz_r = clamp(1.0 / (sx_r * sy_r), 0.6, 1.4)
			skeleton.set_bone_pose_scale(bone_cheek_r, Vector3(sx_r, sy_r, sz_r))
			
			var q_tilt_r = Quaternion.from_euler(Vector3(rot_r.x, -rot_r.y, -rot_r.z))
			skeleton.set_bone_pose_rotation(bone_cheek_r, rest_rot_r * q_tilt_r)

	# 7. GPU Shader Shockwave Time Advance
	if shock_time < 1.0:
		shock_time += dt
		_update_shader_param("slap_wave_time", shock_time)
		_update_shader_param("slap_wave_amp", shock_amp)
		_update_shader_param("slap_impact_pos", shock_pos)

	# 8. Real-time Touch Indentation Update in Shaders
	if is_touching:
		touch_depth = move_toward(touch_depth, 0.028, dt * 0.25)
	else:
		touch_depth = move_toward(touch_depth, 0.0, dt * 0.18)
	_update_shader_param("touch_depth", touch_depth)
	_update_shader_param("touch_pos", touch_pos_local)

	# 9. Dissipate heat / blush
	blush_l = max(0.0, blush_l - cool_rate * dt)
	blush_r = max(0.0, blush_r - cool_rate * dt)
	_update_shader_param("blush_left", blush_l)
	_update_shader_param("blush_right", blush_r)

func _update_shader_param(param_name: String, value: Variant) -> void:
	if skin_mat:
		skin_mat.set_shader_parameter(param_name, value)
	if panty_classic_mat:
		panty_classic_mat.set_shader_parameter(param_name, value)
	if panty_thong_mat:
		panty_thong_mat.set_shader_parameter(param_name, value)

# Real-Time Touch Interaction
func start_touch(world_pos: Vector3, is_left: bool) -> void:
	is_touching = true
	touch_is_left = is_left
	touch_pos_local = world_pos
	touch_drag_target = Vector3(0.0, 0.0, -0.025)
	touch_depth = 0.015
	
	# Initial indent impulse
	if is_left:
		vel_l += Vector3(0.0, 0.0, -0.18)
		squash_vel_l += 1.8
	else:
		vel_r += Vector3(0.0, 0.0, -0.18)
		squash_vel_r += 1.8

func update_touch_drag(drag_delta_screen: Vector2) -> void:
	# Pull the flesh elastically along the finger direction
	var stretch_x = clamp(drag_delta_screen.x * 0.00035, -0.035, 0.035)
	var stretch_y = clamp(-drag_delta_screen.y * 0.00035, -0.035, 0.035)
	touch_drag_target = Vector3(stretch_x, stretch_y, -0.030)

func end_touch(was_slap: bool) -> void:
	is_touching = false
	if not was_slap:
		# Elastic snap-back release from being pulled
		if touch_is_left:
			vel_l += -pos_l * 16.0
			squash_vel_l -= squash_l * 14.0
			ripple_amp_l = 0.55
		else:
			vel_r += -pos_r * 16.0
			squash_vel_r -= squash_r * 14.0
			ripple_amp_r = 0.55

# High-Energy Impact Slap
func apply_slap(is_left: bool, force_normalized: float, slap_direction_2d: Vector2) -> void:
	var strength = clamp(force_normalized, 0.5, 2.4)
	
	# 1. Primary Inward Impact Compression & Lateral Swipe
	var dir_x = slap_direction_2d.x if slap_direction_2d.length() > 0.05 else (0.4 if is_left else -0.4)
	var dir_y = -slap_direction_2d.y if slap_direction_2d.length() > 0.05 else 0.2
	
	var impulse_primary = Vector3(
		dir_x * 0.42 * strength,
		dir_y * 0.38 * strength,
		-0.72 * strength     # Deep inward compression into the body (-Z in world)
	)
	
	# 2. Volume-Preserving Squash Velocity
	var sq_impulse = 4.2 * strength
	
	# 3. Rotational Kick Wobble
	var rot_impulse = Vector3(-dir_y * 6.5, dir_x * 7.5, -dir_x * 5.0) * strength
	
	# 4. Cross-Cheek Wave Transfer (Elastic shear across cleft to the other cheek)
	var impulse_cross = Vector3(
		-dir_x * 0.22 * strength,
		dir_y * 0.16 * strength,
		0.26 * strength      # Opposite cheek sways outward in harmonic antiphase
	)
	var sq_cross = 1.6 * strength
	
	if is_left:
		vel_l += impulse_primary
		squash_vel_l += sq_impulse
		rot_vel_l += rot_impulse
		ripple_amp_l = min(1.3, ripple_amp_l + 0.95 * strength)
		
		# Cross-wave to right cheek
		vel_r += impulse_cross
		squash_vel_r += sq_cross
		rot_vel_r += Vector3(rot_impulse.x * 0.4, -rot_impulse.y * 0.4, -rot_impulse.z * 0.4)
		ripple_amp_r = min(1.0, ripple_amp_r + 0.45 * strength)
		
		blush_l = min(1.0, blush_l + strength * 0.24)
		blush_r = min(1.0, blush_r + strength * 0.06)
		shock_pos = Vector3(-0.11, 0.81, 0.09)
	else:
		vel_r += impulse_primary
		squash_vel_r += sq_impulse
		rot_vel_r += rot_impulse
		ripple_amp_r = min(1.3, ripple_amp_r + 0.95 * strength)
		
		vel_l += impulse_cross
		squash_vel_l += sq_cross
		rot_vel_l += Vector3(rot_impulse.x * 0.4, -rot_impulse.y * 0.4, -rot_impulse.z * 0.4)
		ripple_amp_l = min(1.0, ripple_amp_l + 0.45 * strength)
		
		blush_r = min(1.0, blush_r + strength * 0.24)
		blush_l = min(1.0, blush_l + strength * 0.06)
		shock_pos = Vector3(0.11, 0.81, 0.09)
		
	# Trigger GPU Shockwave Ripple
	shock_time = 0.0
	shock_amp = clamp(0.014 * strength, 0.008, 0.035)

func set_panty(index: int) -> void:
	_resolve_nodes()
	match index:
		0:
			if panty_classic: panty_classic.visible = true
			if panty_thong: panty_thong.visible = false
		1:
			if panty_classic: panty_classic.visible = false
			if panty_thong: panty_thong.visible = true
		2:
			if panty_classic: panty_classic.visible = false
			if panty_thong: panty_thong.visible = false

func set_skin_tone(color: Color) -> void:
	if skin_mat:
		skin_mat.set_shader_parameter("skin_color", color)

func reset_redness() -> void:
	blush_l = 0.0
	blush_r = 0.0
	_update_shader_param("blush_left", 0.0)
	_update_shader_param("blush_right", 0.0)

func get_skin_material() -> ShaderMaterial:
	return skin_mat
