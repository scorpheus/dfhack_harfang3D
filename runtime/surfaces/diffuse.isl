in {
	tex2D diffuse_tex;
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
			vec4 diffuse_color = texture2D(diffuse_tex, v_uv);

			%diffuse% = diffuse_color;
			%normal% = normalize(v_normal);
		%}
	}
}
