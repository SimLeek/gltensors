#version 450
#extension GL_KHR_shader_subgroup_arithmetic : enable
#extension GL_KHR_vulkan_glsl : enable

# define KERNEL_SIZE 1024

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
// backpropogation must be padded as well
uniform int kernel_padding_x;
uniform int kernel_padding_y;
uniform int kernel_dilation_x;
uniform int kernel_dilation_y;

layout (std430, binding = 4) buffer DInputImage {
    float d_in_pixels[];
};

layout (std430, binding = 5) buffer DInputKernal {
    float d_in_kernel[];
};

#ifdef KERNEL_BIAS
layout (std430, binding = 9) buffer DKernelBias {
    float d_bias[];
};
#endif

layout (std430, binding = 6) buffer DOutputImage {
    float d_out_pixels[];
};

layout (std430, binding = 7) buffer InputImage {
    float in_pixels[];
};

layout (std430, binding = 8) buffer InputKernal {
    float in_kernel[];
};

#ifdef KERNEL_BIAS
layout (std430, binding = 10) buffer KernelBias {
    float bias[];
};
#endif

int get_input_pixel(int input_sel, int from_x, int from_y){
    return input_sel + from_x*width*in_channels + from_y*in_channels;
}

layout (constant_id = 2) const int sumSubGroupSize = 64;
shared float sdata[KERNEL_SIZE];

layout (local_size_x = 1, local_size_y = 1) in;
void main() {
    ivec2 ourPos = ivec2(gl_GlobalInvocationID.xy);
    int output_select = (ourPos.x*width*out_channels)+ourPos.y*out_channels;
    int kernel_select;
    int kernel_select_t;
    int i_f = int(floor(kernel_width/2.0));
    int j_f = int(floor(kernel_height/2.0));
    int input_select = ((ourPos.x*kernel_stride_x+kernel_padding_x+i_f)*width*in_channels)+(ourPos.y*kernel_stride_y+kernel_padding_y+j_f)*in_channels;
    int out_pixel_select;

    float d_local_kernel[KERNEL_SIZE];  // automatically initializes to 0: https://www.reddit.com/r/opengl/comments/5cgkkk/how_to_initialize_a_very_large_array_in_a_compute/?ref=share&ref_source=link

    for (int i=-int(floor(kernel_width/2.0)); i<floor(kernel_width/2.0); i++){
        for (int j=-int(floor(kernel_height/2.0)); j<floor(kernel_height/2.0); j++){
            out_pixel_select = get_input_pixel(output_select, i, j);
            for (int co=0;co<out_channels; co++){
                for (int ci=0; ci<in_channels; ci++){
                    kernel_select = (i_f+i)*kernel_height*out_channels*in_channels+(j_f+j)*out_channels*in_channels+ci*out_channels+co;
                    kernel_select_t = (i_f-i-1)*kernel_height*out_channels*in_channels+(j_f-j-1)*out_channels*in_channels+ci*out_channels+co;
                    d_in_pixels[input_select+ci] += d_out_pixels[out_pixel_select+co] * in_kernel[kernel_select_t];
                    d_local_kernel[kernel_select] += in_pixels[input_select+ci] * d_out_pixels[out_pixel_select+co];
                    // map reduce for kernel
                    d_local_kernel[kernel_select] = subgroupAdd(d_local_kernel[kernel_select]);
                    if (gl_SubgroupInvocationID == 0)
                    {
                        sdata[gl_SubgroupID*kernel_select] = d_local_kernel[kernel_select];
                    }
                    memoryBarrierShared();
                    barrier();
                    if (gl_SubgroupID == 0)
                    {
                        d_local_kernel[kernel_select] = gl_SubgroupInvocationID < gl_NumSubgroups ? sdata[gl_SubgroupInvocationID*kernel_select] : 0;
                        d_local_kernel[kernel_select] = subgroupAdd(d_local_kernel[kernel_select]);
                    }

                    if (gl_LocalInvocationID.x == 0 && gl_LocalInvocationID.y == 0)
                    {
                        d_in_kernel[kernel_select] = d_local_kernel[kernel_select];
                    }
                    // end map reduce
                }
                #ifdef KERNEL_BIAS
                d_bias[out_pixel_select+co] += d_out_pixels[out_pixel_select+co];
                #endif
            }
        }
    }
}
