#version 430

//layout(location = 0) uniform float roll;

uniform int width;
uniform int height;
uniform int depth;

uniform float turbulence;


uniform int max_z;
uniform int min_z;


#include "simplex2D.glsl"

layout (std430, binding = 1) buffer Output {
    float outy[];
};

//needs to be 1,1,1, unless you know your input is divideable
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
void main() {
     ivec3 resolution = ivec3(width, height, depth);
     ivec3 storePos = ivec3(gl_GlobalInvocationID.xyz);
     vec2 terrainPos = vec2(gl_GlobalInvocationID.xy);
     uint height_pos = gl_GlobalInvocationID.z;

     int height_z = max_z-min_z;


     int access_pos = (storePos.x*depth*height)+(storePos.y*depth)+storePos.z;

     if(snoise2(terrainPos*turbulence)*height_z + min_z > height_pos){
        outy[access_pos]=1;
     }else{
        outy[access_pos]=0;
     }

 }