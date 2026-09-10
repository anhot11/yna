extends SceneTree

func _init():
	var scn = load("res://scenes/main.tscn")
	var root = scn.instantiate()
	get_root().add_child(root)
	
	await process_frame
	await process_frame
	
	var char_node: CharacterController = root.find_child("Character", true, false)
	print("char_node ready:", char_node != null)
	print("skeleton:", char_node.skeleton != null)
	print("bone_cheek_l:", char_node.bone_cheek_l)
	print("bone_cheek_r:", char_node.bone_cheek_r)
	
	print("\n--- Testing start_touch & update_touch_drag ---")
	char_node.start_touch(Vector3(-0.11, 0.81, 0.09), true)
	char_node.update_touch_drag(Vector2(20.0, -15.0))
	for f in range(3):
		await process_frame
		print("Touch frame %d: pos_l=%s squash_l=%.3f" % [f, str(char_node.pos_l), char_node.squash_l])
	char_node.end_touch(false)
	
	print("\n--- Testing apply_slap(true, 1.4, Vector2(0.5, 0.2)) ---")
	char_node.apply_slap(true, 1.4, Vector2(0.5, 0.2))
	var max_l = 0.0
	var max_r = 0.0
	for f in range(30):
		await process_frame
		var cur_l = char_node.pos_l.length()
		var cur_r = char_node.pos_r.length()
		if cur_l > max_l: max_l = cur_l
		if cur_r > max_r: max_r = cur_r
		if f % 5 == 0:
			var pose_pos = char_node.skeleton.get_bone_pose_position(char_node.bone_cheek_l)
			var pose_scale = char_node.skeleton.get_bone_pose_scale(char_node.bone_cheek_l)
			print("Slap frame %2d: pos_l=%s sq_l=%.3f scale_l=%s | max_l=%.3fm max_r=%.3fm" % [
				f, str(char_node.pos_l), char_node.squash_l, str(pose_scale), max_l, max_r
			])
	
	print("\nSUCCESS: Max L=%.1f cm, Max R=%.1f cm" % [max_l * 100.0, max_r * 100.0])
	quit(0)
