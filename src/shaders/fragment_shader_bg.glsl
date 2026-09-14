#version 330 core 


struct Material {
  mat4 transform;
  mat4 camera_view;
  mat4 camera_projection;
  sampler2D diffuse;
  vec4 color;
  float shininess;
};

in vec2 v_tex_coords;

uniform Material material;

out vec4 frag_color;

void main() {
  frag_color = texture(material.diffuse, v_tex_coords);
}
