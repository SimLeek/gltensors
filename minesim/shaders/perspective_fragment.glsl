#version 430

uniform sampler2D texture_1;
//uniform mat4 model_view_perspective_matrix;

in vec2 v_tex_coord;

out vec4 color;

void main() {
    color = vec4(.1,.1,.1,1.0);
    //color = vec4(texture(texture_1, v_tex_coord).rgb, 1.0);
}