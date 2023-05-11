//https://www.geeks3d.com/20100831/shader-library-noise-and-pseudo-random-number-generator-in-glsl/
#define M_PI 3.1415926535897932384626433832795

float rnd(vec2 x)
{
    int n = int(x.x * 40.0 + x.y * 6400.0);
    n = (n << 13) ^ n;
    return 1.0 - float( (n * (n * n * 15731 + 789221) + \
             1376312589) & 0x7fffffff) / 1073741824.0;
}

float rnd_normal(vec2 x, float mu, float sigma)
{
    float u = rnd(x);
    float v = rnd(x+vec2(1,1));

    //float z1 = sqrt(-2*log(u)) * sin(2*M_PI * v);
    float z2 = sqrt(-2*log(u)) * cos(2*M_PI * v);

    //float x1 = mu + z1 * sigma;
    float x2 = mu + z2 * sigma;

    return x2;
}

float rnd_half_normal(vec2 x, float sigma)
{
    float u = rnd(x);
    float v = rnd(x+vec2(1,1));

    //float z1 = sqrt(-2*log(u)) * sin(2*M_PI * v);
    float z2 = sqrt(-2*log(u)) * cos(2*M_PI * v);

    //float x1 = abs(z1 * sigma);
    float x2 = abs(z2 * sigma);

    return x2;
}