#version 430

in vec4 vert;
in vec2 texture_coord;
in vec4 rgba_multiplier;

uniform float BarrelPower;

uniform mat4 model_view_perspective_matrix;

out vec2 v_tex_coord;
out vec4 v_rgba_mult;

vec4 distort(vec4 p)
{
    vec2 v = p.xy / p.w;
    // Convert to polar coords:
    float radius = length(v);
    if (radius > 0)
    {
        float theta = atan(v.y, v.x);

        // Distort:
        radius = pow(radius, BarrelPower);

        // Convert back to Cartesian:
        v.x = radius * cos(theta);
        v.y = radius * sin(theta);
        p.xy = v.xy * p.w;
    }
    return p;
}

void main() {
    vec4 p = model_view_perspective_matrix * vert;
    gl_Position = distort(p);
    v_tex_coord = texture_coord;
    v_rgba_mult = rgba_multiplier;
}