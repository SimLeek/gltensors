#version 430

in vec2 v_tex_coord;
in vec4 v_rgba_mult;

uniform sampler2D texture_1;

out vec4 color;

void main() {
    color = vec4(texture(texture_1, v_tex_coord).rgb, 1.0)*v_rgba_mult;
}