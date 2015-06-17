in {
	vec4 diffuse_color = vec4(0.7,0.7,0.7,1.0) [hint:color];
	vec4 specular_color = vec4(0.5,0.5,0.5,1.0) [hint:color];
}
surface { double-sided: false }
variant {
	vertex {
		out { vec3 n; }

		source %{
            n = normalize(vNormalMatrix * vNormal);

			%out.position% = _mtx_mul(vModelViewProjectionMatrix, vec4(vPosition, 1.0));
		%}
	}

	pixel {
		source %{
			vec3 light_pos = vec3(160, 200, 0);
			vec3 normal = normalize(n);

			float NdotL = max(dot(normal,light_pos),0.0);

			vec4 color = diffuse_color;
			if (NdotL > 0.0)
				color = vec4(NdotL);

			%diffuse% = color;
			%specular% = specular_color;
		%}
	}
}
