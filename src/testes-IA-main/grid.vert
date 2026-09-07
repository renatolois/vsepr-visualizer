#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

uniform struct Material {
    mat4 transform;
    mat4 camera_view;
    mat4 camera_projection;
    vec4 color;      // adicionado
    float shininess; // adicionado
} material;

out vec3 WorldPos;

void main() {
    WorldPos = vec3(material.transform * vec4(aPos, 1.0));
    gl_Position = material.camera_projection * material.camera_view * vec4(WorldPos, 1.0);
}
