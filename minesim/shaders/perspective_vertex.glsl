#version 430

in vec4 vert;
in vec2 texture_coord;

uniform mat4 model_view_perspective_matrix;

out vec2 v_tex_coord;

void main() {
    gl_Position = model_view_perspective_matrix * vert;
    v_tex_coord = texture_coord;
}