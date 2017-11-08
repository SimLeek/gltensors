import sys
import os

if sys.version_info[0] >= 3:
    xrange = range

from opensimplex import OpenSimplex
from minesim.GLSLComputer import *
from minesim.glsl_util import glsl_import_filter

def plains_top_inst_gen(x, z, turbulence=1):
    noise = OpenSimplex()
    height = noise.noise2d(x / (100.0 / turbulence), z / (100.0 / turbulence))
    top_h = int((height + 1) * 10)
    return [x, z, top_h * 2]

def plains_gen(width, height, depth, min_z, max_z, turbulence=1):
    import numpy as np

    script_dir = os.path.dirname(__file__)

    shader_file = open(script_dir+"/shaders/compute2DNoise.glsl")
    simplex_shader = shader_file.read()
    shader_file.close()

    simplex_shader = glsl_import_filter(simplex_shader, script_dir+"/shaders/")

    test_computer = GLSLComputer(simplex_shader,
                                 width=width, height=height, depth=depth,
                                 min_z=min_z, max_z=max_z, turbulence=turbulence)

    buff = test_computer.ctx.buffer(data = np.zeros(width*height*depth).astype(dtype=np.float32).tobytes())
    buff.bind_to_storage_buffer(1)

    test_computer.cpu.run(width,height,depth)

    simplex_out = np.frombuffer(buff.read(), dtype=np.float32).reshape((width,height,depth))
    locations_out = np.transpose(np.nonzero(simplex_out))
    return locations_out


'''def plains_gen(model, n, s, y, turbulence=1):
    for x in xrange(-n, n + 1, s):
        for z in xrange(-n, n + 1, s):
            # create a layer stone an grass everywhere.
            noise = OpenSimplex()
            height = noise.noise2d(x / (100.0 / turbulence), z / (100.0 / turbulence))
            top_h = int((height + 1) * 10)

            model.add_block((x, z, top_h), 'grass', immediate=False)'''

def stone_container_gen(width, height, depth):
    import numpy as np

    script_dir = os.path.dirname(__file__)

    shader_file = open(script_dir+"/shaders/computeContainer.glsl")
    simplex_shader = shader_file.read()
    shader_file.close()

    simplex_shader = glsl_import_filter(simplex_shader, script_dir+"/shaders/")

    test_computer = GLSLComputer(simplex_shader,
                                 width=width, height=height, depth=depth)

    buff = test_computer.ctx.buffer(data = np.zeros(width*height*depth).astype(dtype=np.float32).tobytes())
    buff.bind_to_storage_buffer(1)

    test_computer.cpu.run(width,height,depth)

    simplex_out = np.frombuffer(buff.read(), dtype=np.float32).reshape((width,height,depth))
    locations_out = np.transpose(np.nonzero(simplex_out))
    return locations_out

'''def stone_container_gen(model, n, s, y, height=20):
    for x in xrange(-n, n + 1, s):
        for z in xrange(-n, n + 1, s):
            model.add_block((x, y - 3, z), 'stone', immediate=False)

            if x in (-n, n) or z in (-n, n):
                # create outer walls.
                for dy in xrange(-2, height):
                    model.add_block((x, y + dy, z), 'stone', immediate=False)'''

def cloud_layer_gen(width, height, depth, turbulence=1, density = 0.0, dissipation_rate=.1):
    import numpy as np

    script_dir = os.path.dirname(__file__)

    shader_file = open(script_dir+"/shaders/compute3DNoiseLayer.glsl")
    simplex_shader = shader_file.read()
    shader_file.close()

    simplex_shader = glsl_import_filter(simplex_shader, script_dir+"/shaders/")

    test_computer = GLSLComputer(simplex_shader,
                                 width=width, height=height, depth=depth,
                                 turbulence=turbulence, density=density, dissipation_rate=dissipation_rate)

    buff = test_computer.ctx.buffer(data = np.zeros(width*height*depth).astype(dtype=np.float32).tobytes())
    buff.bind_to_storage_buffer(1)

    test_computer.cpu.run(width,height,depth)

    simplex_out = np.frombuffer(buff.read(), dtype=np.float32).reshape((width,height,depth))
    locations_out = np.transpose(np.nonzero(simplex_out))
    return locations_out

def inverse_cloud_layer_gen(width, height, depth, turbulence=1, density = 0.0, dissipation_rate=.1):
    import numpy as np

    script_dir = os.path.dirname(__file__)

    shader_file = open(script_dir+"/shaders/compute3DNoiseLayer.glsl")
    simplex_shader = shader_file.read()
    shader_file.close()

    simplex_shader = glsl_import_filter(simplex_shader, script_dir+"/shaders/")

    test_computer = GLSLComputer(simplex_shader,
                                 width=width, height=height, depth=depth,
                                 turbulence=turbulence, density=density, dissipation_rate=dissipation_rate)

    buff = test_computer.ctx.buffer(data = np.zeros(width*height*depth).astype(dtype=np.float32).tobytes())
    buff.bind_to_storage_buffer(1)

    test_computer.cpu.run(width,height,depth)

    simplex_out = 1 - np.frombuffer(buff.read(), dtype=np.float32).reshape((width,height,depth))
    locations_out = np.transpose(np.nonzero(simplex_out))
    return locations_out

'''def cloud_layer_gen(model, n, s, y, size=1, density=0, min_height=20, max_height=40, cloud_height=30,
                    dissipation_rate=.1):
    for x in xrange(-n, n + 1, s):
        for z in xrange(-n, n + 1, s):
            noise = OpenSimplex()

            for h in xrange(min_height, max_height):
                if noise.noise3d(x / (10.0 * size), z / (10.0 * size), h / (3.0 * size)) > density + abs(
                                h - cloud_height) * dissipation_rate:
                    model.add_block((x, h, z), 'cloud', immediate=False)'''


def foam_gen(model, n, s, y, height=40, size=1, density=0):  # 0 is half density, 1 is empty, -1 is full
    for x in xrange(-n, n + 1, s):
        for z in xrange(-n, n + 1, s):
            noise = OpenSimplex()

            for h in xrange(y - 1, height):
                if noise.noise3d(x / (10.0 * size), z / (10.0 * size), h / (3.0 * size)) > density:
                    model.add_block((x, h, z), 'aluminum', immediate=False)


def cave_dig(model, n, s, y, size=1, density=.6):  # 0 is half density, 1 is empty, -1 is full
    for x in xrange(-n, n + 1, s):
        for z in xrange(-n, n + 1, s):
            noise = OpenSimplex()

            for h in xrange(y - 1, 20):
                if noise.noise3d(x / (10.0 * size), z / (10.0 * size), h / (3.0 * size)) > density:
                    if (x, h, z) in model.world:
                        model.remove_block((x, h, z), immediate=False)
