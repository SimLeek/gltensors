#version 430

uniform int width;
uniform int height;
uniform int in_channels;

layout (std430, packed, binding = 0) buffer LeftInputImage {
    float in_pixels_l[];
};

layout (std430, packed, binding = 1) buffer RightInputImage {
    float in_pixels_r[];
};

layout (std430, packed, binding = 2) buffer InputDisparity {
    int in_disparity[];
};

layout (std430, packed, binding = 3) buffer OutputDisparity {
    int out_disparity[];
};

layout (std430, packed, binding = 4) buffer RandomTime {
    float time;
};

int get_input_pixel(int input_sel, int from_x, int from_y){
    return input_sel + from_x*width*in_channels + from_y*in_channels;
}

#include "noise2D.glsl"

layout (local_size_x = 1, local_size_y = 1) in;
void main() {
    ivec2 ourPos = ivec2(gl_GlobalInvocationID.xy);
    int kernel_select;
    int input_select = ((ourPos.x)*width*in_channels)+(ourPos.y)*in_channels;
    int l_pixel_select;
    int r_pixel_select;
    int r2_pixel_select;

    float current_diff;
    r2_pixel_select = get_input_pixel(input_select, 0, -in_disparity[input_select/in_channels]);//l1

    float temp_diff = 0;
    float instdiff;
    for (int c=0; c<in_channels; c++){
            instdiff = (in_pixels_l[input_select+c] - in_pixels_r[r2_pixel_select+c]);
            temp_diff = temp_diff + instdiff*instdiff;
        }
    current_diff = temp_diff;

    out_disparity[input_select/in_channels] = in_disparity[input_select/in_channels];

    for (int i=0; i<8;i++){
        float right_rand = rnd_half_normal(vec2(ourPos.x+time, ourPos.y+time), width/3.0);
        int right_rand_sel = int(right_rand)%int(width-ourPos.y);
        r2_pixel_select = get_input_pixel(input_select, 0, -right_rand_sel);//2
        temp_diff=0;
        for (int c=0; c<in_channels; c++){
            instdiff = (in_pixels_l[input_select+c] - in_pixels_r[r2_pixel_select+c]);
            temp_diff = temp_diff + instdiff*instdiff;
        }
        if (temp_diff<current_diff){
            current_diff = temp_diff;
            out_disparity[input_select/in_channels] = right_rand_sel;
        }
    }

    //todo: kernel width is currently fixed to 3x3, but other kernals may perform better
    for (int i=-int(floor(3/2.0)); i<=floor(3/2.0); i++){
        for (int j=-int(floor(3/2.0)); j<=floor(3/2.0); j++){
            if (i==0&&j==0){
                continue;
            }
            r_pixel_select = get_input_pixel(input_select, i, j);
            r2_pixel_select = get_input_pixel(input_select, 0, -in_disparity[r_pixel_select/in_channels]);
            temp_diff=0;
            for (int c=0; c<in_channels; c++){
                instdiff = (in_pixels_l[input_select+c] - in_pixels_r[r2_pixel_select+c]);
                temp_diff = temp_diff + abs(instdiff*instdiff);
            }
            if (temp_diff<current_diff){
                current_diff = temp_diff;
                out_disparity[input_select/in_channels] = in_disparity[r_pixel_select/in_channels];
            }
        }
    }
}

