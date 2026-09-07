#version 330 core
layout (location = 0) in vec3 a_pos;
layout (location = 1) in vec3 a_normal;

uniform struct Material {
    mat4 transform;
    mat4 camera_view;
    mat4 camera_projection;
    vec4 color;
    float shininess;
} material;

out vec3 world_pos;

void main() {
  world_pos = vec3(material.transform * vec4(a_pos, 1.0));
  gl_Position = material.camera_projection * material.camera_view * vec4(world_pos, 1.0);
}

