extends SceneTree

func _init():
	var cfg = ConfigFile.new()
	cfg.load('res://export_presets.cfg')
	for sec in cfg.get_sections():
		print('[', sec, ']')
		for key in cfg.get_section_keys(sec):
			if 'icon' in key.lower() or 'launcher' in key.lower():
				print(key, '=', cfg.get_value(sec, key))
	quit(0)
