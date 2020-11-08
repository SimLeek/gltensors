#version 430
uniform int num_positions;
uniform int num_faces;
uniform int num_verts;
uniform int num_texs;
uniform int floats_per_vert;

layout (std430, packed, binding = 0) buffer InputVerts {
    float in_verts[];
};

layout (std430, packed, binding = 1) buffer InputTexUv {
    float in_tex_uv[];
};

layout (std430, packed, binding = 2) buffer InputPositions {
    float in_positions[];
};

layout (std430, packed, binding = 3) buffer InputColors {
    float in_colors[];
};

layout (std430, packed, binding = 4) buffer OutputPack {
    float out_pack[];
};

layout (local_size_x = 1, local_size_y = 1) in;
void main() {
    ivec2 ourPos = ivec2(gl_GlobalInvocationID.xy);
    int output_select = (ourPos.x*num_faces)+ourPos.y;
    out_pack[(output_select)*10] = in_verts[(ourPos.y)*3] + in_positions[ourPos.x*3]*2.0;
    out_pack[(output_select)*10+1] = in_verts[(ourPos.y)*3+1] + in_positions[ourPos.x*3+1]*2.0;
    out_pack[(output_select)*10+2] = in_verts[(ourPos.y)*3+2] + in_positions[ourPos.x*3+2]*2.0;
    out_pack[(output_select)*10+3] = 1.0f;
    out_pack[(output_select)*10+4] = in_tex_uv[(ourPos.y)*2];
    out_pack[(output_select)*10+5] = in_tex_uv[(ourPos.y)*2+1];
    // Arbitrary colors based on position.
    // Todo: use the in_colors array to determine colors
    out_pack[(output_select)*10+6] = abs(.5f*(out_pack[(output_select)*10]*.01)+.5);
    out_pack[(output_select)*10+7] = abs(.5f*(out_pack[(output_select)*10+1]*.01)+.5);
    out_pack[(output_select)*10+8] = abs(.5f*(out_pack[(output_select)*10+2]*.01)+.5);
    out_pack[(output_select)*10+9] = 1.0f;
}
