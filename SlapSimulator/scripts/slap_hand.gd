extends Node3D
class_name SlapHandVisual

var active_tween: Tween

func _ready() -> void:
	visible = false

func play_slap_anim(target_pos: Vector3, swipe_dir: Vector2, force_normalized: float) -> void:
	if active_tween and active_tween.is_valid():
		active_tween.kill()
		
	visible = true
	scale = Vector3.ONE * clamp(0.9 + force_normalized * 0.15, 0.8, 1.4)
	
	# Determine incoming angle from swipe direction
	var angle = atan2(swipe_dir.y, swipe_dir.x) if swipe_dir.length() > 0.05 else 0.0
	rotation = Vector3(-0.3, 0.0, angle - PI * 0.5)
	
	# Start position: pulled back towards camera (+Z) and offset opposite to swipe direction
	var start_offset = Vector3(-swipe_dir.x * 0.25, -swipe_dir.y * 0.25, 0.40)
	position = target_pos + start_offset
	
	active_tween = create_tween()
	# Swoop in to strike
	var strike_time = clamp(0.09 - force_normalized * 0.02, 0.04, 0.10)
	active_tween.tween_property(self, "position", target_pos, strike_time).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	
	# Impact squash
	active_tween.parallel().tween_property(self, "scale", scale * Vector3(1.15, 1.15, 0.7), strike_time)
	
	# Recoil and bounce off towards viewer (+Z)
	var recoil_pos = target_pos + Vector3(swipe_dir.x * 0.12, 0.08, 0.30)
	var recoil_time = 0.14
	active_tween.tween_property(self, "position", recoil_pos, recoil_time).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	active_tween.parallel().tween_property(self, "scale", Vector3.ZERO, recoil_time).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	
	active_tween.tween_callback(func(): visible = false)
