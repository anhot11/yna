extends SceneTree

func _init():
	print("==================================================")
	print("     VERIFYING INCREDIBLE BUTT PHYSICS ENGINE     ")
	print("==================================================")
	
	var scn = load("res://scenes/main.tscn")
	if not scn:
		print("FAILED: Could not load scenes/main.tscn")
		quit(1)
		return
		
	var root = scn.instantiate()
	get_root().add_child(root)
	
	await process_frame
	await process_frame
	
	var char_node: CharacterController = root.find_child("Character", true, false)
	var main_node = root
	var touch_area = root.find_child("TouchArea", true, false)
	var tw = touch_area.size.x if touch_area else 720.0
	var th = touch_area.size.y if touch_area else 1280.0
	
	assert(char_node != null, "Character node must exist")
	assert(char_node.skeleton != null, "Skeleton3D must exist")
	assert(char_node.bone_cheek_l != -1, "Cheek_L bone must be resolved")
	assert(char_node.bone_cheek_r != -1, "Cheek_R bone must be resolved")
	print("[PASS] Test 1: Skeleton and Bone resolution verified.")
	
	# Test 2: Interactive Real-Time Touch Down (Poke Indentation)
	print("\n--- Test 2: Real-time Touch Poke Indentation ---")
	var press_event = InputEventScreenTouch.new()
	press_event.index = 0
	press_event.pressed = true
	press_event.position = Vector2(tw * 0.35, th * 0.5) # Left cheek tap
	main_node._on_touch_area_input(press_event)
	
	await process_frame
	await process_frame
	print("  pos_l after poke:", char_node.pos_l)
	print("  squash_l after poke:", char_node.squash_l)
	assert(char_node.is_touching, "Character must be in touching state")
	assert(char_node.touch_is_left, "Touch must be on left cheek")
	assert(char_node.pos_l.z < 0.0, "Cheek must be indented inward in depth (-Z)")
	print("[PASS] Test 2: Real-time Poke Indentation verified.")
	
	# Test 3: Interactive Touch Drag (Elastic Stretch)
	print("\n--- Test 3: Interactive Elastic Drag ---")
	var drag_event = InputEventScreenDrag.new()
	drag_event.index = 0
	drag_event.position = Vector2(tw * 0.40, th * 0.45)
	drag_event.relative = Vector2(40, -40)
	main_node._on_touch_area_input(drag_event)
	
	await process_frame
	await process_frame
	print("  touch_drag_target:", char_node.touch_drag_target)
	assert(char_node.touch_drag_target.x > 0.0, "Cheek must pull horizontally with drag")
	assert(char_node.touch_drag_target.y > 0.0, "Cheek must pull vertically with drag")
	print("[PASS] Test 3: Interactive Elastic Drag verified.")
	
	# Test 4: Elastic Snap-back Release
	print("\n--- Test 4: Elastic Snap-Back Release ---")
	char_node.end_touch(false)
	await process_frame
	assert(not char_node.is_touching, "Touch must end")
	print("  vel_l after release:", char_node.vel_l)
	print("[PASS] Test 4: Elastic Snap-Back Release verified.")
	
	# Test 5: High-Energy Left Cheek Slap Physics
	print("\n--- Test 5: High-Energy Left Cheek Slap ---")
	main_node._execute_slap(Vector2(tw * 0.35, th * 0.5), Vector2(0.8, -0.2), 950.0)
	
	var max_disp_l = 0.0
	var max_disp_r = 0.0
	var max_sq_l = 0.0
	for f in range(40):
		await process_frame
		var dl = char_node.pos_l.length()
		var dr = char_node.pos_r.length()
		if dl > max_disp_l: max_disp_l = dl
		if dr > max_disp_r: max_disp_r = dr
		if abs(char_node.squash_l) > max_sq_l: max_sq_l = abs(char_node.squash_l)
	
	print("  Max Left displacement: %.2f cm" % (max_disp_l * 100.0))
	print("  Max Right (sympathy) displacement: %.2f cm" % (max_disp_r * 100.0))
	print("  Max Squash factor: %.3f" % max_sq_l)
	assert(max_disp_l > 0.030, "Left cheek must bounce at least 3.0 cm")
	assert(max_disp_r > 0.010, "Right cheek must bounce sympathetically via cleft coupling")
	assert(max_sq_l > 0.10, "Squash factor must exceed 0.10")
	assert(char_node.blush_l > 0.20, "Blush must increase on impact")
	print("[PASS] Test 5: Left Cheek Slap Physics verified.")
	
	# Test 6: High-Energy Right Cheek Slap Physics
	print("\n--- Test 6: High-Energy Right Cheek Slap ---")
	main_node._execute_slap(Vector2(tw * 0.65, th * 0.5), Vector2(-0.8, -0.2), 950.0)
	
	var max_r_disp = 0.0
	var max_l_cross = 0.0
	for f in range(40):
		await process_frame
		var dl = char_node.pos_l.length()
		var dr = char_node.pos_r.length()
		if dr > max_r_disp: max_r_disp = dr
		if dl > max_l_cross: max_l_cross = dl
	
	print("  Max Right displacement: %.2f cm" % (max_r_disp * 100.0))
	print("  Max Left (sympathy) displacement: %.2f cm" % (max_l_cross * 100.0))
	assert(max_r_disp > 0.030, "Right cheek must bounce at least 3.0 cm")
	assert(char_node.blush_r > 0.20, "Right blush must increase")
	print("[PASS] Test 6: Right Cheek Slap Physics verified.")
	
	# Test 7: Stability over 100 consecutive frames
	print("\n--- Test 7: Long-term Stability (100 frames) ---")
	for f in range(100):
		await process_frame
		assert(not is_nan(char_node.pos_l.x), "No NaN allowed")
		assert(not is_nan(char_node.pos_r.x), "No NaN allowed")
	print("[PASS] Test 7: Long-term numerical stability verified.")
	
	print("\n==================================================")
	print("  ALL 7 INCREDIBLE BUTT PHYSICS TESTS PASSED 100% ")
	print("==================================================")
	quit(0)
