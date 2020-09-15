#version 430

uniform int width;
uniform int height;

uniform int in_channels;
uniform int out_channels;
uniform int kernel_width;
uniform int kernel_height;
uniform int kernel_stride_x;
uniform int kernel_stride_y;
//actually padding the array will be done elsewhere, or not at all. This indicates which areas to ignore.
//global x and y size should be smaller to deal with restricted area
uniform int kernel_padding_x;
uniform int kernel_padding_y;
uniform int kernel_dilation_x;
uniform int kernel_dilation_y;

layout (std430, packed, binding = 0) buffer InputImage {
    float in_pixels[];
};

layout (std430, binding = 1) buffer InputKernal {
    float in_kernel[];
};

#ifdef KERNEL_BIAS
layout (std430, binding = 3) buffer KernelBias {
    float out_bias[];
};
#endif

layout (std430, packed, binding = 2) buffer OutputImage {
    float out_pixels[];
};

int get_input_pixel(int input_sel, int from_x, int from_y){
    return input_sel + from_x*width*in_channels + from_y*in_channels;
}

layout (local_size_x = 1, local_size_y = 1) in;
void main() {
    ivec2 ourPos = ivec2(gl_GlobalInvocationID.xy);
    int output_select = (ourPos.x*width*out_channels)+ourPos.y*out_channels;
    int kernel_select;
    int i_f = int(floor(kernel_width/2.0));
    int j_f = int(floor(kernel_height/2.0));
    int input_select = ((ourPos.x*kernel_stride_x+kernel_padding_x+i_f)*width*in_channels)+(ourPos.y*kernel_stride_y+kernel_padding_y+j_f)*in_channels;
    int in_pixel_select;

    for (int i=-int(floor(kernel_width/2.0)); i<floor(kernel_width/2.0); i++){
        for (int j=-int(floor(kernel_height/2.0)); j<floor(kernel_height/2.0); j++){
            in_pixel_select = get_input_pixel(input_select, i, j);
            for (int co=0;co<out_channels; co++){
                for (int ci=0; ci<in_channels; ci++){
                    kernel_select = (i_f+i)*kernel_height*out_channels*in_channels+(j_f+j)*out_channels*in_channels+ci*out_channels+co;
                    out_pixels[output_select+co] += in_kernel[kernel_select]*in_pixels[in_pixel_select+ci];
                }
                #ifdef KERNEL_BIAS
                out_pixels[output_select+co] += out_bias[output_select+co];
                #endif
            }
        }
    }

}
