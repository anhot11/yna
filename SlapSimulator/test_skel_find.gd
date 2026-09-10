extends SceneTree

func _init():
	var scn = load("res://scenes/main.tscn")
	var root = scn.instantiate()
	var char_node = root.find_child("Character", true, false)
	print("Char node children:")
	for c in char_node.get_children():
		print("  child: ", c.name, " (", c.get_class(), ")")
		for c2 in c.get_children():
			print("    grandchild: ", c2.name, " (", c2.get_class(), ")")
	
	print("find_child Skeleton3D (recursive=true, owned=false):", char_node.find_child("Skeleton3D", true, false))
	print("find_child Skeleton3D (recursive=true, owned=true):", char_node.find_child("Skeleton3D", true, true))
	print("find_child *Skeleton*:", char_node.find_child("*Skeleton*", true, false))
	
	quit(0)
