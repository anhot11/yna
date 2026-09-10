extends Node3D

@onready var cam_rig: Node3D = $CameraRig
@onready var character: Node3D = $Character
@onready var slap_hand: Node3D = $SlapHand
@onready var sound_mgr: Node = $SoundManager
@onready var fx_mgr: Node = $FXManager
@onready var gfx_mgr: Node = $GraphicsManager

# UI Elements
@onready var lbl_total: Label = %LblTotal
@onready var lbl_combo: Label = %LblCombo
@onready var lbl_speed: Label = %LblSpeed
@onready var lbl_rank: Label = %LblRank
@onready var combo_bar: ProgressBar = %ComboBar

# Interaction Mode
enum Mode { SLAP, ROTATE }
var current_mode: Mode = Mode.SLAP
@onready var btn_mode: Button = %BtnMode

# Camera Controls UI
@onready var btn_zoom_out: Button = %BtnZoomOut
@onready var btn_zoom_in: Button = %BtnZoomIn
@onready var zoom_slider: HSlider = %ZoomSlider
@onready var btn_orbit_l: Button = %BtnOrbitL
@onready var btn_orbit_r: Button = %BtnOrbitR
@onready var orbit_slider: HSlider = %OrbitSlider
@onready var lbl_orbit: Label = %LblOrbit
@onready var btn_reset_cam: Button = %BtnResetCam

# Cinema & Layout Panels
@onready var top_panel: PanelContainer = find_child("TopPanel", true, false)
@onready var cam_panel: PanelContainer = find_child("CameraControlPanel", true, false)
@onready var btm_panel: PanelContainer = find_child("BottomPanel", true, false)
@onready var btn_cinema: Button = %BtnCinema
@onready var btn_restore_ui: Button = %BtnRestoreUI

# Bottom UI
@onready var btn_panty_classic: Button = %BtnPantyClassic
@onready var btn_panty_thong: Button = %BtnPantyThong
@onready var btn_panty_bare: Button = %BtnPantyBare
@onready var btn_cool: Button = %BtnCool
@onready var btn_sound: Button = %BtnSound
@onready var btn_music: Button = %BtnMusic

# Settings UI
@onready var btn_settings_top: Button = %BtnSettingsTop
@onready var btn_settings_bottom: Button = %BtnSettingsBottom
@onready var settings_overlay: PanelContainer = %SettingsOverlay
@onready var lbl_preset_status: Label = %LblPresetStatus

@onready var btn_preset_baja: Button = %BtnPresetBaja
@onready var btn_preset_media: Button = %BtnPresetMedia
@onready var btn_preset_alta: Button = %BtnPresetAlta
@onready var btn_preset_ultra: Button = %BtnPresetUltra

@onready var btn_opt_shadows: Button = %BtnOptShadows
@onready var btn_opt_msaa: Button = %BtnOptMSAA
@onready var btn_opt_glow: Button = %BtnOptGlow
@onready var btn_opt_sss: Button = %BtnOptSSS
@onready var btn_opt_scale: Button = %BtnOptScale
@onready var btn_opt_fps: Button = %BtnOptFPS

@onready var btn_close_settings: Button = %BtnCloseSettings

@onready var touch_area: Control = %TouchArea
@onready var ui_canvas: CanvasLayer = $CanvasLayer

# Gameplay State
var total_slaps: int = 0
var current_combo: int = 0
var max_combo: int = 0
var combo_timer: float = 0.0
var combo_max_time: float = 2.2

# Touch & Gesture Tracking
var active_touches: Dictionary = {}
var prev_pinch_dist: float = -1.0
var touch_start_pos: Vector2 = Vector2.ZERO
var touch_last_pos: Vector2 = Vector2.ZERO
var touch_prev_pos: Vector2 = Vector2.ZERO
var touch_start_time: float = 0.0
var touch_prev_time: float = 0.0
var is_dragging: bool = false
var is_touching_edge: bool = false

func _ready() -> void:
	_resolve_nodes()
	_setup_ui_events()
	_update_stats_ui(0.0)

func _resolve_nodes() -> void:
	if not cam_rig: cam_rig = find_child("CameraRig", true, false)
	if not character: character = find_child("Character", true, false)
	if not slap_hand: slap_hand = find_child("SlapHand", true, false)
	if not sound_mgr: sound_mgr = find_child("SoundManager", true, false)
	if not fx_mgr: fx_mgr = find_child("FXManager", true, false)
	if not gfx_mgr: gfx_mgr = find_child("GraphicsManager", true, false)
	if not touch_area: touch_area = find_child("TouchArea", true, false)
	if not ui_canvas: ui_canvas = find_child("CanvasLayer", true, false)
	if not lbl_total: lbl_total = find_child("LblTotal", true, false)
	if not lbl_combo: lbl_combo = find_child("LblCombo", true, false)
	if not lbl_speed: lbl_speed = find_child("LblSpeed", true, false)
	if not lbl_rank: lbl_rank = find_child("LblRank", true, false)
	if not combo_bar: combo_bar = find_child("ComboBar", true, false)
	
	if not btn_mode: btn_mode = find_child("BtnMode", true, false)
	if not btn_zoom_out: btn_zoom_out = find_child("BtnZoomOut", true, false)
	if not btn_zoom_in: btn_zoom_in = find_child("BtnZoomIn", true, false)
	if not zoom_slider: zoom_slider = find_child("ZoomSlider", true, false)
	if not btn_orbit_l: btn_orbit_l = find_child("BtnOrbitL", true, false)
	if not btn_orbit_r: btn_orbit_r = find_child("BtnOrbitR", true, false)
	if not orbit_slider: orbit_slider = find_child("OrbitSlider", true, false)
	if not lbl_orbit: lbl_orbit = find_child("LblOrbit", true, false)
	if not btn_reset_cam: btn_reset_cam = find_child("BtnResetCam", true, false)

	if not top_panel: top_panel = find_child("TopPanel", true, false)
	if not cam_panel: cam_panel = find_child("CameraControlPanel", true, false)
	if not btm_panel: btm_panel = find_child("BottomPanel", true, false)
	if not btn_cinema: btn_cinema = find_child("BtnCinema", true, false)
	if not btn_restore_ui: btn_restore_ui = find_child("BtnRestoreUI", true, false)

	if not btn_panty_classic: btn_panty_classic = find_child("BtnPantyClassic", true, false)
	if not btn_panty_thong: btn_panty_thong = find_child("BtnPantyThong", true, false)
	if not btn_panty_bare: btn_panty_bare = find_child("BtnPantyBare", true, false)
	if not btn_cool: btn_cool = find_child("BtnCool", true, false)
	if not btn_sound: btn_sound = find_child("BtnSound", true, false)
	if not btn_music: btn_music = find_child("BtnMusic", true, false)

	if not btn_settings_top: btn_settings_top = find_child("BtnSettingsTop", true, false)
	if not btn_settings_bottom: btn_settings_bottom = find_child("BtnSettingsBottom", true, false)
	if not settings_overlay: settings_overlay = find_child("SettingsOverlay", true, false)
	if not lbl_preset_status: lbl_preset_status = find_child("LblPresetStatus", true, false)
	
	if not btn_preset_baja: btn_preset_baja = find_child("BtnPresetBaja", true, false)
	if not btn_preset_media: btn_preset_media = find_child("BtnPresetMedia", true, false)
	if not btn_preset_alta: btn_preset_alta = find_child("BtnPresetAlta", true, false)
	if not btn_preset_ultra: btn_preset_ultra = find_child("BtnPresetUltra", true, false)
	
	if not btn_opt_shadows: btn_opt_shadows = find_child("BtnOptShadows", true, false)
	if not btn_opt_msaa: btn_opt_msaa = find_child("BtnOptMSAA", true, false)
	if not btn_opt_glow: btn_opt_glow = find_child("BtnOptGlow", true, false)
	if not btn_opt_sss: btn_opt_sss = find_child("BtnOptSSS", true, false)
	if not btn_opt_scale: btn_opt_scale = find_child("BtnOptScale", true, false)
	if not btn_opt_fps: btn_opt_fps = find_child("BtnOptFPS", true, false)
	if not btn_close_settings: btn_close_settings = find_child("BtnCloseSettings", true, false)

func _setup_ui_events() -> void:
	if touch_area:
		touch_area.gui_input.connect(_on_touch_area_input)
	
	# Interaction Mode Switcher
	if btn_mode:
		btn_mode.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if current_mode == Mode.SLAP:
				current_mode = Mode.ROTATE
				btn_mode.button_pressed = true
				btn_mode.text = "🔄 Girar 3D"
			else:
				current_mode = Mode.SLAP
				btn_mode.button_pressed = false
				btn_mode.text = "👋 Nalgada"
		)

	# Camera Controls
	if btn_zoom_out:
		btn_zoom_out.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if cam_rig:
				cam_rig.call("zoom_step", -0.35)
				if zoom_slider: zoom_slider.value = cam_rig.call("get_zoom_ratio")
		)
		
	if btn_zoom_in:
		btn_zoom_in.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if cam_rig:
				cam_rig.call("zoom_step", 0.35)
				if zoom_slider: zoom_slider.value = cam_rig.call("get_zoom_ratio")
		)
		
	if zoom_slider:
		zoom_slider.value_changed.connect(func(v: float):
			if cam_rig: cam_rig.call("set_zoom_ratio", v)
		)
		
	# Native Direction: Left button turns model to Left (+15 yaw)
	if btn_orbit_l:
		btn_orbit_l.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if cam_rig:
				cam_rig.call("orbit_step", 15.0)
				if orbit_slider: orbit_slider.set_value_no_signal(-cam_rig.call("get_yaw"))
		)
		
	# Native Direction: Right button turns model to Right (-15 yaw)
	if btn_orbit_r:
		btn_orbit_r.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if cam_rig:
				cam_rig.call("orbit_step", -15.0)
				if orbit_slider: orbit_slider.set_value_no_signal(-cam_rig.call("get_yaw"))
		)

	if orbit_slider:
		orbit_slider.value_changed.connect(func(v: float):
			if cam_rig: cam_rig.call("set_yaw", -v)
		)
		
	if btn_reset_cam:
		btn_reset_cam.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if cam_rig:
				cam_rig.call("reset_view")
				if zoom_slider: zoom_slider.value = cam_rig.call("get_zoom_ratio")
				if orbit_slider: orbit_slider.set_value_no_signal(0.0)
		)
	
	# Cinema Mode
	if btn_cinema:
		btn_cinema.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			_set_cinema_mode(true)
		)
	if btn_restore_ui:
		btn_restore_ui.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			_set_cinema_mode(false)
		)

	# Panty Buttons (0: Classic, 1: Thong, 2: Bare)
	if btn_panty_thong:
		btn_panty_thong.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			_select_panty(1)
		)
	if btn_panty_classic:
		btn_panty_classic.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			_select_panty(0)
		)
	if btn_panty_bare:
		btn_panty_bare.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			_select_panty(2)
		)
	
	if btn_cool:
		btn_cool.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if character: character.call("reset_redness")
			var vp_size = touch_area.size if touch_area else Vector2(720, 1280)
			if fx_mgr and ui_canvas:
				fx_mgr.call("spawn_floating_text", ui_canvas, vp_size * 0.5, 0.5)
		)
	
	if btn_sound:
		btn_sound.pressed.connect(func():
			if sound_mgr:
				var muted = sound_mgr.call("toggle_sound")
				btn_sound.text = "🔇 Mute" if muted else "🔊 SFX: ON"
				sound_mgr.call("play_click")
		)
	
	if btn_music:
		btn_music.pressed.connect(func():
			if sound_mgr:
				var muted = sound_mgr.call("toggle_music")
				btn_music.text = "🔇 BGM: OFF" if muted else "🎵 BGM: ON"
				sound_mgr.call("play_click")
		)
	
	var tone_container = find_child("SkinToneContainer", true, false)
	if tone_container:
		var colors = [
			Color(0.98, 0.82, 0.74, 1.0),
			Color(0.95, 0.75, 0.65, 1.0),
			Color(0.85, 0.62, 0.48, 1.0),
			Color(0.68, 0.45, 0.32, 1.0)
		]
		for i in range(min(colors.size(), tone_container.get_child_count())):
			var btn: Button = tone_container.get_child(i)
			var col = colors[i]
			btn.pressed.connect(func():
				if sound_mgr: sound_mgr.call("play_click")
				if character: character.call("set_skin_tone", col)
			)

	# Settings Button Triggers
	if btn_settings_top:
		btn_settings_top.pressed.connect(_open_settings)
	if btn_settings_bottom:
		btn_settings_bottom.pressed.connect(_open_settings)
	if btn_close_settings:
		btn_close_settings.pressed.connect(_close_settings)

	# Presets
	if btn_preset_baja:
		btn_preset_baja.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if gfx_mgr: gfx_mgr.call("set_preset", "Baja")
			_refresh_settings_ui()
		)
	if btn_preset_media:
		btn_preset_media.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if gfx_mgr: gfx_mgr.call("set_preset", "Media")
			_refresh_settings_ui()
		)
	if btn_preset_alta:
		btn_preset_alta.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if gfx_mgr: gfx_mgr.call("set_preset", "Alta")
			_refresh_settings_ui()
		)
	if btn_preset_ultra:
		btn_preset_ultra.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if gfx_mgr: gfx_mgr.call("set_preset", "Ultra")
			_refresh_settings_ui()
		)

	# Granular Controls
	if btn_opt_shadows:
		btn_opt_shadows.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if gfx_mgr: gfx_mgr.call("cycle_shadows")
			_refresh_settings_ui()
		)
	if btn_opt_msaa:
		btn_opt_msaa.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if gfx_mgr: gfx_mgr.call("cycle_msaa")
			_refresh_settings_ui()
		)
	if btn_opt_glow:
		btn_opt_glow.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if gfx_mgr: gfx_mgr.call("toggle_glow")
			_refresh_settings_ui()
		)
	if btn_opt_sss:
		btn_opt_sss.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if gfx_mgr: gfx_mgr.call("toggle_sss")
			_refresh_settings_ui()
		)
	if btn_opt_scale:
		btn_opt_scale.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if gfx_mgr: gfx_mgr.call("toggle_resolution_scale")
			_refresh_settings_ui()
		)
	if btn_opt_fps:
		btn_opt_fps.pressed.connect(func():
			if sound_mgr: sound_mgr.call("play_click")
			if gfx_mgr: gfx_mgr.call("cycle_fps")
			_refresh_settings_ui()
		)

func _open_settings() -> void:
	if sound_mgr: sound_mgr.call("play_click")
	if settings_overlay:
		settings_overlay.visible = true
	_refresh_settings_ui()

func _close_settings() -> void:
	if sound_mgr: sound_mgr.call("play_click")
	if settings_overlay:
		settings_overlay.visible = false

func _refresh_settings_ui() -> void:
	if not gfx_mgr: return
	if lbl_preset_status:
		var cur_preset = gfx_mgr.get("preset")
		lbl_preset_status.text = "PREAJUSTES (ACTUAL: %s):" % str(cur_preset).to_upper()
	if btn_opt_shadows:
		btn_opt_shadows.text = gfx_mgr.call("get_shadows_label")
	if btn_opt_msaa:
		btn_opt_msaa.text = gfx_mgr.call("get_msaa_label")
	if btn_opt_glow:
		btn_opt_glow.text = gfx_mgr.call("get_glow_label")
	if btn_opt_sss:
		btn_opt_sss.text = gfx_mgr.call("get_sss_label")
	if btn_opt_scale:
		btn_opt_scale.text = gfx_mgr.call("get_scale_label")
	if btn_opt_fps:
		btn_opt_fps.text = gfx_mgr.call("get_fps_label")

func _select_panty(idx: int) -> void:
	if character:
		character.call("set_panty", idx)
	if btn_panty_thong:
		btn_panty_thong.button_pressed = (idx == 1)
	if btn_panty_classic:
		btn_panty_classic.button_pressed = (idx == 0)
	if btn_panty_bare:
		btn_panty_bare.button_pressed = (idx == 2)

func _set_cinema_mode(enabled: bool) -> void:
	if top_panel:
		top_panel.visible = not enabled
	if cam_panel:
		cam_panel.visible = not enabled
	if btm_panel:
		btm_panel.visible = not enabled
	if btn_restore_ui:
		btn_restore_ui.visible = enabled

func _process(delta: float) -> void:
	if cam_rig:
		var yaw = cam_rig.call("get_yaw")
		if lbl_orbit:
			lbl_orbit.text = "%d°" % int(round(-yaw))
		if orbit_slider and not orbit_slider.has_focus():
			orbit_slider.set_value_no_signal(-yaw)

	if current_combo > 0:
		combo_timer -= delta
		if combo_bar:
			combo_bar.value = (combo_timer / combo_max_time) * 100.0
		if combo_timer <= 0.0:
			current_combo = 0
			_update_combo_ui()
	else:
		if combo_bar:
			combo_bar.value = 0.0

func _calc_touch_world_pos(screen_pos: Vector2) -> Dictionary:
	var vp_w = touch_area.size.x if touch_area else 720.0
	var vp_h = touch_area.size.y if touch_area else 1280.0
	var center_x = vp_w * 0.5
	var rel_x = (screen_pos.x - center_x) / center_x
	var is_left = rel_x < 0.0
	var target_x = clamp(rel_x * 0.18, -0.16, 0.16)
	var rel_y = (screen_pos.y - vp_h * 0.5) / (vp_h * 0.5)
	var target_y = clamp(0.82 - rel_y * 0.15, 0.70, 0.94)
	var target_z = 0.09
	return {
		"is_left": is_left,
		"world_pos": Vector3(target_x, target_y, target_z)
	}

func _handle_touch_press(pos: Vector2, now: float) -> void:
	touch_start_pos = pos
	touch_last_pos = pos
	touch_prev_pos = pos
	touch_start_time = now
	touch_prev_time = now
	is_dragging = true
	var vp_w = touch_area.size.x if touch_area else 720.0
	
	if current_mode == Mode.ROTATE:
		if cam_rig: cam_rig.call("set_orbit_velocity", Vector2.ZERO)
	else:
		is_touching_edge = (pos.x < 70.0 or pos.x > vp_w - 70.0)
		if not is_touching_edge:
			var info = _calc_touch_world_pos(pos)
			if character:
				character.call("start_touch", info.world_pos, info.is_left)
			if sound_mgr:
				sound_mgr.call("play_sfx", sound_mgr.get("slap_light_stream"), -12.0, 0.15)
			Input.vibrate_handheld(12)

func _handle_touch_drag(pos: Vector2, relative: Vector2, now: float) -> void:
	if not is_dragging:
		return
	if current_mode == Mode.ROTATE or is_touching_edge:
		if cam_rig:
			cam_rig.call("add_orbit_drag", - relative.x * 0.28, relative.y * 0.20)
	else:
		var drag_delta = pos - touch_start_pos
		if character:
			character.call("update_touch_drag", drag_delta)
	touch_prev_pos = touch_last_pos
	touch_prev_time = now
	touch_last_pos = pos

func _handle_touch_release(now: float) -> void:
	if not is_dragging:
		return
	is_dragging = false
	if current_mode == Mode.ROTATE or is_touching_edge:
		var dt = max(0.016, now - touch_prev_time)
		var delta_x = touch_last_pos.x - touch_prev_pos.x
		var delta_y = touch_last_pos.y - touch_prev_pos.y
		var vel_x = - (delta_x / dt) * 0.28
		var vel_y = (delta_y / dt) * 0.20
		if cam_rig:
			cam_rig.call("set_orbit_velocity", Vector2(clamp(vel_x, -280.0, 280.0), clamp(vel_y, -160.0, 160.0)))
	else:
		var duration = max(0.02, now - touch_start_time)
		var delta_pos = touch_last_pos - touch_start_pos
		var dist = delta_pos.length()
		var speed = dist / duration
		
		# Quick tap or fast swipe triggers slap
		if duration < 0.40 or speed > 90.0 or dist < 25.0:
			var force: float = 0.0
			if dist < 25.0:
				force = randf_range(420.0, 680.0)
			else:
				force = clamp(speed * 0.52, 380.0, 1950.0)
			_execute_slap(touch_last_pos, delta_pos.normalized(), force)
		else:
			# Slow drag released: snap-back elastic bounce
			if character:
				character.call("end_touch", false)

func _on_touch_area_input(event: InputEvent) -> void:
	if settings_overlay and settings_overlay.visible:
		return
	var now = Time.get_ticks_msec() / 1000.0
	
	# Handle screen touch
	if event is InputEventScreenTouch:
		if event.pressed:
			active_touches[event.index] = event.position
			if active_touches.size() == 1:
				_handle_touch_press(event.position, now)
			elif active_touches.size() == 2:
				is_dragging = false
				var p0 = active_touches.values()[0]
				var p1 = active_touches.values()[1]
				prev_pinch_dist = p0.distance_to(p1)
		else:
			active_touches.erase(event.index)
			if active_touches.size() < 2:
				prev_pinch_dist = -1.0
				
			if is_dragging and active_touches.size() == 0:
				_handle_touch_release(now)

	# Handle screen drag
	elif event is InputEventScreenDrag:
		active_touches[event.index] = event.position
		
		# Two finger gesture: Pinch-to-zoom and two-finger orbit
		if active_touches.size() >= 2:
			is_dragging = false
			var keys = active_touches.keys()
			var p0 = active_touches[keys[0]]
			var p1 = active_touches[keys[1]]
			var cur_dist = p0.distance_to(p1)
			
			if prev_pinch_dist > 0.0 and cam_rig:
				var pinch_delta = cur_dist - prev_pinch_dist
				cam_rig.call("zoom_step", pinch_delta * 0.005)
				cam_rig.call("orbit_step", - event.relative.x * 0.22, event.relative.y * 0.18)
				if zoom_slider: zoom_slider.value = cam_rig.call("get_zoom_ratio")
				
			prev_pinch_dist = cur_dist
		else:
			_handle_touch_drag(event.position, event.relative, now)

	# Handle desktop mouse emulation
	elif event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				_handle_touch_press(event.position, now)
			else:
				_handle_touch_release(now)
					
		elif event.button_index == MOUSE_BUTTON_WHEEL_UP:
			if cam_rig:
				cam_rig.call("zoom_step", 0.15)
				if zoom_slider: zoom_slider.value = cam_rig.call("get_zoom_ratio")
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			if cam_rig:
				cam_rig.call("zoom_step", -0.15)
				if zoom_slider: zoom_slider.value = cam_rig.call("get_zoom_ratio")

	elif event is InputEventMouseMotion:
		_handle_touch_drag(event.position, event.relative, now)

func _execute_slap(screen_pos: Vector2, swipe_dir_2d: Vector2, force: float) -> void:
	_resolve_nodes()
	total_slaps += 1
	current_combo += 1
	if current_combo > max_combo:
		max_combo = current_combo
	combo_timer = combo_max_time
	
	var info = _calc_touch_world_pos(screen_pos)
	var is_left = info.is_left
	var impact_world_pos = info.world_pos
	
	var norm_force = force / 700.0
	
	# 1. 3D Slap Hand Animation
	if slap_hand:
		slap_hand.call("play_slap_anim", impact_world_pos, swipe_dir_2d, norm_force)
	
	# 2. Incredible Character Jiggle & Blush
	if character:
		character.call("apply_slap", is_left, norm_force, swipe_dir_2d)
	
	# 3. Audio
	if sound_mgr:
		sound_mgr.call("play_slap", force)
	
	# 4. Haptic vibration
	var vib_ms = int(clamp(norm_force * 40.0, 25.0, 100.0))
	Input.vibrate_handheld(vib_ms)
	
	# 5. Subtle micro-sheen on heavy impact
	if fx_mgr:
		fx_mgr.call("spawn_hit_particles", self, impact_world_pos, norm_force)
	
	# 6. Floating Text (on combos or hard hits)
	if fx_mgr and ui_canvas and (current_combo >= 3 or norm_force > 1.2):
		fx_mgr.call("spawn_floating_text", ui_canvas, screen_pos, norm_force)
	
	# 7. Camera trauma
	if cam_rig:
		cam_rig.call("add_trauma", norm_force * 0.20)
	
	# 8. Update UI
	_update_stats_ui(force)

func _update_stats_ui(force: float) -> void:
	if lbl_total: lbl_total.text = "NALGADAS: %d" % total_slaps
	var speed_kmh = int(force * 0.075)
	if lbl_speed: lbl_speed.text = "FUERZA: %d km/h" % speed_kmh
	_update_combo_ui()
	_update_rank_ui()

func _update_combo_ui() -> void:
	if not lbl_combo: return
	if current_combo > 1:
		lbl_combo.text = "COMBO x%d 🔥" % current_combo
		lbl_combo.modulate = Color(1.0, 0.3 + min(0.7, current_combo * 0.05), 0.2)
	else:
		lbl_combo.text = "COMBO: x1"
		lbl_combo.modulate = Color(1.0, 1.0, 1.0)

func _update_rank_ui() -> void:
	if not lbl_rank: return
	var rank = "Novato 👋"
	if total_slaps >= 200:
		rank = "¡DIOS DEL SPANK! 👑"
	elif total_slaps >= 100:
		rank = "Maestro Supremo 💥"
	elif total_slaps >= 50:
		rank = "Nalgueador Pro ⚡"
	elif total_slaps >= 20:
		rank = "Entusiasta 😏"
	elif total_slaps >= 5:
		rank = "Aficionado 🍑"
	lbl_rank.text = "RANGO: " + rank
