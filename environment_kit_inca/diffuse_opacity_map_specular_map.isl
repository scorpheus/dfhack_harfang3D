in {
	tex2D diffuse_map;
	tex2D specular_map;
	float glossiness = 0.5;
}

surface { double-sided: true, alpha-test: true }

variant {
	vertex {
		out {
			vec2 v_uv;
		}

		source %{
			v_uv = vUV0;
		%}
	}

	pixel {
		source %{
			vec4 diffuse_color = texture2D(diffuse_map, v_uv);
			vec4 specular_color = texture2D(specular_map, v_uv);

			%diffuse% = diffuse_color.xyz;
			%specular% = specular_color.xyz;
			%glossiness% = glossiness;
			%opacity% = diffuse_color.w;
		%}
	}
}
