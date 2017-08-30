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
			%diffuse% = diffuse_color.xyz;
			%specular% = specular_color.xyz;
		%}
	}
}
