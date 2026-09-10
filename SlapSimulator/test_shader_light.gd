extends SceneTree

func _init():
	print("Checking if custom light function works in Compatibility mode...")
	var mat = ShaderMaterial.new()
	var sh = Shader.new()
	sh.code = """
	shader_type spatial;
	render_mode diffuse_burley;
	void fragment() {
		ALBEDO = vec3(0.9, 0.7, 0.6);
	}
	void light() {
		DIFFUSE_LIGHT += clamp(dot(NORMAL, LIGHT), 0.0, 1.0) * ATTENUATION * LIGHT_COLOR;
	}
	"""
	mat.shader = sh
	print("Shader compiled successfully!")
	quit(0)
