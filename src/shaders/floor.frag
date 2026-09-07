#version 330 core
in vec3 world_pos;
uniform vec3 camera_pos;

uniform struct Material {
    mat4 transform;
    mat4 camera_view;
    mat4 camera_projection;
    vec4 color;
    float shininess;
} material;

out vec4 frag_color;

void main() {
    float step_value = 1.0;
    vec2 uv = world_pos.xz / step_value;
    vec2 f = abs(fract(uv - 0.5) - 0.5);
    vec2 df = fwidth(uv);
    float line = 1.0 - min(1.0, min(f.x / df.x, f.y / df.y));

    vec3 line_color = vec3(0.7, 0.7, 0.7);
    vec3 bg_color = vec3(0.15, 0.15, 0.15);
    vec3 color = mix(bg_color, line_color, line);

    float dist = length(world_pos.xz - camera_pos.xz);
    float fade_start = 5.0;
    float fade_end = 30.0;
    float fade = 1.0 - smoothstep(fade_start, fade_end, dist);

    frag_color = vec4(color * fade, 1.0);
}
