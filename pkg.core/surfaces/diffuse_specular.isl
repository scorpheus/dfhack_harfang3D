in {
	vec4 diffuse_color = vec4(0.7,0.7,0.7,1.0) [hint:color];
	vec4 specular_color = vec4(0.5,0.5,0.5,1.0) [hint:color];
}

variant {
	pixel {
		source %{
			%diffuse% = diffuse_color;
			%specular% = specular_color;
		%}
	}
}
