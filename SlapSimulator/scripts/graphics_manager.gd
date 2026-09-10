extends Node
class_name GraphicsManager

const SAVE_PATH = "user://graphics_settings.cfg"

# Available settings
var preset: String = "Alta" # "Baja", "Media", "Alta", "Ultra"
var shadows_quality: int = 1 # 0: OFF, 1: Suaves, 2: Alta
var msaa_quality: int = 1 # 0: OFF, 1: 2X, 2: 4X
var glow_enabled: bool = true
var sss_enabled: bool = true
var resolution_scale: float = 1.0 # 0.75 or 1.0
var target_fps: int = 60 # 30, 60, 0 (unlimited)

# References
var world_env: WorldEnvironment
var key_light: DirectionalLight3D
var rim_light: DirectionalLight3D
var fill_light: DirectionalLight3D
var character: Node3D

func _ready() -> void:
	load_settings()
	call_deferred("apply_settings")

func set_preset(preset_name: String) -> void:
	preset = preset_name
	match preset_name:
		"Baja":
			shadows_quality = 0
			msaa_quality = 0
			glow_enabled = false
			sss_enabled = false
			resolution_scale = 0.75
			target_fps = 30
		"Media":
			shadows_quality = 1
			msaa_quality = 0
			glow_enabled = false
			sss_enabled = true
			resolution_scale = 1.0
			target_fps = 60
		"Alta":
			shadows_quality = 1
			msaa_quality = 1
			glow_enabled = true
			sss_enabled = true
			resolution_scale = 1.0
			target_fps = 60
		"Ultra":
			shadows_quality = 2
			msaa_quality = 2
			glow_enabled = true
			sss_enabled = true
			resolution_scale = 1.0
			target_fps = 0
	apply_settings()
	save_settings()

func cycle_shadows() -> int:
	shadows_quality = (shadows_quality + 1) % 3
	preset = "Personalizado"
	apply_settings()
	save_settings()
	return shadows_quality

func cycle_msaa() -> int:
	msaa_quality = (msaa_quality + 1) % 3
	preset = "Personalizado"
	apply_settings()
	save_settings()
	return msaa_quality

func toggle_glow() -> bool:
	glow_enabled = !glow_enabled
	preset = "Personalizado"
	apply_settings()
	save_settings()
	return glow_enabled

func toggle_sss() -> bool:
	sss_enabled = !sss_enabled
	preset = "Personalizado"
	apply_settings()
	save_settings()
	return sss_enabled

func toggle_resolution_scale() -> float:
	if resolution_scale >= 0.99:
		resolution_scale = 0.75
	else:
		resolution_scale = 1.0
	preset = "Personalizado"
	apply_settings()
	save_settings()
	return resolution_scale

func cycle_fps() -> int:
	match target_fps:
		30: target_fps = 60
		60: target_fps = 0
		_: target_fps = 30
	preset = "Personalizado"
	apply_settings()
	save_settings()
	return target_fps

func get_shadows_label() -> String:
	match shadows_quality:
		0: return "🌑 Sombras: DESACTIVADAS"
		1: return "⛅ Sombras: SUAVES (Media)"
		2: return "☀️ Sombras: ALTAS (Ultra HD)"
		_: return "Sombras: Suaves"

func get_msaa_label() -> String:
	match msaa_quality:
		0: return "📐 Antialiasing (MSAA): OFF"
		1: return "📐 Antialiasing (MSAA): 2X"
		2: return "✨ Antialiasing (MSAA): 4X Nítido"
		_: return "MSAA: 2X"

func get_glow_label() -> String:
	return "✨ Brillo Bloom / Glow: SÍ" if glow_enabled else "🌑 Brillo Bloom / Glow: NO"

func get_sss_label() -> String:
	return "🍑 Piel SSS y Poros HD: ACTIVADO" if sss_enabled else "⚪ Piel SSS y Poros: DESACTIVADO"

func get_scale_label() -> String:
	return "📱 Resolución 3D: 100% Nativa" if resolution_scale >= 0.99 else "⚡ Resolución 3D: 75% Rendimiento"

func get_fps_label() -> String:
	match target_fps:
		30: return "⏱️ Límite FPS: 30 FPS (Ahorro Batería)"
		60: return "🚀 Límite FPS: 60 FPS (Fluido)"
		0: return "⚡ Límite FPS: Ilimitado (Máx Hz)"
		_: return "⏱️ Límite FPS: 60 FPS"

func apply_settings() -> void:
	# 1. Target FPS
	Engine.max_fps = target_fps
	
	# 2. Viewport settings (MSAA & Resolution Scaling)
	var vp = get_viewport()
	if vp:
		match msaa_quality:
			0: vp.msaa_3d = Viewport.MSAA_DISABLED
			1: vp.msaa_3d = Viewport.MSAA_2X
			2: vp.msaa_3d = Viewport.MSAA_4X
		
		vp.scaling_3d_scale = resolution_scale
		vp.scaling_3d_mode = Viewport.SCALING_3D_MODE_BILINEAR
		
	# 3. Environment (Glow)
	if not world_env:
		world_env = get_tree().root.find_child("WorldEnvironment", true, false)
	if world_env and world_env.environment:
		world_env.environment.glow_enabled = glow_enabled
		
	# 4. Shadows
	if not key_light:
		key_light = get_tree().root.find_child("KeyLight", true, false)
	if key_light:
		match shadows_quality:
			0:
				key_light.shadow_enabled = false
			1:
				key_light.shadow_enabled = true
				key_light.shadow_blur = 1.8
			2:
				key_light.shadow_enabled = true
				key_light.shadow_blur = 2.4
				
	# 5. Character Shader (SSS & Normal Map)
	if not character:
		character = get_tree().root.find_child("Character", true, false)
	if character:
		var sm = character.get("skin_mat")
		if not sm and character.has_method("get_skin_material"):
			sm = character.call("get_skin_material")
		if sm:
			sm.set_shader_parameter("sss_strength", 1.0 if sss_enabled else 0.0)
			sm.set_shader_parameter("normal_strength", 0.40 if sss_enabled else 0.0)

func save_settings() -> void:
	var cfg = ConfigFile.new()
	cfg.set_value("graphics", "preset", preset)
	cfg.set_value("graphics", "shadows", shadows_quality)
	cfg.set_value("graphics", "msaa", msaa_quality)
	cfg.set_value("graphics", "glow", glow_enabled)
	cfg.set_value("graphics", "sss", sss_enabled)
	cfg.set_value("graphics", "res_scale", resolution_scale)
	cfg.set_value("graphics", "target_fps", target_fps)
	cfg.save(SAVE_PATH)

func load_settings() -> void:
	var cfg = ConfigFile.new()
	var err = cfg.load(SAVE_PATH)
	if err == OK:
		preset = cfg.get_value("graphics", "preset", "Alta")
		shadows_quality = cfg.get_value("graphics", "shadows", 1)
		msaa_quality = cfg.get_value("graphics", "msaa", 1)
		glow_enabled = cfg.get_value("graphics", "glow", true)
		sss_enabled = cfg.get_value("graphics", "sss", true)
		resolution_scale = cfg.get_value("graphics", "res_scale", 1.0)
		target_fps = cfg.get_value("graphics", "target_fps", 60)
	else:
		preset = "Alta"
		shadows_quality = 1
		msaa_quality = 1
		glow_enabled = true
		sss_enabled = true
		resolution_scale = 1.0
		target_fps = 60
	apply_settings()
