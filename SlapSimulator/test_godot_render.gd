extends SceneTree

func _init():
	var scn = load("res://scenes/main.tscn")
	var root = scn.instantiate()
	get_root().add_child(root)
	
	await process_frame
	await process_frame
	
	var img = get_root().get_viewport().get_texture().get_image()
	img.save_png("C:/Users/kiosk/.gemini/antigravity-cli/brain/c69cd41b-33a7-42a9-9d33-a8d52789ab72/test_godot_baseline.png")
	print("Saved test_godot_baseline.png!")
	quit(0)
