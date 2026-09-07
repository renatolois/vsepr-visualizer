#version 330 core
in vec3 WorldPos;
uniform vec3 CameraPos;

uniform struct Material {
    mat4 transform;
    mat4 camera_view;
    mat4 camera_projection;
    vec4 color;
    float shininess;
} material;

uniform struct Light {
    vec3 translation;
    vec3 color;
    float intensity;
} light;

out vec4 FragColor;

void main() {
    float gridSize = 1.0;
    vec2 uv = WorldPos.xz / gridSize;
    vec2 f = abs(fract(uv - 0.5) - 0.5);
    vec2 df = fwidth(uv);
    float line = 1.0 - min(1.0, min(f.x / df.x, f.y / df.y));

    vec3 lineColor = vec3(0.7, 0.7, 0.7);
    vec3 bgColor = vec3(0.15, 0.15, 0.15);
    vec3 color = mix(bgColor, lineColor, line);

    float dist = length(WorldPos.xz - CameraPos.xz);
    float fadeStart = 5.0;
    float fadeEnd = 30.0;
    float fade = 1.0 - smoothstep(fadeStart, fadeEnd, dist);

    FragColor = vec4(color * fade, 1.0);
}
