extends SceneTree

func _init():
	var scn = load("res://scenes/main.tscn")
	var root = scn.instantiate()
	get_root().add_child(root)
	await process_frame
	await process_frame
	
	var skel: Skeleton3D = root.find_child("Skeleton3D", true, false)
	var b_l = skel.find_bone("Cheek_L")
	var b_r = skel.find_bone("Cheek_R")
	var rest_l = skel.get_bone_rest(b_l)
	var rest_r = skel.get_bone_rest(b_r)
	
	print("Cheek_L rest origin:", rest_l.origin)
	print("Cheek_R rest origin:", rest_r.origin)
	
	# Test displacement of 3cm forward, 2cm outward
	var disp = Vector3(-0.02, 0.02, 0.035)
	skel.set_bone_pose_position(b_l, rest_l.origin + disp)
	skel.set_bone_pose_scale(b_l, Vector3(1.15, 1.15, 0.80))
	skel.set_bone_pose_rotation(b_l, Quaternion.from_euler(Vector3(0.1, 0.15, -0.05)))
	
	print("After applying pose:")
	print("  Cheek_L pose pos:", skel.get_bone_pose_position(b_l))
	print("  Cheek_L pose scale:", skel.get_bone_pose_scale(b_l))
	print("  Cheek_L pose rot:", skel.get_bone_pose_rotation(b_l))
	
	quit(0)
