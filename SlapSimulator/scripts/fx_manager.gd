extends Node

var star_tex: Texture2D = preload("res://assets/textures/star.png")
var heart_tex: Texture2D = preload("res://assets/textures/heart.png")

var comic_words: Array[String] = [
	"¡PERFECT! 💥", "¡CRITICAL! 🔥", "¡SPANK! ⚡", "¡EXCELLENT! ✨", "¡OUCH! 🍑"
]

var comic_colors: Array[Color] = [
	Color(1.0, 0.85, 0.2),
	Color(1.0, 0.35, 0.55),
	Color(0.2, 0.9, 1.0),
	Color(1.0, 0.5, 0.2)
]

func spawn_hit_particles(parent: Node3D, pos_3d: Vector3, force_normalized: float) -> void:
	if not parent or not parent.is_inside_tree():
		return
		
	# Subtle realistic micro-sheen on heavy impact
	if force_normalized < 0.9:
		return
		
	var count = int(clamp(4 + force_normalized * 4, 4, 10))
	
	var p = CPUParticles3D.new()
	p.position = pos_3d
	p.emitting = false
	p.one_shot = true
	p.explosiveness = 0.98
	p.amount = count
	p.lifetime = 0.35
	
	var quad = QuadMesh.new()
	quad.size = Vector2(0.02, 0.02)
	var mat = StandardMaterial3D.new()
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	mat.albedo_color = Color(1.0, 0.92, 0.82, 0.55)
	quad.material = mat
	p.mesh = quad
	
	p.direction = Vector3(0.0, 0.2, 1.0)
	p.spread = 45.0
	p.initial_velocity_min = 0.8 + force_normalized * 0.5
	p.initial_velocity_max = 1.6 + force_normalized * 0.8
	p.gravity = Vector3(0.0, -2.5, 0.0)
	p.damping_min = 2.0
	p.damping_max = 3.5
	p.scale_amount_min = 0.4
	p.scale_amount_max = 0.9
	
	parent.add_child(p)
	p.emitting = true
	
	var tree = parent.get_tree()
	if tree:
		tree.create_timer(0.7).timeout.connect(func(): if is_instance_valid(p): p.queue_free())
	else:
		p.queue_free()

func spawn_floating_text(canvas: Node, screen_pos: Vector2, force_normalized: float) -> void:
	if not canvas or not canvas.is_inside_tree():
		return
		
	var label = Label.new()
	
	var text_idx = randi() % comic_words.size()
	label.text = comic_words[text_idx]
	label.position = screen_pos + Vector2(randf_range(-30, 30), randf_range(-20, 20))
	
	var col = comic_colors[randi() % comic_colors.size()]
	label.add_theme_color_override("font_color", col)
	label.add_theme_color_override("font_outline_color", Color.BLACK)
	label.add_theme_constant_override("outline_size", 8)
	label.add_theme_font_size_override("font_size", int(24 + force_normalized * 14))
	
	label.pivot_offset = Vector2(80, 20)
	label.scale = Vector2(0.2, 0.2)
	
	canvas.add_child(label)
	
	var tw = label.create_tween()
	if tw:
		tw.tween_property(label, "scale", Vector2(1.3, 1.3), 0.12).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		tw.tween_property(label, "scale", Vector2(1.0, 1.0), 0.08)
		tw.parallel().tween_property(label, "position:y", label.position.y - 70.0, 0.45).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tw.tween_property(label, "modulate:a", 0.0, 0.25)
		tw.tween_callback(func(): if is_instance_valid(label): label.queue_free())
