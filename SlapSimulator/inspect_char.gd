extends SceneTree

func _init():
	print("--- INSPECTING SCENE ---")
	var scn = load("res://scenes/main.tscn")
	if not scn:
		print("ERROR: could not load main.tscn")
		quit(1)
		return
	var root = scn.instantiate()
	var char_node = root.find_child("Character", true, false)
	print("Character node:", char_node)
	if char_node:
		_print_tree(char_node, 1)
		var skel: Skeleton3D = char_node.find_child("Skeleton3D", true, false)
		if skel:
			print("Skeleton found! Bone count:", skel.get_bone_count())
			for i in range(skel.get_bone_count()):
				print("  Bone %d: %s" % [i, skel.get_bone_name(i)])
		else:
			print("NO Skeleton3D found in Character!")
	
	print("\n--- INSPECTING character.glb ---")
	var glb = load("res://assets/models/character.glb")
	if glb:
		var inst = glb.instantiate()
		_print_tree(inst, 1)
		var skel2: Skeleton3D = inst.find_child("Skeleton3D", true, false)
		if skel2:
			print("GLB Skeleton bone count:", skel2.get_bone_count())
			for i in range(skel2.get_bone_count()):
				print("  GLB Bone %d: %s" % [i, skel2.get_bone_name(i)])
		else:
			print("NO Skeleton3D in GLB!")
	quit(0)

func _print_tree(node: Node, depth: int):
	var indent = "  ".repeat(depth)
	print("%s- %s (%s)" % [indent, node.name, node.get_class()])
	for child in node.get_children():
		_print_tree(child, depth + 1)
