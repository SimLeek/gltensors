#version 430

in vec4 vert;
in vec2 texture_coord;
in vec4 rgba_multiplier;

uniform mat4 model_view_perspective_matrix;

out vec2 v_tex_coord;
out vec4 v_rgba_mult;

void main() {
    gl_Position = model_view_perspective_matrix * vert;
    v_tex_coord = texture_coord;
    v_rgba_mult = rgba_multiplier;
}