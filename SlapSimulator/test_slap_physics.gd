extends SceneTree

func _init():
	var scn = load("res://scenes/main.tscn")
	var root = scn.instantiate()
	get_root().add_child(root)
	
	var char_node: CharacterController = root.find_child("Character", true, false)
	print("char_node:", char_node)
	print("skeleton:", char_node.skeleton)
	print("bone_cheek_l idx:", char_node.bone_cheek_l)
	print("bone_cheek_r idx:", char_node.bone_cheek_r)
	print("rest_pos_l:", char_node.rest_pos_l)
	print("rest_pos_r:", char_node.rest_pos_r)
	
	print("\nCalling apply_slap(true, 1.5, Vector2(0, 1))...")
	char_node.apply_slap(true, 1.5, Vector2(0, 1))
	print("pos_l before process:", char_node.pos_l, "vel_l:", char_node.vel_l)
	
	for i in range(10):
		char_node._process(0.016)
		print("Frame %d: pos_l=%s vel_l=%s" % [i, str(char_node.pos_l), str(char_node.vel_l)])
		if char_node.skeleton:
			var pose_pos = char_node.skeleton.get_bone_pose_position(char_node.bone_cheek_l)
			print("   skeleton pose pos: %s" % str(pose_pos))
	
	quit(0)
