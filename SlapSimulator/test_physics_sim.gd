extends SceneTree

class CheekState:
	var pos: Vector3 = Vector3.ZERO
	var vel: Vector3 = Vector3.ZERO
	var squash: float = 0.0
	var squash_vel: float = 0.0
	var rot: Vector3 = Vector3.ZERO
	var rot_vel: Vector3 = Vector3.ZERO
	var ripple_phase: float = 0.0
	var ripple_amp: float = 0.0

func _init():
	var left = CheekState.new()
	var right = CheekState.new()
	
	var omega = 14.5
	var damping = 0.22
	var d_coeff = 2.0 * damping * omega
	
	# Slap left cheek with force 1.2
	var strength = 1.2
	left.vel += Vector3(0.35 * strength, 0.20 * strength, -0.65 * strength)
	left.squash_vel += 3.8 * strength
	left.rot_vel += Vector3(-2.5, 3.0, -2.0) * strength
	left.ripple_amp = 0.85 * strength
	
	# Cross coupling to right cheek
	right.vel += Vector3(-0.15 * strength, 0.12 * strength, 0.25 * strength)
	right.squash_vel += 1.4 * strength
	
	print("--- SIMULATING 60 FRAMES (1.0 SEC) ---")
	var dt = 0.01666
	var max_pos_l = 0.0
	var max_squash_l = 0.0
	var max_pos_r = 0.0
	
	for i in range(60):
		# Left cheek
		var acc_l = - (omega * omega) * left.pos - d_coeff * left.vel
		# Cross-cheek cleft shear
		acc_l += (right.pos - left.pos) * 12.0
		left.vel += acc_l * dt
		left.pos += left.vel * dt
		
		# Squash
		var acc_sq_l = - (19.0 * 19.0) * left.squash - (2.0 * 0.26 * 19.0) * left.squash_vel
		left.squash_vel += acc_sq_l * dt
		left.squash += left.squash_vel * dt
		
		# Right cheek
		var acc_r = - (omega * omega) * right.pos - d_coeff * right.vel
		acc_r += (left.pos - right.pos) * 12.0
		right.vel += acc_r * dt
		right.pos += right.vel * dt
		
		var acc_sq_r = - (19.0 * 19.0) * right.squash - (2.0 * 0.26 * 19.0) * right.squash_vel
		right.squash_vel += acc_sq_r * dt
		right.squash += right.squash_vel * dt
		
		max_pos_l = max(max_pos_l, left.pos.length())
		max_squash_l = max(max_squash_l, abs(left.squash))
		max_pos_r = max(max_pos_r, right.pos.length())
		
		if i % 10 == 0:
			print("Frame %2d: L_pos=(%.3f, %.3f, %.3f) L_sq=%.3f | R_pos=(%.3f, %.3f, %.3f) R_sq=%.3f" % [
				i, left.pos.x, left.pos.y, left.pos.z, left.squash,
				right.pos.x, right.pos.y, right.pos.z, right.squash
			])
	
	print("\nRESULTS:")
	print("Max Left displacement: %.4f m (%.1f cm)" % [max_pos_l, max_pos_l * 100.0])
	print("Max Left squash factor: %.3f" % max_squash_l)
	print("Max Right displacement: %.4f m (%.1f cm)" % [max_pos_r, max_pos_r * 100.0])
	
	quit(0)
