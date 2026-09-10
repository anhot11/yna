shader_type spatial;
render_mode cull_back, diffuse_burley, specular_schlick_ggx;

uniform sampler2D texture_albedo : source_color, filter_linear_mipmap, repeat_enable;
uniform vec4 color_tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float roughness : hint_range(0.0, 1.0) = 0.35;
uniform float metallic : hint_range(0.0, 1.0) = 0.05;
uniform vec2 uv_scale = vec2(3.0, 3.0);

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
uniform float depth_bias : hint_range(0.0, 0.005) = 0.0012;

void vertex() {
	// 1. Slap Ripple Shockwave
	if (slap_wave_time < 0.85 && slap_wave_amp > 0.0005) {
		float dist = length(VERTEX - slap_impact_pos);
		float wave_front = slap_wave_speed * slap_wave_time;
		float delta_d = dist - wave_front;
		float envelope = exp(-6.5 * slap_wave_time) * exp(-28.0 * delta_d * delta_d);
		float wave = sin(delta_d * slap_wave_freq) * envelope * slap_wave_amp;
		VERTEX += NORMAL * wave;
	}
	
	// 2. Real-time Touch Indentation
	if (touch_depth > 0.0005) {
		float touch_d = length(VERTEX - touch_pos);
		if (touch_d < touch_radius) {
			float poke_factor = smoothstep(touch_radius, 0.0, touch_d);
			float rim_bulge = sin(poke_factor * 3.1415926) * 0.28;
			VERTEX += NORMAL * (-poke_factor * touch_depth + rim_bulge * touch_depth * 0.45);
		}
	}
	
	// 3. Normal depth bias to guarantee zero clipping over skin
	VERTEX += NORMAL * depth_bias;
}

void fragment() {
	vec4 tex = texture(texture_albedo, UV * uv_scale);
	ALBEDO = tex.rgb * color_tint.rgb;
	ROUGHNESS = roughness;
	METALLIC = metallic;
	
	float fresnel = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 3.0);
	SPECULAR = mix(0.35, 0.65, fresnel);
}

void light() {
	float NdotL = clamp(dot(NORMAL, LIGHT), 0.0, 1.0);
	DIFFUSE_LIGHT += NdotL * ALBEDO * 0.85 * ATTENUATION * LIGHT_COLOR;
	
	vec3 H = normalize(VIEW + LIGHT);
	float NdotH = clamp(dot(NORMAL, H), 0.0, 1.0);
	SPECULAR_LIGHT += pow(NdotH, 32.0) * 0.22 * ATTENUATION * LIGHT_COLOR;
}
