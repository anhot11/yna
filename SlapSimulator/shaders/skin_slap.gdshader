shader_type spatial;
render_mode diffuse_burley, specular_schlick_ggx, cull_back;

uniform vec4 skin_color : source_color = vec4(0.92, 0.72, 0.64, 1.0);
uniform vec4 blush_color : source_color = vec4(0.94, 0.16, 0.22, 1.0);
uniform sampler2D normal_map : hint_normal, filter_linear_mipmap, repeat_enable;
uniform float normal_strength : hint_range(0.0, 2.0) = 0.35;
uniform vec2 normal_scale = vec2(18.0, 18.0);

uniform float roughness : hint_range(0.0, 1.0) = 0.42;
uniform float specular : hint_range(0.0, 1.0) = 0.45;

uniform float blush_left : hint_range(0.0, 1.0) = 0.0;
uniform float blush_right : hint_range(0.0, 1.0) = 0.0;
uniform float sss_strength : hint_range(0.0, 1.0) = 1.0;

// Local space coordinates of cheek centers
uniform vec3 left_cheek_center = vec3(-0.110, 0.81, 0.09);
uniform vec3 right_cheek_center = vec3(0.110, 0.81, 0.09);
uniform float blush_radius = 0.18;

// Slap impact ripple wave
uniform vec3 slap_impact_pos = vec3(0.0, 0.81, 0.09);
uniform float slap_wave_time = 99.0;
uniform float slap_wave_amp = 0.0;
uniform float slap_wave_freq = 28.0;
uniform float slap_wave_speed = 1.35;

// Real-time touch poke indentation
uniform vec3 touch_pos = vec3(0.0, 0.81, 0.09);
uniform float touch_depth = 0.0;
uniform float touch_radius = 0.15;

varying vec3 v_vertex;
varying vec3 v_world_pos;
varying vec3 v_normal;
varying vec4 v_color;
varying float sss_local;

// Pure mathematical pseudo-random hash & value noise for procedural skin micro-variation (No texture sampling)
float skin_hash(vec3 p) {
	p = fract(p * 0.3183099 + vec3(0.1, 0.2, 0.3));
	p *= 17.0;
	return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float skin_noise(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	vec3 u = f * f * (3.0 - 2.0 * f);
	
	return mix(
		mix(
			mix(skin_hash(i + vec3(0.0, 0.0, 0.0)), skin_hash(i + vec3(1.0, 0.0, 0.0)), u.x),
			mix(skin_hash(i + vec3(0.0, 1.0, 0.0)), skin_hash(i + vec3(1.0, 1.0, 0.0)), u.x),
			u.y
		),
		mix(
			mix(skin_hash(i + vec3(0.0, 0.0, 1.0)), skin_hash(i + vec3(1.0, 0.0, 1.0)), u.x),
			mix(skin_hash(i + vec3(0.0, 1.0, 1.0)), skin_hash(i + vec3(1.0, 1.0, 1.0)), u.x),
			u.y
		),
		u.z
	);
}

void vertex() {
	// 1. Slap Ripple Shockwave (Expanding concentric rings across soft tissue)
	if (slap_wave_time < 0.85 && slap_wave_amp > 0.0005) {
		float dist = length(VERTEX - slap_impact_pos);
		float wave_front = slap_wave_speed * slap_wave_time;
		float delta_d = dist - wave_front;
		float envelope = exp(-6.5 * slap_wave_time) * exp(-28.0 * delta_d * delta_d);
		float wave = sin(delta_d * slap_wave_freq) * envelope * slap_wave_amp;
		VERTEX += NORMAL * wave;
	}
	
	// 2. Real-time Touch Indentation (Fingertip pushes into soft tissue with rim bulge)
	if (touch_depth > 0.0005) {
		float touch_d = length(VERTEX - touch_pos);
		if (touch_d < touch_radius) {
			float poke_factor = smoothstep(touch_radius, 0.0, touch_d);
			float rim_bulge = sin(poke_factor * 3.1415926) * 0.28;
			VERTEX += NORMAL * (-poke_factor * touch_depth + rim_bulge * touch_depth * 0.45);
		}
	}

	v_vertex = VERTEX;
	v_world_pos = VERTEX;
	v_normal = NORMAL;
	v_color = COLOR;
}

void fragment() {
	// Blush calculation from slap impacts
	float dist_l = length(v_vertex - left_cheek_center);
	float dist_r = length(v_vertex - right_cheek_center);
	
	float factor_l = clamp(1.0 - (dist_l / blush_radius), 0.0, 1.0);
	factor_l = factor_l * factor_l * blush_left;
	
	float factor_r = clamp(1.0 - (dist_r / blush_radius), 0.0, 1.0);
	factor_r = factor_r * factor_r * blush_right;
	
	float total_blush = clamp(factor_l + factor_r, 0.0, 0.95);
	
	// Tangent-space Micro-skin pore normal mapping
	NORMAL_MAP = texture(normal_map, UV * normal_scale).rgb;
	NORMAL_MAP_DEPTH = normal_strength;
	
	// Base color modulated by smooth vertex ambient occlusion (v_color.r)
	float ao = clamp(v_color.r, 0.65, 1.0);
	vec3 base_skin = skin_color.rgb * mix(0.88, 1.0, ao);
	vec3 final_color = mix(base_skin, blush_color.rgb * ao, total_blush);
	
	// --- Realistic Anatomical Skin Color & SSS Variation ---
	// Body coordinate mapping: X = left/right, Y = front/back (buttocks face -Y), Z = height
	vec3 body_pos = vec3(v_world_pos.x, -v_world_pos.z, v_world_pos.y);
	
	// a. Gluteal cleft darkening: X≈0, Y<0, Z in [0.72, 0.92], Gaussian falloff from center (X=0)
	float cleft_x = exp(-pow(body_pos.x / 0.028, 2.0));
	float cleft_y = smoothstep(0.01, -0.02, body_pos.y);
	float cleft_z = smoothstep(0.70, 0.74, body_pos.z) * smoothstep(0.94, 0.88, body_pos.z);
	float cleft_factor = cleft_x * cleft_y * cleft_z * 0.25;
	final_color = mix(final_color, vec3(0.72, 0.52, 0.47) * ao, cleft_factor);
	
	// b. Intimate area coloring (vulva & anus): X near 0, Z in [0.72, 0.78], smooth falloff
	float intimate_x = exp(-pow(body_pos.x / 0.030, 2.0));
	float intimate_y = exp(-pow((body_pos.y + 0.012) / 0.038, 2.0));
	float intimate_z = smoothstep(0.70, 0.73, body_pos.z) * smoothstep(0.80, 0.77, body_pos.z);
	float intimate_factor = intimate_x * intimate_y * intimate_z * 0.30;
	final_color = mix(final_color, vec3(0.78, 0.48, 0.45) * ao, intimate_factor);
	
	// c. Upper inner thigh warmth: Z < 0.73 and abs(X) < 0.12
	float thigh_x = smoothstep(0.12, 0.03, abs(body_pos.x));
	float thigh_z = smoothstep(0.74, 0.70, body_pos.z) * smoothstep(0.48, 0.60, body_pos.z);
	float thigh_factor = thigh_x * thigh_z * 0.15;
	final_color = mix(final_color, vec3(0.85, 0.62, 0.56) * ao, thigh_factor);
	
	// d. General skin color variation: subtle procedural noise breaking uniform tone (factor 0.04)
	float noise_val = skin_noise(v_world_pos * 52.0) * 0.65 + skin_noise(v_world_pos * 118.0) * 0.35;
	vec3 noise_tone = mix(vec3(0.96, 0.80, 0.72), vec3(0.86, 0.62, 0.56), noise_val) * ao;
	final_color = mix(final_color, noise_tone, 0.04);
	
	// Subsurface scattering intensity variation: higher in intimate and cleft areas
	sss_local = 1.0 + intimate_factor * 1.0 + cleft_factor * 0.40;
	
	ALBEDO = final_color;
	ROUGHNESS = mix(roughness, 0.22, total_blush);
	SPECULAR = mix(specular, 0.65, total_blush);
	AO = ao;
	AO_LIGHT_AFFECT = 0.50;
}

void light() {
	// Subsurface Scattering with local anatomical intensity variation
	float effective_sss = sss_strength * sss_local;

	// 1. Subsurface Scattering (Wrapped Diffuse)
	float NdotL = dot(NORMAL, LIGHT);
	float wrap = 0.30 * effective_sss;
	float wrapped_diff = clamp((NdotL + wrap) / (1.0 + wrap), 0.0, 1.0);
	
	// 2. Warm Dermal Blood Scatter at Shadow Terminator
	float scatter_band = smoothstep(-0.20, 0.10, NdotL) * (1.0 - smoothstep(0.0, 0.40, NdotL));
	vec3 sss_color = vec3(0.85, 0.18, 0.08) * scatter_band * 0.25 * effective_sss;
	
	DIFFUSE_LIGHT += (wrapped_diff * ALBEDO * 0.80 + sss_color) * ATTENUATION * LIGHT_COLOR;
	
	// 3. Dual-Lobe Specular (Natural skin sheen)
	vec3 H = normalize(VIEW + LIGHT);
	float NdotH = clamp(dot(NORMAL, H), 0.0, 1.0);
	float NdotV = clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	
	float broad_spec = pow(NdotH, 18.0) * 0.14;
	float sharp_spec = pow(NdotH, 55.0) * 0.32;
	
	float fresnel = pow(1.0 - NdotV, 4.0);
	vec3 spec_tint = mix(vec3(0.04), vec3(0.60), fresnel);
	
	SPECULAR_LIGHT += (broad_spec + sharp_spec) * spec_tint * ATTENUATION * LIGHT_COLOR;
}
