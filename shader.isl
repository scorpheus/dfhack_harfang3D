in {
}

surface {
	double-sided: true
}

variant {
	vertex {
        out {
            vec3 v_normal;
        }

		source %{
			%out.position% = _mtx_mul(vModelViewProjectionMatrix, vec4(vPosition, 1.0));
			v_normal = vNormal;
		%}
	}

	pixel {
		source %{
			%diffuse% = vec4(0.22, 0.73, 0.35, 1.0);
			%normal% = normalize(v_normal);
		%}
	}
}
