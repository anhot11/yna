extends SceneTree

func _init():
	var scn = load("res://scenes/main.tscn")
	var root = scn.instantiate()
	get_root().add_child(root)
	await process_frame
	await process_frame
	
	var cam: Camera3D = root.find_child("Camera3D", true, false)
	print("Camera:", cam)
	var vp_size = Vector2(720, 1280)
	
	# Test raycast at center of screen (360, 640)
	var screen_center = vp_size * 0.5
	var ray_o = cam.project_ray_origin(screen_center)
	var ray_d = cam.project_ray_normal(screen_center)
	print("Ray origin:", ray_o, "dir:", ray_d)
	
	# Intersect with plane Z = 0.09
	var t = (0.09 - ray_o.z) / ray_d.z
	var hit = ray_o + ray_d * t
	print("Hit point for screen center:", hit)
	
	# Test raycast at left cheek (approx X = 260, Y = 640)
	var screen_left = Vector2(260, 640)
	var ray_o_l = cam.project_ray_origin(screen_left)
	var ray_d_l = cam.project_ray_normal(screen_left)
	var t_l = (0.09 - ray_o_l.z) / ray_d_l.z
	var hit_l = ray_o_l + ray_d_l * t_l
	print("Hit point for left tap:", hit_l)
	
	# Test raycast at right cheek (approx X = 460, Y = 640)
	var screen_right = Vector2(460, 640)
	var ray_o_r = cam.project_ray_origin(screen_right)
	var ray_d_r = cam.project_ray_normal(screen_right)
	var t_r = (0.09 - ray_o_r.z) / ray_d_r.z
	var hit_r = ray_o_r + ray_d_r * t_r
	print("Hit point for right tap:", hit_r)
	
	quit(0)
