#version 430 //because SSBOs :D

#extension GL_ARB_shader_storage_buffer_object : require

in vec4 vertex;
in vec2 texture_coord;
//in vec2 tex_coord;

out vec2 v_tex_coord;
//uniform mat4 model_view_matrix;
uniform mat4 model_view_perspective_matrix;

//in normal;
//out v_normal;
//out v

layout (std430, binding = 2) buffer shader_data
{
    mat4 instance_transform_matrix[];
};

void main() {
    mat4 transform = instance_transform_matrix[gl_InstanceID];
    //mat4 unused_mat = model_view_matrix;
    gl_Position = model_view_perspective_matrix * (vertex * transform);
    //v =  (model_view_matrix * (vertex * transform)).xyz; // Convert the vertex in the View space with the instanciation matrix (transform)
    //vec3 instanciednormal = (vec4(p3d_Normal,0.0) * transform).xyz;
    //mynormal = normalize(gl_NormalMatrix * instanciednormal);
    v_tex_coord = texture_coord;
}