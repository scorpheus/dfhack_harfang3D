in {
	int ITER_GEOMETRY = 1;
    int ITER_FRAGMENT = 4;
    float SEA_HEIGHT = 0.3;
    float SEA_CHOPPY = 2.0;
    float SEA_SPEED = 0.1;
    float SEA_FREQ = 0.4;
    vec4 SEA_BASE = vec4(0.1, 0.19, 0.22, 1.0) [hint:color];
    vec4 SEA_WATER_COLOR = vec4(0.8, 0.9, 0.6, 1.0) [hint:color];
}

variant {

	vertex {
		out {
			vec3 v_vtx;
			vec3 v_normal;
			vec3 v_tangent;
			vec3 v_bitangent;
		}

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

            // sky
            vec3 getSkyColor(vec3 e) {
                e.z = max(e.z,0.0);
                vec3 ret;
                ret.x = pow(1.0-e.z,2.0);
                ret.y = 1.0-e.z;
                ret.z = 0.6+(1.0-e.z)*0.4;
                return ret;
            }

            // sea
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
                vec2 uv = p.xy; uv.x *= 0.75;

                float d, h = 0.0;
                for(int i = 0; i < iteration; i++) {
                    d = sea_octave((uv+SEA_TIME)*freq,choppy);
                    d += sea_octave((uv-SEA_TIME)*freq,choppy);
                    h += d * amp;
                    uv *= octave_m; freq *= 1.9; amp *= 0.22;
                    choppy = mix(choppy,1.0,0.2);
                }
                return p.z - h;
            }

            vec3 getSeaColor(vec3 p, vec3 n, vec3 eye, vec3 dist) {
                float fresnel = 1.0 - max(dot(n,-eye),0.0);
                fresnel = pow(fresnel,3.0) * 0.65;

                vec3 reflected = getSkyColor(reflect(eye,n));
                vec3 refracted = SEA_BASE.xyz + SEA_WATER_COLOR.xyz * 0.12;

               vec3 color = mix(refracted,reflected,fresnel);

                float atten = max(1.0 - dot(dist,dist) * 0.001, 0.0);
                color += SEA_WATER_COLOR.xyz * (p.z - SEA_HEIGHT) * 0.18 * atten;

                return color;
            }

            // tracing
            vec3 getNormal(vec3 p, float eps) {
                vec3 n;
                n.z = map(p, ITER_FRAGMENT);
                n.x = map(vec3(p.x+eps,p.y,p.z), ITER_FRAGMENT) - n.z;
                n.y = map(vec3(p.x,p.y+eps,p.z), ITER_FRAGMENT) - n.z;
                n.z = eps;
                return normalize(n);
            }

            float heightMapTracing(vec3 ori, vec3 dir, out vec3 p) {
                float tm = 0.0;
                float tx = 1000.0;
                float hx = map(ori + dir * tx, ITER_GEOMETRY);
                if(hx > 0.0) return tx;
                float hm = map(ori + dir * tm, ITER_GEOMETRY);
                float tmid = 0.0;
                for(int i = 0; i < NUM_STEPS; i++) {
                    tmid = mix(tm,tx, hm/(hm-hx));
                    p = ori + dir * tmid;
                    float hmid = map(p, ITER_GEOMETRY);
                    if(hmid < 0.0) {
                        tx = tmid;
                        hx = hmid;
                    } else {
                        tm = tmid;
                        hm = hmid;
                    }
                }
                return tmid;
            }
        %}

		source %{
			v_vtx = vPosition;

			v_normal = vNormal;
			v_tangent = vTangent;
			v_bitangent = vBitangent;

			mat3 tangent_matrix = _build_mat3(normalize(v_tangent), normalize(v_bitangent), normalize(v_normal));

			// compute the pixel to view direction in tangent space
			vec4 model_view_pos = _mtx_mul(vInverseModelMatrix, vViewPosition);
			vec3 view_dir = normalize(v_vtx - model_view_pos.xyz);

			vec3 tangent_view_dir = normalize(_mtx_mul(transpose(tangent_matrix), view_dir));

			vec3 p;
			vec3 ori = _mtx_mul(transpose(tangent_matrix), model_view_pos.xyz);
			heightMapTracing(ori, tangent_view_dir, p);

			%position% = vec4(vPosition + p.z * vNormal, 1.0);
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

            // sky
            vec3 getSkyColor(vec3 e) {
                e.z = max(e.z,0.0);
                vec3 ret;
                ret.x = pow(1.0-e.z,2.0);
                ret.y = 1.0-e.z;
                ret.z = 0.6+(1.0-e.z)*0.4;
                return ret;
            }

            // sea
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
                vec2 uv = p.xy; uv.x *= 0.75;

                float d, h = 0.0;
                for(int i = 0; i < iteration; i++) {
                    d = sea_octave((uv+SEA_TIME)*freq,choppy);
                    d += sea_octave((uv-SEA_TIME)*freq,choppy);
                    h += d * amp;
                    uv *= octave_m; freq *= 1.9; amp *= 0.22;
                    choppy = mix(choppy,1.0,0.2);
                }
                return p.z - h;
            }

            vec3 getSeaColor(vec3 p, vec3 n, vec3 eye, vec3 dist) {
                float fresnel = 1.0 - max(dot(n,-eye),0.0);
                fresnel = pow(fresnel,3.0) * 0.65;

                vec3 reflected = getSkyColor(reflect(eye,n));
                vec3 refracted = SEA_BASE.xyz + SEA_WATER_COLOR.xyz * 0.12;

               vec3 color = mix(refracted,reflected,fresnel);

                float atten = max(1.0 - dot(dist,dist) * 0.001, 0.0);
                color += SEA_WATER_COLOR.xyz * (p.z - SEA_HEIGHT) * 0.18 * atten;

                return color;
            }

            // tracing
            vec3 getNormal(vec3 p, float eps) {
                vec3 n;
                n.z = map(p, ITER_FRAGMENT);
                n.x = map(vec3(p.x+eps,p.y,p.z), ITER_FRAGMENT) - n.z;
                n.y = map(vec3(p.x,p.y+eps,p.z), ITER_FRAGMENT) - n.z;
                n.z = eps;
                return normalize(n);
            }

            float heightMapTracing(vec3 ori, vec3 dir, out vec3 p) {
                float tm = 0.0;
                float tx = 1000.0;
                float hx = map(ori + dir * tx, ITER_GEOMETRY);
                if(hx > 0.0) return tx;
                float hm = map(ori + dir * tm, ITER_GEOMETRY);
                float tmid = 0.0;
                for(int i = 0; i < NUM_STEPS; i++) {
                    tmid = mix(tm,tx, hm/(hm-hx));
                    p = ori + dir * tmid;
                    float hmid = map(p, ITER_GEOMETRY);
                    if(hmid < 0.0) {
                        tx = tmid;
                        hx = hmid;
                    } else {
                        tm = tmid;
                        hm = hmid;
                    }
                }
                return tmid;
            }
        %}

		source %{
			mat3 tangent_matrix = _build_mat3(normalize(v_tangent), normalize(v_bitangent), normalize(v_normal));

			// compute the pixel to view direction in tangent space
			vec4 model_view_pos = _mtx_mul(vInverseModelMatrix, vViewPosition);
			vec3 view_dir = normalize(v_vtx - model_view_pos.xyz);

			vec3 tangent_view_dir = normalize(_mtx_mul(transpose(tangent_matrix), view_dir));

			vec3 p;
			vec3 ori = _mtx_mul(transpose(tangent_matrix), model_view_pos.xyz);
			heightMapTracing(ori, tangent_view_dir, p);

			vec3 dist = p - ori;
            vec3 n = getNormal(p, dot(dist, dist) * EPSILON_NRM);

			vec3 color = getSeaColor(p, n, tangent_view_dir, dist);
			%diffuse% = vec3(pow(color, vec3(0.75)));
		%}
	}
}