in {
	tex2D diffuse_map = "assets/blank.jpg";
	tex2D specular_map = "assets/blank.jpg";
}

variant {
	vertex {
		out {
			vec2 v_uv;
			vec3 v_normal;
		}

		source %{
			v_uv = vUV0;
			v_normal = vNormal;
		%}
	}

	pixel {
		source %{
			%diffuse% = texture2D(diffuse_map, v_uv);
			%specular% = texture2D(specular_map, v_uv);
			%normal% = normalize(v_normal);
		%}
	}
}