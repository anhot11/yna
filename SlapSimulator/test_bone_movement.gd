extends SceneTree

func _init():
	var scn = load("res://scenes/main.tscn")
	var root = scn.instantiate()
	var skel: Skeleton3D = root.find_child("Skeleton3D", true, false)
	var bone_l = skel.find_bone("Cheek_L")
	print("Bone Cheek_L rest pose:")
	var rest = skel.get_bone_rest(bone_l)
	print("  rest origin:", rest.origin)
	print("  initial pose position:", skel.get_bone_pose_position(bone_l))
	
	# If we set pose position to rest.origin + Vector3(0, 0.1, 0)
	skel.set_bone_pose_position(bone_l, rest.origin + Vector3(0, 0.1, 0))
	print("After setting rest + (0, 0.1, 0):")
	print("  pose position:", skel.get_bone_pose_position(bone_l))
	print("  bone global pose:", skel.get_bone_global_pose(bone_l).origin)
	
	# Now let's see what happens if we set pose position to Vector3(0, 0.1, 0):
	skel.set_bone_pose_position(bone_l, Vector3(0, 0.1, 0))
	print("After setting (0, 0.1, 0):")
	print("  pose position:", skel.get_bone_pose_position(bone_l))
	print("  bone global pose:", skel.get_bone_global_pose(bone_l).origin)
	
	quit(0)
