extends SceneTree

func _init():
	print("--- BEGIN GRAPHICS SETTINGS TEST ---")
	var scene = load("res://scenes/main.tscn")
	if not scene:
		print("FAILED: Could not load scenes/main.tscn")
		quit(1)
		return
		
	var inst = scene.instantiate()
	root.add_child(inst)
	
	await process_frame
	await process_frame
	
	var gfx = inst.find_child("GraphicsManager", true, false)
	var overlay = inst.find_child("SettingsOverlay", true, false)
	var btn_top = inst.find_child("BtnSettingsTop", true, false)
	var btn_bottom = inst.find_child("BtnSettingsBottom", true, false)
	var btn_baja = inst.find_child("BtnPresetBaja", true, false)
	var btn_media = inst.find_child("BtnPresetMedia", true, false)
	var btn_alta = inst.find_child("BtnPresetAlta", true, false)
	var btn_ultra = inst.find_child("BtnPresetUltra", true, false)
	var btn_close = inst.find_child("BtnCloseSettings", true, false)
	
	assert(gfx != null, "GraphicsManager must exist")
	assert(overlay != null, "SettingsOverlay must exist")
	assert(btn_top != null, "BtnSettingsTop must exist")
	assert(btn_bottom != null, "BtnSettingsBottom must exist")
	assert(btn_baja != null, "BtnPresetBaja must exist")
	assert(btn_close != null, "BtnCloseSettings must exist")
	print("All settings nodes verified successfully!")
	
	# Verify default hidden
	assert(overlay.visible == false, "Overlay should initially be hidden")
	print("Initial overlay visibility: FALSE (PASS)")
	
	# Open settings via script
	inst.call("_open_settings")
	assert(overlay.visible == true, "Overlay should be visible after _open_settings")
	print("Overlay visibility after open: TRUE (PASS)")
	
	# Test Baja Preset
	btn_baja.emit_signal("pressed")
	assert(gfx.preset == "Baja", "Preset should be Baja")
	assert(gfx.shadows_quality == 0, "Baja shadows should be 0")
	assert(gfx.glow_enabled == false, "Baja glow should be false")
	assert(gfx.sss_enabled == false, "Baja SSS should be false")
	print("Preset Baja test: PASS (Shadows=0, Glow=false, SSS=false)")
	
	# Test Ultra Preset
	btn_ultra.emit_signal("pressed")
	assert(gfx.preset == "Ultra", "Preset should be Ultra")
	assert(gfx.shadows_quality == 2, "Ultra shadows should be 2")
	assert(gfx.msaa_quality == 2, "Ultra MSAA should be 2")
	assert(gfx.glow_enabled == true, "Ultra glow should be true")
	assert(gfx.sss_enabled == true, "Ultra SSS should be true")
	print("Preset Ultra test: PASS (Shadows=2, MSAA=2, Glow=true, SSS=true)")
	
	# Test granular toggle SSS
	var btn_sss = inst.find_child("BtnOptSSS", true, false)
	assert(btn_sss != null, "BtnOptSSS must exist")
	btn_sss.emit_signal("pressed")
	assert(gfx.sss_enabled == false, "SSS should be toggled to false")
	assert(gfx.preset == "Personalizado", "Preset should now be Personalizado")
	print("Granular SSS toggle test: PASS")
	
	# Test config file persistence
	var cfg = ConfigFile.new()
	var err = cfg.load("user://graphics_settings.cfg")
	assert(err == OK, "ConfigFile should be saved and loaded from user://graphics_settings.cfg")
	var saved_preset = cfg.get_value("graphics", "preset")
	assert(saved_preset == "Personalizado", "Saved preset in config should match")
	print("Persistence test: PASS (user://graphics_settings.cfg saved successfully)")
	
	# Close settings
	btn_close.emit_signal("pressed")
	assert(overlay.visible == false, "Overlay should be hidden after close")
	print("Overlay visibility after close: FALSE (PASS)")
	
	print("--- ALL GRAPHICS SETTINGS TESTS PASSED SUCCESSFULLY! ---")
	quit(0)
