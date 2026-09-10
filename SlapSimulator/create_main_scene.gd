extends SceneTree

func _init():
	print("Building enhanced main.tscn with CameraRig and Zoom UI...")
	
	var root = Node3D.new()
	root.name = "Main"
	root.set_script(load("res://scripts/main.gd"))
	
	# 1. World Environment with Luxury Studio Sky IBL
	var env_node = WorldEnvironment.new()
	env_node.name = "WorldEnvironment"
	var env = Environment.new()
	env.background_mode = Environment.BG_SKY
	
	var sky = Sky.new()
	var sky_mat = PanoramaSkyMaterial.new()
	sky_mat.panorama = load("res://assets/textures/studio_sky.png")
	sky.sky_material = sky_mat
	env.sky = sky
	
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_sky_contribution = 0.50
	env.ambient_light_energy = 0.18
	env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	env.tonemap_exposure = 0.95
	env.glow_enabled = true
	env.glow_intensity = 0.10
	env.glow_bloom = 0.02
	env_node.environment = env
	root.add_child(env_node)
	env_node.owner = root
	
	# 2. Key Light (Top right rear warm softbox)
	var key_light = DirectionalLight3D.new()
	key_light.name = "KeyLight"
	key_light.light_color = Color(1.0, 0.95, 0.90)
	key_light.light_energy = 0.65
	key_light.shadow_enabled = true
	key_light.shadow_blur = 1.8
	key_light.rotation_degrees = Vector3(-35, 32, 0)
	root.add_child(key_light)
	key_light.owner = root
	
	# 3. Rim Light (Cool edge definition for silhouette)
	var rim_light = DirectionalLight3D.new()
	rim_light.name = "RimLight"
	rim_light.light_color = Color(0.85, 0.92, 1.0)
	rim_light.light_energy = 0.40
	rim_light.rotation_degrees = Vector3(32, -145, 0)
	root.add_child(rim_light)
	rim_light.owner = root
	
	# 4. Fill Light (Soft shadow relief)
	var fill_light = DirectionalLight3D.new()
	fill_light.name = "FillLight"
	fill_light.light_color = Color(0.92, 0.88, 0.95)
	fill_light.light_energy = 0.20
	fill_light.rotation_degrees = Vector3(-15, -60, 0)
	root.add_child(fill_light)
	fill_light.owner = root
	
	# 5. CameraRig (Handles Zoom, Orbit, Pitch, Shake)
	var cam_rig = Node3D.new()
	cam_rig.name = "CameraRig"
	cam_rig.position = Vector3(0.0, 0.82, 0.0) # Centered on the hips/buttocks
	cam_rig.set_script(load("res://scripts/camera_rig.gd"))
	root.add_child(cam_rig)
	cam_rig.owner = root
	
	var cam = Camera3D.new()
	cam.name = "Camera3D"
	cam.position = Vector3(0.0, 0.0, 1.35) # Positioned behind buttocks
	cam.fov = 42.0
	cam.current = true
	cam_rig.add_child(cam)
	cam.owner = root
	
	# 6. Character Instance
	var char_scene = load("res://assets/models/character.glb")
	var char_inst = char_scene.instantiate()
	char_inst.name = "Character"
	char_inst.set_script(load("res://scripts/character.gd"))
	root.add_child(char_inst)
	char_inst.owner = root
	
	# 7. Slap Hand Instance
	var hand_scene = load("res://assets/models/hand.glb")
	var hand_inst = hand_scene.instantiate()
	hand_inst.name = "SlapHand"
	hand_inst.set_script(load("res://scripts/slap_hand.gd"))
	root.add_child(hand_inst)
	hand_inst.owner = root
	
	# 8. Managers
	var snd_node = Node.new()
	snd_node.name = "SoundManager"
	snd_node.set_script(load("res://scripts/sound_manager.gd"))
	root.add_child(snd_node)
	snd_node.owner = root
	
	var fx_node = Node.new()
	fx_node.name = "FXManager"
	fx_node.set_script(load("res://scripts/fx_manager.gd"))
	root.add_child(fx_node)
	fx_node.owner = root
	
	var gfx_node = Node.new()
	gfx_node.name = "GraphicsManager"
	gfx_node.set_script(load("res://scripts/graphics_manager.gd"))
	root.add_child(gfx_node)
	gfx_node.owner = root
	
	# 9. CanvasLayer & UI
	var canvas = CanvasLayer.new()
	canvas.name = "CanvasLayer"
	root.add_child(canvas)
	canvas.owner = root
	
	var root_ui = Control.new()
	root_ui.name = "RootUI"
	root_ui.set_anchors_preset(Control.PRESET_FULL_RECT)
	canvas.add_child(root_ui)
	root_ui.owner = root
	
	# Fullscreen Touch Area
	var touch_area = Control.new()
	touch_area.name = "TouchArea"
	touch_area.unique_name_in_owner = true
	touch_area.set_anchors_preset(Control.PRESET_FULL_RECT)
	touch_area.mouse_filter = Control.MOUSE_FILTER_PASS
	root_ui.add_child(touch_area)
	touch_area.owner = root
	
	# Helper for modern glassmorphism styles
	var make_glass = func(bg: Color, border: Color, radius: int = 16, border_w: int = 1, pad_x: int = 12, pad_y: int = 6) -> StyleBoxFlat:
		var s = StyleBoxFlat.new()
		s.bg_color = bg
		s.border_color = border
		s.set_border_width_all(border_w)
		s.set_corner_radius_all(radius)
		s.content_margin_left = pad_x
		s.content_margin_right = pad_x
		s.content_margin_top = pad_y
		s.content_margin_bottom = pad_y
		return s
		
	var style_btn = func(btn: Button, accent: Color = Color(1.0, 0.45, 0.75), radius: int = 16, pad_x: int = 12, pad_y: int = 6):
		var norm = make_glass.call(Color(0.12, 0.09, 0.18, 0.82), Color(accent.r, accent.g, accent.b, 0.40), radius, 1, pad_x, pad_y)
		var hov = make_glass.call(Color(0.22, 0.16, 0.30, 0.90), Color(accent.r, accent.g, accent.b, 0.75), radius, 1, pad_x, pad_y)
		var press = make_glass.call(Color(0.92, 0.25, 0.58, 0.95), Color(1.0, 0.90, 0.96, 1.0), radius, 2, pad_x, pad_y)
		btn.add_theme_stylebox_override("normal", norm)
		btn.add_theme_stylebox_override("hover", hov)
		btn.add_theme_stylebox_override("pressed", press)
		btn.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		btn.add_theme_color_override("font_color", Color(0.95, 0.92, 0.98))
		btn.add_theme_color_override("font_hover_color", Color(1.0, 0.95, 1.0))
		btn.add_theme_color_override("font_pressed_color", Color(1.0, 1.0, 1.0))

	# TOP BAR (Stats & Global Controls)
	var top_panel = PanelContainer.new()
	top_panel.name = "TopPanel"
	top_panel.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top_panel.offset_left = 16
	top_panel.offset_top = 18
	top_panel.offset_right = -16
	top_panel.offset_bottom = 152
	
	var top_style = make_glass.call(Color(0.10, 0.08, 0.16, 0.88), Color(1.0, 0.45, 0.75, 0.35), 20, 1, 14, 10)
	top_panel.add_theme_stylebox_override("panel", top_style)
	root_ui.add_child(top_panel)
	top_panel.owner = root
	
	var top_vbox = VBoxContainer.new()
	top_vbox.add_theme_constant_override("separation", 6)
	top_panel.add_child(top_vbox)
	top_vbox.owner = root
	
	var title_hbox = HBoxContainer.new()
	title_hbox.add_theme_constant_override("separation", 8)
	top_vbox.add_child(title_hbox)
	title_hbox.owner = root

	var title_lbl = Label.new()
	title_lbl.text = "✨ YNA"
	title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	title_lbl.add_theme_font_size_override("font_size", 22)
	title_lbl.add_theme_color_override("font_color", Color(1.0, 0.55, 0.80))
	title_hbox.add_child(title_lbl)
	title_lbl.owner = root

	var btn_mode = Button.new()
	btn_mode.name = "BtnMode"
	btn_mode.unique_name_in_owner = true
	btn_mode.text = "👋 Nalgada"
	btn_mode.custom_minimum_size = Vector2(105, 34)
	btn_mode.toggle_mode = true
	btn_mode.button_pressed = false
	style_btn.call(btn_mode, Color(0.40, 0.80, 1.0), 16, 8, 4)
	title_hbox.add_child(btn_mode)
	btn_mode.owner = root

	var btn_cinema = Button.new()
	btn_cinema.name = "BtnCinema"
	btn_cinema.unique_name_in_owner = true
	btn_cinema.text = "🎬 Cine"
	btn_cinema.custom_minimum_size = Vector2(76, 34)
	style_btn.call(btn_cinema, Color(1.0, 0.50, 0.75), 16, 8, 4)
	title_hbox.add_child(btn_cinema)
	btn_cinema.owner = root

	var btn_settings_top = Button.new()
	btn_settings_top.name = "BtnSettingsTop"
	btn_settings_top.unique_name_in_owner = true
	btn_settings_top.text = "⚙️"
	btn_settings_top.custom_minimum_size = Vector2(42, 34)
	style_btn.call(btn_settings_top, Color(0.85, 0.75, 1.0), 16, 6, 4)
	title_hbox.add_child(btn_settings_top)
	btn_settings_top.owner = root

	var btn_restore_ui = Button.new()
	btn_restore_ui.name = "BtnRestoreUI"
	btn_restore_ui.unique_name_in_owner = true
	btn_restore_ui.text = "👁️ Mostrar UI"
	btn_restore_ui.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	btn_restore_ui.offset_left = -130
	btn_restore_ui.offset_top = 18
	btn_restore_ui.offset_right = -16
	btn_restore_ui.offset_bottom = 56
	btn_restore_ui.visible = false
	style_btn.call(btn_restore_ui, Color(1.0, 0.50, 0.75), 18, 12, 6)
	root_ui.add_child(btn_restore_ui)
	btn_restore_ui.owner = root
	
	var stats_hbox = HBoxContainer.new()
	stats_hbox.alignment = BoxContainer.ALIGNMENT_CENTER
	stats_hbox.add_theme_constant_override("separation", 6)
	top_vbox.add_child(stats_hbox)
	stats_hbox.owner = root
	
	var lbl_total = Label.new()
	lbl_total.name = "LblTotal"
	lbl_total.unique_name_in_owner = true
	lbl_total.text = "NALGADAS: 0"
	lbl_total.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lbl_total.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_total.add_theme_font_size_override("font_size", 14)
	stats_hbox.add_child(lbl_total)
	lbl_total.owner = root
	
	var lbl_combo = Label.new()
	lbl_combo.name = "LblCombo"
	lbl_combo.unique_name_in_owner = true
	lbl_combo.text = "COMBO: x1"
	lbl_combo.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lbl_combo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_combo.add_theme_font_size_override("font_size", 14)
	stats_hbox.add_child(lbl_combo)
	lbl_combo.owner = root
	
	var lbl_speed = Label.new()
	lbl_speed.name = "LblSpeed"
	lbl_speed.unique_name_in_owner = true
	lbl_speed.text = "FUERZA: 0 km/h"
	lbl_speed.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lbl_speed.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_speed.add_theme_font_size_override("font_size", 14)
	stats_hbox.add_child(lbl_speed)
	lbl_speed.owner = root
	
	var combo_bar = ProgressBar.new()
	combo_bar.name = "ComboBar"
	combo_bar.unique_name_in_owner = true
	combo_bar.custom_minimum_size = Vector2(0, 6)
	combo_bar.show_percentage = false
	var cbar_bg = make_glass.call(Color(0.08, 0.06, 0.12, 0.8), Color(0.4, 0.3, 0.5, 0.3), 3, 0, 0, 0)
	var cbar_fg = make_glass.call(Color(0.95, 0.28, 0.60, 0.95), Color(1.0, 0.8, 0.9, 0.8), 3, 0, 0, 0)
	combo_bar.add_theme_stylebox_override("background", cbar_bg)
	combo_bar.add_theme_stylebox_override("fill", cbar_fg)
	top_vbox.add_child(combo_bar)
	combo_bar.owner = root
	
	var lbl_rank = Label.new()
	lbl_rank.name = "LblRank"
	lbl_rank.unique_name_in_owner = true
	lbl_rank.text = "RANGO: Novato 👋"
	lbl_rank.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_rank.add_theme_font_size_override("font_size", 13)
	lbl_rank.add_theme_color_override("font_color", Color(0.98, 0.88, 0.50))
	top_vbox.add_child(lbl_rank)
	lbl_rank.owner = root
	
	# CAMERA CONTROLS BAR (Dedicated Zoom & Android 3D Orbit Dock)
	var cam_panel = PanelContainer.new()
	cam_panel.name = "CameraControlPanel"
	cam_panel.set_anchors_preset(Control.PRESET_TOP_WIDE)
	cam_panel.offset_left = 16
	cam_panel.offset_top = 160
	cam_panel.offset_right = -16
	cam_panel.offset_bottom = 248
	
	var cam_style = make_glass.call(Color(0.09, 0.07, 0.14, 0.85), Color(0.85, 0.40, 0.70, 0.35), 18, 1, 12, 8)
	cam_panel.add_theme_stylebox_override("panel", cam_style)
	root_ui.add_child(cam_panel)
	cam_panel.owner = root
	
	var cam_vbox = VBoxContainer.new()
	cam_vbox.add_theme_constant_override("separation", 6)
	cam_panel.add_child(cam_vbox)
	cam_vbox.owner = root
	
	# Row 1: Zoom Controls
	var zoom_hbox = HBoxContainer.new()
	zoom_hbox.alignment = BoxContainer.ALIGNMENT_CENTER
	zoom_hbox.add_theme_constant_override("separation", 8)
	cam_vbox.add_child(zoom_hbox)
	zoom_hbox.owner = root
	
	var btn_zoom_out = Button.new()
	btn_zoom_out.name = "BtnZoomOut"
	btn_zoom_out.unique_name_in_owner = true
	btn_zoom_out.text = "🔍➖"
	btn_zoom_out.custom_minimum_size = Vector2(44, 30)
	style_btn.call(btn_zoom_out, Color(0.6, 0.8, 1.0), 14, 4, 3)
	zoom_hbox.add_child(btn_zoom_out)
	btn_zoom_out.owner = root
	
	var zoom_slider = HSlider.new()
	zoom_slider.name = "ZoomSlider"
	zoom_slider.unique_name_in_owner = true
	zoom_slider.min_value = 0.0
	zoom_slider.max_value = 1.0
	zoom_slider.step = 0.02
	zoom_slider.value = 0.29
	zoom_slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	zoom_hbox.add_child(zoom_slider)
	zoom_slider.owner = root
	
	var btn_zoom_in = Button.new()
	btn_zoom_in.name = "BtnZoomIn"
	btn_zoom_in.unique_name_in_owner = true
	btn_zoom_in.text = "🔍➕"
	btn_zoom_in.custom_minimum_size = Vector2(44, 30)
	style_btn.call(btn_zoom_in, Color(0.6, 0.8, 1.0), 14, 4, 3)
	zoom_hbox.add_child(btn_zoom_in)
	btn_zoom_in.owner = root
	
	var btn_reset_cam = Button.new()
	btn_reset_cam.name = "BtnResetCam"
	btn_reset_cam.unique_name_in_owner = true
	btn_reset_cam.text = "🔄 Centrar"
	btn_reset_cam.custom_minimum_size = Vector2(76, 30)
	style_btn.call(btn_reset_cam, Color(1.0, 0.5, 0.75), 14, 6, 3)
	zoom_hbox.add_child(btn_reset_cam)
	btn_reset_cam.owner = root
	
	# Row 2: Orbit Turntable Controls (Android style)
	var orbit_hbox = HBoxContainer.new()
	orbit_hbox.alignment = BoxContainer.ALIGNMENT_CENTER
	orbit_hbox.add_theme_constant_override("separation", 8)
	cam_vbox.add_child(orbit_hbox)
	orbit_hbox.owner = root
	
	var btn_orbit_l = Button.new()
	btn_orbit_l.name = "BtnOrbitL"
	btn_orbit_l.unique_name_in_owner = true
	btn_orbit_l.text = "◀ Gira Izq"
	btn_orbit_l.custom_minimum_size = Vector2(76, 30)
	style_btn.call(btn_orbit_l, Color(0.5, 0.8, 1.0), 14, 6, 3)
	orbit_hbox.add_child(btn_orbit_l)
	btn_orbit_l.owner = root
	
	var orbit_slider = HSlider.new()
	orbit_slider.name = "OrbitSlider"
	orbit_slider.unique_name_in_owner = true
	orbit_slider.min_value = -75.0
	orbit_slider.max_value = 75.0
	orbit_slider.step = 1.0
	orbit_slider.value = 0.0
	orbit_slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	orbit_hbox.add_child(orbit_slider)
	orbit_slider.owner = root
	
	var btn_orbit_r = Button.new()
	btn_orbit_r.name = "BtnOrbitR"
	btn_orbit_r.unique_name_in_owner = true
	btn_orbit_r.text = "Gira Der ▶"
	btn_orbit_r.custom_minimum_size = Vector2(76, 30)
	style_btn.call(btn_orbit_r, Color(0.5, 0.8, 1.0), 14, 6, 3)
	orbit_hbox.add_child(btn_orbit_r)
	btn_orbit_r.owner = root
	
	var lbl_orbit = Label.new()
	lbl_orbit.name = "LblOrbit"
	lbl_orbit.unique_name_in_owner = true
	lbl_orbit.text = "0°"
	lbl_orbit.custom_minimum_size = Vector2(36, 0)
	lbl_orbit.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_orbit.add_theme_font_size_override("font_size", 12)
	lbl_orbit.add_theme_color_override("font_color", Color(0.8, 0.9, 1.0))
	orbit_hbox.add_child(lbl_orbit)
	lbl_orbit.owner = root
	
	# BOTTOM PANEL (Pantys, Skin, Actions)
	var btm_panel = PanelContainer.new()
	btm_panel.name = "BottomPanel"
	btm_panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	btm_panel.offset_left = 16
	btm_panel.offset_top = -242
	btm_panel.offset_right = -16
	btm_panel.offset_bottom = -16
	
	var btm_style = make_glass.call(Color(0.10, 0.08, 0.16, 0.90), Color(1.0, 0.45, 0.75, 0.35), 20, 1, 12, 10)
	btm_panel.add_theme_stylebox_override("panel", btm_style)
	root_ui.add_child(btm_panel)
	btm_panel.owner = root
	
	var btm_vbox = VBoxContainer.new()
	btm_vbox.add_theme_constant_override("separation", 8)
	btm_panel.add_child(btm_vbox)
	btm_vbox.owner = root
	
	# Panty Selection Header
	var panty_title = Label.new()
	panty_title.text = "🍑 LENCERÍA & ESTILO"
	panty_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	panty_title.add_theme_font_size_override("font_size", 13)
	panty_title.add_theme_color_override("font_color", Color(1.0, 0.65, 0.85))
	btm_vbox.add_child(panty_title)
	panty_title.owner = root
	
	var panty_hbox = HBoxContainer.new()
	panty_hbox.alignment = BoxContainer.ALIGNMENT_CENTER
	panty_hbox.add_theme_constant_override("separation", 8)
	btm_vbox.add_child(panty_hbox)
	panty_hbox.owner = root
	
	var btn_panty_thong = Button.new()
	btn_panty_thong.name = "BtnPantyThong"
	btn_panty_thong.unique_name_in_owner = true
	btn_panty_thong.text = "🖤 Tanga Sexy"
	btn_panty_thong.custom_minimum_size = Vector2(0, 38)
	btn_panty_thong.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	btn_panty_thong.toggle_mode = true
	btn_panty_thong.button_pressed = true
	style_btn.call(btn_panty_thong, Color(0.95, 0.30, 0.60), 16, 8, 6)
	panty_hbox.add_child(btn_panty_thong)
	btn_panty_thong.owner = root
	
	var btn_panty_classic = Button.new()
	btn_panty_classic.name = "BtnPantyClassic"
	btn_panty_classic.unique_name_in_owner = true
	btn_panty_classic.text = "🌸 Clásica"
	btn_panty_classic.custom_minimum_size = Vector2(0, 38)
	btn_panty_classic.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	btn_panty_classic.toggle_mode = true
	btn_panty_classic.button_pressed = false
	style_btn.call(btn_panty_classic, Color(0.95, 0.30, 0.60), 16, 8, 6)
	panty_hbox.add_child(btn_panty_classic)
	btn_panty_classic.owner = root
	
	var btn_panty_bare = Button.new()
	btn_panty_bare.name = "BtnPantyBare"
	btn_panty_bare.unique_name_in_owner = true
	btn_panty_bare.text = "✨ Al Natural"
	btn_panty_bare.custom_minimum_size = Vector2(0, 38)
	btn_panty_bare.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	btn_panty_bare.toggle_mode = true
	btn_panty_bare.button_pressed = false
	style_btn.call(btn_panty_bare, Color(0.95, 0.30, 0.60), 16, 8, 6)
	panty_hbox.add_child(btn_panty_bare)
	btn_panty_bare.owner = root
	
	# Skin tone row
	var skin_hbox = HBoxContainer.new()
	skin_hbox.name = "SkinToneContainer"
	skin_hbox.unique_name_in_owner = true
	skin_hbox.alignment = BoxContainer.ALIGNMENT_CENTER
	skin_hbox.add_theme_constant_override("separation", 8)
	btm_vbox.add_child(skin_hbox)
	skin_hbox.owner = root
	
	var tone_defs = [
		{"name": "Clara", "col": Color(0.98, 0.82, 0.74)},
		{"name": "Cálida", "col": Color(0.95, 0.75, 0.65)},
		{"name": "Canela", "col": Color(0.85, 0.62, 0.48)},
		{"name": "Morena", "col": Color(0.68, 0.45, 0.32)}
	]
	for td in tone_defs:
		var tbtn = Button.new()
		tbtn.text = td["name"]
		tbtn.custom_minimum_size = Vector2(0, 30)
		tbtn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		style_btn.call(tbtn, td["col"], 14, 6, 4)
		skin_hbox.add_child(tbtn)
		tbtn.owner = root
	
	# Action buttons row
	var act_hbox = HBoxContainer.new()
	act_hbox.alignment = BoxContainer.ALIGNMENT_CENTER
	act_hbox.add_theme_constant_override("separation", 8)
	btm_vbox.add_child(act_hbox)
	act_hbox.owner = root
	
	var btn_cool = Button.new()
	btn_cool.name = "BtnCool"
	btn_cool.unique_name_in_owner = true
	btn_cool.text = "❄️ Enfriar"
	btn_cool.custom_minimum_size = Vector2(0, 36)
	btn_cool.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	style_btn.call(btn_cool, Color(0.5, 0.85, 1.0), 14, 8, 4)
	act_hbox.add_child(btn_cool)
	btn_cool.owner = root
	
	var btn_sound = Button.new()
	btn_sound.name = "BtnSound"
	btn_sound.unique_name_in_owner = true
	btn_sound.text = "🔊 SFX: ON"
	btn_sound.custom_minimum_size = Vector2(0, 36)
	btn_sound.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	style_btn.call(btn_sound, Color(0.9, 0.7, 1.0), 14, 8, 4)
	act_hbox.add_child(btn_sound)
	btn_sound.owner = root
	
	var btn_music = Button.new()
	btn_music.name = "BtnMusic"
	btn_music.unique_name_in_owner = true
	btn_music.text = "🎵 BGM: ON"
	btn_music.custom_minimum_size = Vector2(0, 36)
	btn_music.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	style_btn.call(btn_music, Color(0.9, 0.7, 1.0), 14, 8, 4)
	act_hbox.add_child(btn_music)
	btn_music.owner = root
	
	var btn_settings_bottom = Button.new()
	btn_settings_bottom.name = "BtnSettingsBottom"
	btn_settings_bottom.unique_name_in_owner = true
	btn_settings_bottom.text = "⚙️ Gráficos"
	btn_settings_bottom.custom_minimum_size = Vector2(0, 36)
	btn_settings_bottom.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	style_btn.call(btn_settings_bottom, Color(1.0, 0.5, 0.75), 14, 8, 4)
	act_hbox.add_child(btn_settings_bottom)
	btn_settings_bottom.owner = root

	# 10. Settings Modal Dialog Overlay
	var settings_overlay = PanelContainer.new()
	settings_overlay.name = "SettingsOverlay"
	settings_overlay.unique_name_in_owner = true
	settings_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	settings_overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	settings_overlay.visible = false
	
	var overlay_style = StyleBoxFlat.new()
	overlay_style.bg_color = Color(0.02, 0.02, 0.05, 0.85)
	settings_overlay.add_theme_stylebox_override("panel", overlay_style)
	root_ui.add_child(settings_overlay)
	settings_overlay.owner = root

	var overlay_center = CenterContainer.new()
	overlay_center.set_anchors_preset(Control.PRESET_FULL_RECT)
	settings_overlay.add_child(overlay_center)
	overlay_center.owner = root

	var settings_card = PanelContainer.new()
	settings_card.name = "SettingsCard"
	settings_card.custom_minimum_size = Vector2(340, 520)
	var card_style = make_glass.call(Color(0.11, 0.09, 0.17, 0.98), Color(1.0, 0.45, 0.75, 0.75), 22, 2, 16, 16)
	settings_card.add_theme_stylebox_override("panel", card_style)
	overlay_center.add_child(settings_card)
	settings_card.owner = root

	var card_vbox = VBoxContainer.new()
	card_vbox.add_theme_constant_override("separation", 10)
	settings_card.add_child(card_vbox)
	card_vbox.owner = root

	# Title
	var dlg_title = Label.new()
	dlg_title.text = "⚙️ AJUSTES GRÁFICOS"
	dlg_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	dlg_title.add_theme_font_size_override("font_size", 19)
	dlg_title.add_theme_color_override("font_color", Color(1.0, 0.60, 0.85))
	card_vbox.add_child(dlg_title)
	dlg_title.owner = root

	var preset_lbl = Label.new()
	preset_lbl.name = "LblPresetStatus"
	preset_lbl.unique_name_in_owner = true
	preset_lbl.text = "PREAJUSTES (SELECCIÓN RÁPIDA):"
	preset_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	preset_lbl.add_theme_font_size_override("font_size", 12)
	preset_lbl.add_theme_color_override("font_color", Color(0.75, 0.85, 1.0))
	card_vbox.add_child(preset_lbl)
	preset_lbl.owner = root

	# Row of Presets
	var preset_grid = GridContainer.new()
	preset_grid.columns = 4
	preset_grid.add_theme_constant_override("h_separation", 6)
	preset_grid.add_theme_constant_override("v_separation", 6)
	card_vbox.add_child(preset_grid)
	preset_grid.owner = root

	var preset_defs = [
		{"name": "BtnPresetBaja", "text": "Baja"},
		{"name": "BtnPresetMedia", "text": "Media"},
		{"name": "BtnPresetAlta", "text": "Alta"},
		{"name": "BtnPresetUltra", "text": "Ultra"}
	]
	for p in preset_defs:
		var pbtn = Button.new()
		pbtn.name = p["name"]
		pbtn.unique_name_in_owner = true
		pbtn.text = p["text"]
		pbtn.custom_minimum_size = Vector2(70, 36)
		pbtn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		style_btn.call(pbtn, Color(0.7, 0.85, 1.0), 14, 4, 4)
		preset_grid.add_child(pbtn)
		pbtn.owner = root

	# Separator
	var hsep = HSeparator.new()
	card_vbox.add_child(hsep)
	hsep.owner = root

	var granular_lbl = Label.new()
	granular_lbl.text = "AJUSTES AVANZADOS (TOCA PARA CAMBIAR):"
	granular_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	granular_lbl.add_theme_font_size_override("font_size", 12)
	granular_lbl.add_theme_color_override("font_color", Color(0.75, 0.85, 1.0))
	card_vbox.add_child(granular_lbl)
	granular_lbl.owner = root

	# Granular options buttons
	var opt_shadows = Button.new()
	opt_shadows.name = "BtnOptShadows"
	opt_shadows.unique_name_in_owner = true
	opt_shadows.text = "⛅ Sombras: SUAVES (Media)"
	opt_shadows.custom_minimum_size = Vector2(0, 36)
	style_btn.call(opt_shadows, Color(0.8, 0.6, 0.9), 14, 10, 4)
	card_vbox.add_child(opt_shadows)
	opt_shadows.owner = root

	var opt_msaa = Button.new()
	opt_msaa.name = "BtnOptMSAA"
	opt_msaa.unique_name_in_owner = true
	opt_msaa.text = "📐 Antialiasing (MSAA): 2X"
	opt_msaa.custom_minimum_size = Vector2(0, 36)
	style_btn.call(opt_msaa, Color(0.8, 0.6, 0.9), 14, 10, 4)
	card_vbox.add_child(opt_msaa)
	opt_msaa.owner = root

	var opt_glow = Button.new()
	opt_glow.name = "BtnOptGlow"
	opt_glow.unique_name_in_owner = true
	opt_glow.text = "✨ Brillo Bloom / Glow: SÍ"
	opt_glow.custom_minimum_size = Vector2(0, 36)
	style_btn.call(opt_glow, Color(0.8, 0.6, 0.9), 14, 10, 4)
	card_vbox.add_child(opt_glow)
	opt_glow.owner = root

	var opt_sss = Button.new()
	opt_sss.name = "BtnOptSSS"
	opt_sss.unique_name_in_owner = true
	opt_sss.text = "🍑 Piel SSS y Poros HD: ACTIVADO"
	opt_sss.custom_minimum_size = Vector2(0, 36)
	style_btn.call(opt_sss, Color(0.8, 0.6, 0.9), 14, 10, 4)
	card_vbox.add_child(opt_sss)
	opt_sss.owner = root

	var opt_scale = Button.new()
	opt_scale.name = "BtnOptScale"
	opt_scale.unique_name_in_owner = true
	opt_scale.text = "📱 Resolución 3D: 100% Nativa"
	opt_scale.custom_minimum_size = Vector2(0, 36)
	style_btn.call(opt_scale, Color(0.8, 0.6, 0.9), 14, 10, 4)
	card_vbox.add_child(opt_scale)
	opt_scale.owner = root

	var opt_fps = Button.new()
	opt_fps.name = "BtnOptFPS"
	opt_fps.unique_name_in_owner = true
	opt_fps.text = "🚀 Límite FPS: 60 FPS"
	opt_fps.custom_minimum_size = Vector2(0, 36)
	style_btn.call(opt_fps, Color(0.8, 0.6, 0.9), 14, 10, 4)
	card_vbox.add_child(opt_fps)
	opt_fps.owner = root

	# Separator
	var hsep2 = HSeparator.new()
	card_vbox.add_child(hsep2)
	hsep2.owner = root

	# Close / Confirm Button
	var btn_close = Button.new()
	btn_close.name = "BtnCloseSettings"
	btn_close.unique_name_in_owner = true
	btn_close.text = "✅ Guardar y Volver"
	btn_close.custom_minimum_size = Vector2(0, 42)
	btn_close.add_theme_font_size_override("font_size", 15)
	style_btn.call(btn_close, Color(0.3, 0.95, 0.6), 16, 12, 6)
	card_vbox.add_child(btn_close)
	btn_close.owner = root

	var packed = PackedScene.new()
	var err = packed.pack(root)
	if err == OK:
		var save_err = ResourceSaver.save(packed, "res://scenes/main.tscn")
		print("main.tscn saved successfully!")
	else:
		print("Packing error:", err)
		
	quit()

func _set_owner_recursive(node: Node, new_owner: Node):
	for child in node.get_children():
		child.owner = new_owner
		_set_owner_recursive(child, new_owner)
