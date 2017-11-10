#version 430

in vec3 vert;
uniform mat4 model_view_perspective_matrix;

void main() {
    gl_Position = model_view_perspective_matrix * vec4(vert, 1.0);
}