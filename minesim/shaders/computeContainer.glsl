#version 430

//layout(location = 0) uniform float roll;

uniform int width;
uniform int height;
uniform int depth;

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

     int access_pos = (storePos.x*depth*height)+(storePos.y*depth)+storePos.z;

     if(storePos.x==0 || storePos.y==0 || storePos.z==0 ||
        storePos.x==width-1 || storePos.y==height-1){
        outy[access_pos]=1;
     }else{
        outy[access_pos]=0;
     }

 }