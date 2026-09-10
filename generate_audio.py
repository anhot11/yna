import numpy as np
import wave
import struct
import os
import math

audio_dir = r"I:\workzone\gotot\yna\SlapSimulator\assets\audio"
os.makedirs(audio_dir, exist_ok=True)
sample_rate = 44100

def write_wav(filename, samples, sr=44100):
    filepath = os.path.join(audio_dir, filename)
    # Normalize to 0.95 peak
    peak = np.max(np.abs(samples))
    if peak > 0:
        samples = samples / peak * 0.95
    int_samples = np.int16(samples * 32767)
    with wave.open(filepath, "w") as f:
        f.setnchannels(1) # mono
        f.setsampwidth(2) # 16-bit
        f.setframerate(sr)
        f.writeframes(int_samples.tobytes())
    print("Generated:", filename)

# 1. SLAP SOUNDS
def make_slap(dur=0.25, snap_f=3200, thump_f=180, snap_decay=60.0, thump_decay=25.0, noise_amount=0.7):
    n_samples = int(sample_rate * dur)
    t = np.linspace(0, dur, n_samples, endpoint=False)
    
    # Transient snap
    snap_env = np.exp(-snap_decay * t)
    snap = np.sin(2 * np.pi * snap_f * t) * snap_env
    
    # Noise crack
    noise = (np.random.rand(n_samples) * 2.0 - 1.0)
    # Simple lowpass / bandpass for noise
    noise_env = np.exp(-snap_decay * 1.5 * t)
    noise_crack = noise * noise_env * noise_amount
    
    # Flesh body & thump (pitch drop)
    flesh_freq = thump_f * np.exp(-15.0 * t) + 70.0
    flesh_phase = 2 * np.pi * np.cumsum(flesh_freq) / sample_rate
    flesh_env = np.exp(-thump_decay * t)
    flesh_thump = np.sin(flesh_phase) * flesh_env * 1.2
    
    # Add subtle sub punch
    sub_env = np.exp(-thump_decay * 1.8 * t)
    sub_thump = np.sin(2 * np.pi * 65.0 * t) * sub_env * 0.8
    
    total = snap * 0.6 + noise_crack * 0.8 + flesh_thump + sub_thump
    return total

# Light Slap (quick, crisp)
write_wav("slap_light.wav", make_slap(dur=0.15, snap_f=3800, thump_f=240, snap_decay=80.0, thump_decay=40.0, noise_amount=0.8))

# Medium Slap (solid, punchy)
write_wav("slap_medium.wav", make_slap(dur=0.22, snap_f=3200, thump_f=190, snap_decay=55.0, thump_decay=28.0, noise_amount=0.9))

# Hard Slap (deep thud and sharp crack)
write_wav("slap_hard.wav", make_slap(dur=0.30, snap_f=2800, thump_f=160, snap_decay=42.0, thump_decay=20.0, noise_amount=1.1))

# Critical Slap (explosive resonant smack)
crit = make_slap(dur=0.40, snap_f=2500, thump_f=140, snap_decay=30.0, thump_decay=14.0, noise_amount=1.4)
# Add a small stereo-like reverb tail
reverb_tail = np.zeros_like(crit)
for delay, decay in [(0.02, 0.4), (0.045, 0.25), (0.07, 0.15)]:
    d_samp = int(delay * sample_rate)
    reverb_tail[d_samp:] += crit[:-d_samp] * decay
write_wav("slap_crit.wav", crit + reverb_tail)

# 2. WHOOSH SOUND (Swipe gesture)
def make_whoosh(dur=0.20):
    n = int(sample_rate * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    noise = np.random.randn(n)
    # Bandpass sweep from 400Hz to 1200Hz and back
    env = np.sin(np.pi * t / dur) ** 2
    f_center = 500 + 800 * np.sin(np.pi * t / dur)
    # Approximate filter via sine modulation
    whoosh = noise * env * np.sin(2 * np.pi * f_center * t)
    return whoosh

write_wav("whoosh.wav", make_whoosh())

# 3. CUTE GASP / SQUEAK REACTION SOUNDS
def make_gasp(dur=0.28):
    n = int(sample_rate * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    # Breathy aspiration + formant
    noise = np.random.randn(n) * 0.4
    f1, f2 = 800, 1600
    env = np.sin(np.pi * t / dur) ** 1.5
    tone = np.sin(2 * np.pi * f1 * t) * 0.3 + np.sin(2 * np.pi * f2 * t) * 0.2
    return (noise + tone) * env

write_wav("gasp_soft.wav", make_gasp(0.25))

def make_squeak(dur=0.22):
    n = int(sample_rate * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    # Pitch upward sweep
    f = 500 + 1200 * (t / dur) ** 0.7
    phase = 2 * np.pi * np.cumsum(f) / sample_rate
    env = np.sin(np.pi * t / dur) ** 1.8
    return np.sin(phase) * env

write_wav("squeak.wav", make_squeak(0.20))

# 4. UI CLICK
def make_click(dur=0.05):
    n = int(sample_rate * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    env = np.exp(-80.0 * t)
    return np.sin(2 * np.pi * 1200 * t) * env

write_wav("ui_click.wav", make_click())

# 5. BGM BEAT LOOP (Catchy, cheerful, bouncy beat loop, ~8 seconds)
def make_bgm(bpm=110, bars=4):
    beat_dur = 60.0 / bpm
    total_dur = beat_dur * 4 * bars # 4/4 time
    n = int(sample_rate * total_dur)
    track = np.zeros(n)
    
    # Bassline notes (Frequencies in Hz: C3, D#3, F3, G3, A#2, etc.)
    scale = [130.81, 155.56, 174.61, 196.00, 116.54, 146.83]
    
    # Drums & Bass
    total_beats = 4 * bars
    for b in range(total_beats):
        b_time = b * beat_dur
        idx = int(b_time * sample_rate)
        
        # Kick on 1 and 3
        if b % 2 == 0:
            k_dur = 0.2
            k_n = min(int(k_dur * sample_rate), n - idx)
            kt = np.linspace(0, k_dur, k_n, endpoint=False)
            kf = 120 * np.exp(-25.0 * kt) + 45.0
            kp = 2 * np.pi * np.cumsum(kf) / sample_rate
            ke = np.exp(-18.0 * kt)
            track[idx:idx+k_n] += np.sin(kp) * ke * 0.7
        
        # Snare / Clap on 2 and 4
        if b % 2 == 1:
            s_dur = 0.18
            s_n = min(int(s_dur * sample_rate), n - idx)
            st = np.linspace(0, s_dur, s_n, endpoint=False)
            sn = np.random.randn(s_n) * np.exp(-22.0 * st) * 0.4
            st_tone = np.sin(2 * np.pi * 220 * st) * np.exp(-25.0 * st) * 0.3
            track[idx:idx+s_n] += (sn + st_tone) * 0.6
        
        # Hi-hat on every 8th note
        for sub_b in [0, 0.5]:
            h_time = (b + sub_b) * beat_dur
            h_idx = int(h_time * sample_rate)
            h_dur = 0.04
            h_n = min(int(h_dur * sample_rate), n - h_idx)
            ht = np.linspace(0, h_dur, h_n, endpoint=False)
            hn = np.random.randn(h_n) * np.exp(-90.0 * ht) * 0.15
            track[h_idx:h_idx+h_n] += hn
            
        # Funky synth bass note
        note_freq = scale[(b // 2) % len(scale)]
        bass_dur = beat_dur * 0.75
        bass_n = min(int(bass_dur * sample_rate), n - idx)
        bt = np.linspace(0, bass_dur, bass_n, endpoint=False)
        benv = np.sin(np.pi * bt / bass_dur) ** 0.8
        # Rich sawtooth/FM bass
        bass = (np.sin(2 * np.pi * note_freq * bt) + 
                0.5 * np.sin(4 * np.pi * note_freq * bt) +
                0.25 * np.sin(6 * np.pi * note_freq * bt)) * benv * 0.45
        track[idx:idx+bass_n] += bass

    return track

write_wav("bgm_loop.wav", make_bgm())
print("All audio assets generated successfully!")
