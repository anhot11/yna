extends Node

var slap_light_stream: AudioStream = preload("res://assets/audio/slap_light.wav")
var slap_medium_stream: AudioStream = preload("res://assets/audio/slap_medium.wav")
var slap_hard_stream: AudioStream = preload("res://assets/audio/slap_hard.wav")
var slap_crit_stream: AudioStream = preload("res://assets/audio/slap_crit.wav")
var whoosh_stream: AudioStream = preload("res://assets/audio/whoosh.wav")
var gasp_stream: AudioStream = preload("res://assets/audio/gasp_soft.wav")
var squeak_stream: AudioStream = preload("res://assets/audio/squeak.wav")
var ui_click_stream: AudioStream = preload("res://assets/audio/ui_click.wav")
var bgm_stream: AudioStream = preload("res://assets/audio/bgm_loop.wav")

var bgm_player: AudioStreamPlayer
var sfx_players: Array[AudioStreamPlayer] = []
var max_sfx_players: int = 8
var current_sfx_idx: int = 0

var sound_muted: bool = false
var music_muted: bool = false
var is_initialized: bool = false

func _init() -> void:
	_ensure_setup()

func _ready() -> void:
	_ensure_setup()
	if bgm_player and not bgm_player.playing and not music_muted and is_inside_tree():
		bgm_player.play()

func _ensure_setup() -> void:
	if is_initialized:
		return
	is_initialized = true
	
	bgm_player = AudioStreamPlayer.new()
	bgm_player.stream = bgm_stream
	bgm_player.volume_db = -8.0
	add_child(bgm_player)
	bgm_player.finished.connect(_on_bgm_finished)
	
	for i in range(max_sfx_players):
		var p = AudioStreamPlayer.new()
		add_child(p)
		sfx_players.append(p)

func _on_bgm_finished() -> void:
	if not music_muted and bgm_player and is_inside_tree():
		bgm_player.play()

func play_sfx(stream: AudioStream, vol_db: float = 0.0, pitch_var: float = 0.05) -> void:
	_ensure_setup()
	if sound_muted or not stream or sfx_players.is_empty() or not is_inside_tree():
		return
	var player = sfx_players[current_sfx_idx]
	current_sfx_idx = (current_sfx_idx + 1) % sfx_players.size()
	player.stream = stream
	player.volume_db = vol_db
	player.pitch_scale = randf_range(1.0 - pitch_var, 1.0 + pitch_var)
	if player.is_inside_tree():
		player.play()

func play_slap(force: float) -> void:
	if not is_inside_tree():
		return
	var tree = get_tree()
	if force < 350.0:
		play_sfx(slap_light_stream, -2.0, 0.08)
	elif force < 750.0:
		play_sfx(slap_medium_stream, 0.0, 0.06)
		if tree and randf() < 0.4:
			tree.create_timer(0.06).timeout.connect(func(): play_sfx(gasp_stream, -4.0))
	elif force < 1200.0:
		play_sfx(slap_hard_stream, 2.0, 0.05)
		if tree and randf() < 0.6:
			tree.create_timer(0.05).timeout.connect(func(): play_sfx(squeak_stream, -2.0))
	else:
		play_sfx(slap_crit_stream, 4.0, 0.03)
		if tree:
			tree.create_timer(0.04).timeout.connect(func(): play_sfx(squeak_stream, 0.0))

func play_whoosh() -> void:
	play_sfx(whoosh_stream, -5.0, 0.1)

func play_click() -> void:
	play_sfx(ui_click_stream, -3.0, 0.02)

func toggle_sound() -> bool:
	sound_muted = not sound_muted
	return sound_muted

func toggle_music() -> bool:
	music_muted = not music_muted
	if bgm_player and is_inside_tree():
		if music_muted:
			bgm_player.stop()
		else:
			bgm_player.play()
	return music_muted
