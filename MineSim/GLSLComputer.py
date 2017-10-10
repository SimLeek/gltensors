import ModernGL
import re

class GLSLComputer(object):
    def __init__(self, compute_shader, **named_args):
        self.ctx = ModernGL.create_standalone_context()

        #self.prog = self.ctx.program([self.ctx.compute_shader(compute_shader)])

        self.cpu = self.ctx.compute_shader(compute_shader)

        #self.cpu.uniform_blocks['Output'].
        for name, value in named_args.items():
            self.cpu.uniforms[name].value = value

def glsl_import_filter(shader_str, include_dir):
    include_re = re.compile("#include\s*\"([a-zA-Z0-9\.]+)\"")

    includes = include_re.finditer(shader_str)
    for i in includes:
        shader_file = open(include_dir+i.group(1))
        addon_shader = shader_file.read()
        shader_file.close()

        shader_str_start = shader_str[0:i.span()[0]]
        shader_str_end = shader_str[i.span()[1]:]

        shader_str = shader_str_start+addon_shader+shader_str_end

    return shader_str


if __name__ == '__main__':
    import numpy as np

    shader_file = open("shaders/compute2DNoise.glsl")
    simplex_shader = shader_file.read()
    shader_file.close()

    simplex_shader = glsl_import_filter(simplex_shader, "shaders/")

    test_computer = GLSLComputer(simplex_shader,
                                 width=20, height=20, depth=20,
                                 min_z=5, max_z=10)

    buff = test_computer.ctx.buffer(data = np.zeros(20*20*20).astype(dtype=np.float32).tobytes())
    buff.bind_to_storage_buffer(1)
    #buff.write()

    test_computer.cpu.run(20,20,20)

    simplex_out = np.frombuffer(buff.read(), dtype=np.float32).reshape((20,20,20))

    print(simplex_out)
    #print([x for x in dir(test_computer.cpu.mglo)])