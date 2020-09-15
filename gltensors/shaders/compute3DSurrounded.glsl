#version 430

uniform int width;
uniform int height;
uniform int depth;
uniform bool show_bounds;

layout (std430, binding = 0) buffer InputOccupied {
    float occupied[];
};

layout (std430, binding = 1) buffer InputBlocking {
    float blocking[];
};

layout (std430, binding = 2) buffer OutputVisible {
    float visible[];
};

layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
void main() {
     ivec3 resolution = ivec3(width, height, depth);
     ivec3 ourPos = ivec3(gl_GlobalInvocationID.xyz);
     int index = (ourPos.x*depth*height)+(ourPos.y*depth)+ourPos.z;

     int move_x = depth*height;
     int move_y = depth;
     int move_z = 1;

     bool at_bounds = ourPos.x==0 || ourPos.y==0 || ourPos.z==0 ||
        ourPos.x==width-1 || ourPos.y==height-1 || ourPos.z==depth-1;

     if(occupied[index]==1){
        if(at_bounds){
            if(show_bounds){
                visible[index] = 1;
            }
            else{
                visible[index] = 0;
            }
        }
        else{
            if(blocking[index+move_x]==1 && blocking[index-move_x]==1 &&
               blocking[index+move_y]==1 && blocking[index-move_y]==1 &&
               blocking[index+move_z]==1 && blocking[index-move_z]==1){
                visible[index] = 0;
               }
            else{
                visible[index] = 1;
            }
        }
     }
     else{
        visible[index] = 0;
     }

}
