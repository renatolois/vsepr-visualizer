#version 330 core

layout(location = 0) in vec3 a_position;

uniform mat4 material_transform;
uniform mat4 material_camera_view;
uniform mat4 material_camera_projection;

void main() {
    gl_Position = material_camera_projection
                * material_camera_view
                * material_transform
                * vec4(a_position, 1.0);
}
