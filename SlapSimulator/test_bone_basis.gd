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
	var b_pelvis = skel.find_bone("Pelvis")
	
	print("Pelvis rest transform:", skel.get_bone_rest(b_pelvis))
	print("Cheek_L rest transform:", skel.get_bone_rest(b_l))
	print("Cheek_R rest transform:", skel.get_bone_rest(b_r))
	
	print("Pelvis global pose:", skel.get_bone_global_pose(b_pelvis))
	print("Cheek_L global pose:", skel.get_bone_global_pose(b_l))
	print("Cheek_R global pose:", skel.get_bone_global_pose(b_r))
	
	quit(0)
