export const vertexShader = `
  void main() {
    // Render full screen quad
    gl_Position = vec4(position.xy, 1.0, 1.0);
  }
`;

export const fragmentShader = `
  uniform float time;
  uniform vec2 resolution;
  uniform vec3 cameraPos;
  uniform mat4 cameraWorldMatrix;
  uniform mat4 cameraProjectionMatrixInverse;

  const int MAX_STEPS = 100;
  const float MAX_DIST = 50.0;
  const float EPSILON = 0.001;

  vec2 mandelbulbDE(vec3 pos) {
    vec3 z = pos;
    float dr = 1.0;
    float r = 0.0;
    float trap = 1e10;
    
    for (int i = 0; i < 8; i++) {
      r = length(z);
      if (r > 2.0) break;
      
      float theta = acos(z.z / r);
      float phi = atan(z.y, z.x);
      dr = pow(r, 7.0) * 8.0 * dr + 1.0;
      
      float zr = pow(r, 8.0);
      theta = theta * 8.0;
      phi = phi * 8.0;
      
      z = zr * vec3(
        sin(theta) * cos(phi),
        sin(phi) * sin(theta),
        cos(theta)
      );
      z += pos;
      
      trap = min(trap, length(z.xy));
    }
    
    return vec2(0.5 * log(r) * r / dr, trap);
  }

  vec3 rayMarch(vec3 ro, vec3 rd) {
    float t = 0.0;
    float trap = 0.0;
    
    for (int i = 0; i < MAX_STEPS; i++) {
      vec3 p = ro + rd * t;
      vec2 d = mandelbulbDE(p);
      trap = d.y;
      
      if (d.x < EPSILON) return vec3(t, trap, 1.0);
      if (t > MAX_DIST) break;
      
      t += d.x * 0.5;
    }
    
    return vec3(t, trap, 0.0);
  }

  vec3 calcNormal(vec3 p) {
    vec2 e = vec2(EPSILON, 0.0);
    return normalize(vec3(
      mandelbulbDE(p + e.xyy).x - mandelbulbDE(p - e.xyy).x,
      mandelbulbDE(p + e.yxy).x - mandelbulbDE(p - e.yxy).x,
      mandelbulbDE(p + e.yyx).x - mandelbulbDE(p - e.yyx).x
    ));
  }

  void main() {
    // Reconstruct world space ray from frustum
    vec4 ndc = vec4( (gl_FragCoord.xy / resolution.xy) * 2.0 - 1.0, 1.0, 1.0 );
    vec4 viewDir = cameraProjectionMatrixInverse * ndc;
    vec3 rd = normalize((cameraWorldMatrix * vec4(viewDir.xyz, 0.0)).xyz);
    vec3 ro = cameraPos;
    
    vec3 result = rayMarch(ro, rd);
    
    vec3 col = vec3(0.0);
    
    if (result.z > 0.5) {
      vec3 p = ro + rd * result.x;
      vec3 n = calcNormal(p);
      
      vec3 lightDir = normalize(vec3(0.5, 0.8, -1.0));
      float diff = clamp(dot(n, lightDir), 0.0, 1.0);
      
      col = mix(
        vec3(0.0, 0.2, 0.15),
        vec3(0.0, 0.8, 0.5),
        diff
      );
      
      col += vec3(pow(result.y, 0.5)) * 0.3;
      col *= 1.0 - result.x * 0.05;
    } else {
      col = vec3(0.0, 0.02, 0.03);
    }
    
    col = pow(col, vec3(0.4545));
    gl_FragColor = vec4(col, 1.0);
  }
`;
