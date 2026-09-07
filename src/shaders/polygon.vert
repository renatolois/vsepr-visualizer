#version 330 core

layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec3 a_normal;

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

out vec3 frag_pos;
out vec3 normal;
out vec2 v_tex_coords;

void main() {
  vec4 world_pos = material.transform * vec4(a_pos, 1.0);
  frag_pos = world_pos.xyz;
  normal = mat3(transpose(inverse(material.transform))) * a_normal;
  gl_Position = material.camera_projection * material.camera_view * world_pos;
}
