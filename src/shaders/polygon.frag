#version 330 core

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

uniform sampler2D diffuse;

in vec2 v_tex_coords;
in vec3 frag_pos;
in vec3 normal;

out vec4 frag_color;

void main() {
  vec3 ambient = 0.2 * material.color.rgb;
  vec3 norm = normalize(normal);
  vec3 light_dir = normalize(light.translation - frag_pos);
  float diff = max(dot(norm, light_dir), 0.0);
  vec3 diffuse = light.intensity * light.color * diff * material.color.rgb;

  vec3 result = ambient + diffuse;
  frag_color = vec4(result, material.color.a);
}
