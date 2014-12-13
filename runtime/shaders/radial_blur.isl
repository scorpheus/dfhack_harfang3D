in {
	float u_strength;
	vec2 u_center;
	tex2D u_tex;
}

variant {
	vertex {
		out {
			vec2 v_uv;
			vec2 forward;
		}

		source %{
			v_uv = vUV0;
			%out.position% = _mtx_mul(vModelViewProjectionMatrix, vec4(vPosition, 1.0));
		%}
	}

	pixel {
		in {
			vec2 v_uv;
			vec2 forward;
		}

		source %{
			vec2 UV = v_uv - u_center;
			float noise = texture2D(vNoiseMap, UV / 128.0 * (vec2(1.0, 1.0) / vInverseInternalResolution.xy)).r; // dampen noise...

			#define STEP 0.1
			noise *= STEP * 2.0;

			vec4 txl = vec4(0.0, 0.0, 0.0, 0.0);
			for	(float k = 0.0; k < 1.0; k += STEP)
				txl += texture2D(u_tex, UV / (1.0 + (k + noise) * u_strength) + u_center);

			%out.color% = txl * STEP;
		%}
	}
}
