extends Node3D

@onready var camera: Camera3D = $Camera3D

var target_distance: float = 1.35
var current_distance: float = 1.35
var min_dist: float = 0.75
var max_dist: float = 2.80

var target_yaw: float = 0.0
var current_yaw: float = 0.0

var target_pitch: float = -3.5
var current_pitch: float = -3.5

var trauma: float = 0.0
var orbit_velocity: Vector2 = Vector2.ZERO

func _ready() -> void:
	if not camera:
		camera = find_child("Camera3D", true, false)
	_apply_transform()

func _process(delta: float) -> void:
	# Inertia glide from touch swipe release
	if orbit_velocity.length_squared() > 0.01:
		target_yaw = clamp(target_yaw + orbit_velocity.x * delta, -80.0, 80.0)
		target_pitch = clamp(target_pitch + orbit_velocity.y * delta, -35.0, 25.0)
		orbit_velocity = orbit_velocity.lerp(Vector2.ZERO, delta * 6.5)
	else:
		orbit_velocity = Vector2.ZERO

	current_distance = lerp(current_distance, target_distance, delta * 12.0)
	current_yaw = lerp(current_yaw, target_yaw, delta * 12.0)
	current_pitch = lerp(current_pitch, target_pitch, delta * 12.0)
	_apply_transform()
	
	if trauma > 0.0:
		trauma = max(0.0, trauma - delta * 2.5)
		var shake = trauma * trauma * 0.03
		if camera:
			camera.position.x = randf_range(-shake, shake)
			camera.position.y = randf_range(-shake, shake)
	else:
		if camera:
			camera.position.x = 0.0
			camera.position.y = 0.0

func _apply_transform() -> void:
	rotation_degrees.y = current_yaw
	rotation_degrees.x = current_pitch
	if camera:
		camera.position.z = current_distance

func zoom_step(amount: float) -> void:
	# amount > 0: zoom in (closer), amount < 0: zoom out (further)
	target_distance = clamp(target_distance - amount, min_dist, max_dist)

func set_zoom_ratio(ratio: float) -> void:
	# ratio from 0.0 (closest) to 1.0 (furthest)
	target_distance = lerp(min_dist, max_dist, clamp(ratio, 0.0, 1.0))

func get_zoom_ratio() -> float:
	return (target_distance - min_dist) / (max_dist - min_dist)

func orbit_step(yaw_delta: float, pitch_delta: float = 0.0) -> void:
	orbit_velocity = Vector2.ZERO
	target_yaw = clamp(target_yaw + yaw_delta, -80.0, 80.0)
	target_pitch = clamp(target_pitch + pitch_delta, -35.0, 25.0)

func add_orbit_drag(delta_yaw: float, delta_pitch: float = 0.0) -> void:
	orbit_velocity = Vector2.ZERO
	target_yaw = clamp(target_yaw + delta_yaw, -80.0, 80.0)
	target_pitch = clamp(target_pitch + delta_pitch, -35.0, 25.0)

func set_orbit_velocity(vel: Vector2) -> void:
	orbit_velocity = vel

func set_yaw(val: float) -> void:
	orbit_velocity = Vector2.ZERO
	target_yaw = clamp(val, -80.0, 80.0)

func get_yaw() -> float:
	return target_yaw

func reset_view() -> void:
	orbit_velocity = Vector2.ZERO
	target_distance = 1.35
	target_yaw = 0.0
	target_pitch = -3.5

func add_trauma(amt: float) -> void:
	trauma = min(1.0, trauma + amt)
