#version 430

in vec4 vert;
in vec2 texture_coord;

uniform mat4 uniform_transform;
layout (std430, binding = 0) buffer InputTranslations {
    vec3 translations[];
};

layout (std430, binding = 1) buffer InputBlocking {
    float blocking[];
};

layout (std430, binding = 2) buffer OutputVisible {
    float visible[];
};

void mass_translate() {

}
