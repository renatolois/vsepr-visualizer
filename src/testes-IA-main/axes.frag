#version 330 core

uniform vec4 material_color;

out vec4 frag_color;

void main() {
    frag_color = material_color;
}
