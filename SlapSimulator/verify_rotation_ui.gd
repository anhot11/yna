extends SceneTree

func _init():
	print('--- STARTING ROTATION & MODERN UI VERIFICATION ---')
	var scene = load('res://scenes/main.tscn')
	if not scene:
		print('FAILED to load main.tscn')
		quit(1)
		return
	var inst = scene.instantiate()
	root.add_child(inst)
	
	await process_frame
	await process_frame
	
	var cam_rig = inst.find_child('CameraRig', true, false)
	var btn_mode = inst.find_child('BtnMode', true, false)
	var btn_orbit_l = inst.find_child('BtnOrbitL', true, false)
	var btn_orbit_r = inst.find_child('BtnOrbitR', true, false)
	var orbit_slider = inst.find_child('OrbitSlider', true, false)
	var lbl_orbit = inst.find_child('LblOrbit', true, false)
	var btn_reset = inst.find_child('BtnResetCam', true, false)
	
	assert(cam_rig != null, 'CameraRig missing')
	assert(btn_mode != null, 'BtnMode missing')
	assert(btn_orbit_l != null, 'BtnOrbitL missing')
	assert(btn_orbit_r != null, 'BtnOrbitR missing')
	assert(orbit_slider != null, 'OrbitSlider missing')
	assert(lbl_orbit != null, 'LblOrbit missing')
	assert(btn_reset != null, 'BtnResetCam missing')
	print('All new camera & mode nodes found (PASS)')
	
	# 1. Verify modern button styles exist on buttons
	var style_normal = btn_orbit_l.get_theme_stylebox('normal')
	assert(style_normal is StyleBoxFlat, 'Button normal style should be StyleBoxFlat')
	assert(style_normal.corner_radius_top_left > 0, 'Button should have rounded corners')
	print('Modern glassmorphism button style: PASS')
	
	# 2. Test initial view
	btn_reset.emit_signal('pressed')
	await process_frame
	assert(abs(cam_rig.get_yaw()) < 0.1, 'Initial yaw should be 0')
	print('Initial Camera Yaw: 0° (PASS)')
	
	# 3. Test BtnOrbitL (should rotate camera right -> character turns LEFT)
	btn_orbit_l.emit_signal('pressed')
	await process_frame
	var yaw_after_l = cam_rig.get_yaw()
	assert(yaw_after_l > 5.0, 'BtnOrbitL must increase yaw to turn model left (got %f)' % yaw_after_l)
	print('BtnOrbitL direction (turns model left): PASS (Yaw = +%f°)' % yaw_after_l)
	
	# 4. Test BtnOrbitR (should rotate camera left -> character turns RIGHT)
	btn_reset.emit_signal('pressed')
	await process_frame
	btn_orbit_r.emit_signal('pressed')
	await process_frame
	var yaw_after_r = cam_rig.get_yaw()
	assert(yaw_after_r < -5.0, 'BtnOrbitR must decrease yaw to turn model right (got %f)' % yaw_after_r)
	print('BtnOrbitR direction (turns model right): PASS (Yaw = %f°)' % yaw_after_r)
	
	# 5. Test OrbitSlider direct turntable control
	orbit_slider.value = 30.0
	orbit_slider.emit_signal('value_changed', 30.0)
	await process_frame
	assert(abs(cam_rig.get_yaw() - (-30.0)) < 0.1, 'OrbitSlider 30° should set yaw to -30°')
	print('OrbitSlider Turntable Control: PASS')
	
	# 6. Test Mode Switcher
	assert(inst.current_mode == inst.Mode.SLAP, 'Initial mode should be SLAP')
	btn_mode.emit_signal('pressed')
	assert(inst.current_mode == inst.Mode.ROTATE, 'Mode after toggle should be ROTATE')
	print('Mode Switcher to ROTATE: PASS')
	btn_mode.emit_signal('pressed')
	assert(inst.current_mode == inst.Mode.SLAP, 'Mode after second toggle should be SLAP')
	print('Mode Switcher back to SLAP: PASS')
	
	# 7. Test Camera Inertia
	cam_rig.set_orbit_velocity(Vector2(50.0, 0.0))
	await process_frame
	await process_frame
	assert(cam_rig.orbit_velocity.x < 50.0, 'Inertia must damp over time')
	print('Camera Inertia & Friction Damping: PASS')
	
	# 8. Reset View
	btn_reset.emit_signal('pressed')
	await process_frame
	assert(abs(cam_rig.get_yaw()) < 0.1, 'Yaw after reset should be 0')
	print('Camera Reset: PASS')
	
	print('====================================================')
	print('ALL ROTATION & MODERN UI CHECKS PASSED 100%!')
	print('====================================================')
	quit(0)
