#version 330 core 


layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec3 a_normal;
layout(location = 2) in vec2 a_tex_coords;

struct Material {
  mat4 transform;
  mat4 camera_view;
  mat4 camera_projection;
  sampler2D diffuse;
  vec4 color;
  float shininess;
};
uniform Material material;

out vec2 v_tex_coords;

void main() {
  gl_Position = 
    material.camera_projection *
    material.camera_view *
    material.transform * 
    vec4(a_pos, 1);

  v_tex_coords = a_tex_coords;
}
