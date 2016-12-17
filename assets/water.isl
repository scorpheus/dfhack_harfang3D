in {
	vec4 diffuse_color = vec4(0.7,0.7,0.7,1.0) [hint:color];
	vec4 specular_color = vec4(0.5,0.5,0.5,1.0) [hint:color];
	int ITER_GEOMETRY = 1;
    int ITER_FRAGMENT = 4;
    float SEA_HEIGHT = 0.3;
    float SEA_CHOPPY = 2.0;
    float SEA_SPEED = 0.1;
    float SEA_FREQ = 0.4;
    vec4 SEA_BASE = vec4(0.1, 0.19, 0.22, 1.0) [hint:color];
    vec4 SEA_WATER_COLOR = vec4(0.8, 0.9, 0.6, 1.0) [hint:color];
}
surface { double-sided: false }
variant {
	vertex {
		out { 	vec3 v_vtx;		}

		source %{
			v_vtx = _mtx_mul(vModelMatrix, vec4(vPosition, 1.0)).xyz;
			%position% = vec4(vPosition, 1.0);
		%}
	}

	pixel {

		global %{
            const int NUM_STEPS = 8;
            const float PI	 	= 3.1415;
            const float EPSILON	= 1e-3;
            float EPSILON_NRM	= 0.1 * vInverseInternalResolution.x;

            // sea
       		float SEA_TIME = vClock * SEA_SPEED;
            mat2 octave_m = mat2(1.6,1.2,-1.2,1.6);

            // math
            float hash( vec2 p ) {
                float h = dot(p,vec2(127.1,311.7));
                return fract(sin(h)*43758.5453123);
            }

            float noise( in vec2 p ) {
                vec2 i = floor( p );
                vec2 f = fract( p );
                vec2 u = f*f*(3.0-2.0*f);
                return -1.0+2.0*mix( mix( hash( i + vec2(0.0,0.0) ),
                                 hash( i + vec2(1.0,0.0) ), u.x),
                            mix( hash( i + vec2(0.0,1.0) ),
                                 hash( i + vec2(1.0,1.0) ), u.x), u.y);
            }

	 		float sea_octave(vec2 uv, float choppy) {
                uv += noise(uv);
                vec2 wv = 1.0-abs(sin(uv));
                vec2 swv = abs(cos(uv));
                wv = mix(wv,swv,wv);
                return pow(1.0-pow(wv.x * wv.y,0.65),choppy);
            }

            float map(vec3 p, int iteration) {
                float freq = SEA_FREQ;
                float amp = SEA_HEIGHT;
                float choppy = SEA_CHOPPY;
                vec2 uv = p.xz; uv.x *= 0.75;

                float d, h = 0.0;
                for(int i = 0; i < iteration; i++) {
                    d = sea_octave((uv+SEA_TIME)*freq,choppy);
                    d += sea_octave((uv-SEA_TIME)*freq,choppy);
                    h += d * amp;
                    uv *= octave_m; freq *= 1.9; amp *= 0.22;
                    choppy = mix(choppy,1.0,0.2);
                }
                return h;
            }
        %}

		source %{
			vec3 pos = v_vtx;
			pos.x += sin(vClock);
			pos.z += sin(vClock*0.2);
            vec3 color = SEA_BASE.xyz + SEA_WATER_COLOR.xyz * 0.12;
            color += SEA_WATER_COLOR.xyz * (map(pos, ITER_FRAGMENT) - SEA_HEIGHT) * 0.18;
			%diffuse% = color;

			%specular% = specular_color.xyz;
		%}
	}
}
