extends SceneTree

func _init():
	var scn = load("res://scenes/main.tscn")
	var root = scn.instantiate()
	get_root().add_child(root)
	await process_frame
	await process_frame
	
	var skel: Skeleton3D = root.find_child("Skeleton3D", true, false)
	var b_l = skel.find_bone("Cheek_L")
	print("Cheek_L initial pose scale:", skel.get_bone_pose_scale(b_l))
	skel.set_bone_pose_scale(b_l, Vector3(1.2, 1.2, 0.8))
	print("Cheek_L modified pose scale:", skel.get_bone_pose_scale(b_l))
	
	quit(0)
