extends SceneTree

func _init():
	var scn = load("res://scenes/main.tscn")
	var root = scn.instantiate()
	get_root().add_child(root)
	
	# Give engine a frame to run _ready
	await process_frame
	await process_frame
	
	var char_node: CharacterController = root.find_child("Character", true, false)
	print("char_node:", char_node)
	print("skeleton:", char_node.skeleton)
	print("bone_cheek_l idx:", char_node.bone_cheek_l)
	print("bone_cheek_r idx:", char_node.bone_cheek_r)
	print("rest_pos_l:", char_node.rest_pos_l)
	print("rest_pos_r:", char_node.rest_pos_r)
	
	# Let's test apply_slap!
	char_node.apply_slap(true, 1.5, Vector2(0, 1))
	for f in range(5):
		await process_frame
		print("Frame ", f, " pos_l: ", char_node.pos_l, " vel_l: ", char_node.vel_l)
		var pose_pos = char_node.skeleton.get_bone_pose_position(char_node.bone_cheek_l)
		print("  Bone Cheek_L pose_pos: ", pose_pos)
	
	quit(0)
