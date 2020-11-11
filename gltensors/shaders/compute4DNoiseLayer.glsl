#version 430

//layout(location = 0) uniform float roll;

uniform int width;
uniform int height;
uniform int depth;
uniform int time;

uniform float turbulence;
uniform float density;
uniform float dissipation_rate;


#include "simplex4D.glsl"

layout (std430, binding = 1) buffer Output {
    float outy[];
};

//needs to be 1,1,1, unless you know your input is divideable
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
void main() {
     vec4 storePos = vec4(gl_GlobalInvocationID.xyz, time);
     uint height_pos = gl_GlobalInvocationID.z;

     uint center_pos = depth/2;

     int access_pos = int((storePos.x*depth*height)+(storePos.y*depth)+storePos.z);

     if(snoise4(storePos*turbulence) + density > 0 +distance(height_pos, center_pos) * dissipation_rate){
        outy[access_pos]=1;
     }else{
        outy[access_pos]=0;
     }

 }