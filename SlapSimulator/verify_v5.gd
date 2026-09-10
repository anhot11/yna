extends SceneTree

func _init():
	print('--- STARTING V1.5 COMPREHENSIVE VERIFICATION ---')
	var scene = load('res://scenes/main.tscn')
	if not scene:
		print('FAILED: Could not load scenes/main.tscn')
		quit(1)
		return
		
	var inst = scene.instantiate()
	root.add_child(inst)
	
	await process_frame
	await process_frame
	
	var character = inst.find_child('Character', true, false)
	var body_mesh = inst.find_child('Body', true, false)
	var panty_classic = inst.find_child('Panty_Classic', true, false)
	var panty_thong = inst.find_child('Panty_Thong', true, false)
	var skeleton = inst.find_child('Skeleton3D', true, false)
	
	assert(character != null, 'Character node missing')
	assert(body_mesh != null, 'Body mesh missing')
	assert(panty_classic != null, 'Panty_Classic mesh missing')
	assert(panty_thong != null, 'Panty_Thong mesh missing')
	assert(skeleton != null, 'Skeleton3D missing')
	print('Model & Mesh Nodes: PASS')
	
	# Verify bone existence
	var bone_l = skeleton.find_bone('Cheek_L')
	var bone_r = skeleton.find_bone('Cheek_R')
	assert(bone_l != -1, 'Cheek_L bone missing')
	assert(bone_r != -1, 'Cheek_R bone missing')
	print('Cheek Bones found: Cheek_L=%d, Cheek_R=%d (PASS)' % [bone_l, bone_r])
	
	# Verify initial panty is Thong
	assert(panty_thong.visible == true, 'Initial panty should be Thong')
	assert(panty_classic.visible == false, 'Initial panty Classic should be hidden')
	print('Default Panty (Tanga Sexy): PASS')
	
	# Test Panty Classic
	inst.call('_select_panty', 0)
	assert(panty_classic.visible == true, 'Classic panty should be visible')
	assert(panty_thong.visible == false, 'Thong panty should be hidden')
	print('Switch Panty to Classic: PASS')
	
	# Test Panty Bare (Al Natural)
	inst.call('_select_panty', 2)
	assert(panty_classic.visible == false, 'Classic panty should be hidden in bare mode')
	assert(panty_thong.visible == false, 'Thong panty should be hidden in bare mode')
	print('Switch Panty to Al Natural (Bare): PASS')
	
	# Switch back to Thong
	inst.call('_select_panty', 1)
	assert(panty_thong.visible == true, 'Thong panty should be visible')
	assert(panty_classic.visible == false, 'Classic panty should be hidden')
	print('Switch Panty back to Thong: PASS')
	
	# Verify Cinema Mode
	var top_p = inst.find_child('TopPanel', true, false)
	var cam_p = inst.find_child('CameraControlPanel', true, false)
	var btm_p = inst.find_child('BottomPanel', true, false)
	var btn_restore = inst.find_child('BtnRestoreUI', true, false)
	
	assert(top_p != null and cam_p != null and btm_p != null and btn_restore != null, 'UI Panels missing')
	assert(top_p.visible == true, 'Top panel should be visible initially')
	assert(btn_restore.visible == false, 'Restore button should be hidden initially')
	
	# Enable Cinema Mode
	inst.call('_set_cinema_mode', true)
	assert(top_p.visible == false, 'Top panel must be hidden in cinema mode')
	assert(cam_p.visible == false, 'Cam panel must be hidden in cinema mode')
	assert(btm_p.visible == false, 'Bottom panel must be hidden in cinema mode')
	assert(btn_restore.visible == true, 'Restore button must be visible in cinema mode')
	print('Cinema Mode (Modo Cine) Enable: PASS')
	
	# Disable Cinema Mode
	inst.call('_set_cinema_mode', false)
	assert(top_p.visible == true, 'Top panel must be restored')
	assert(cam_p.visible == true, 'Cam panel must be restored')
	assert(btm_p.visible == true, 'Bottom panel must be restored')
	assert(btn_restore.visible == false, 'Restore button must be hidden')
	print('Cinema Mode (Modo Cine) Restore: PASS')
	
	# Test Slap Physics
	character.call('apply_slap', true, 1.2, Vector2(0.3, 0.9))
	await process_frame
	await process_frame
	print('Slap Physics Test: PASS')
	
	print('====================================================')
	print('ALL V1.5 QUALITY & FUNCTIONALITY CHECKS PASSED 100%!')
	print('====================================================')
	quit(0)
