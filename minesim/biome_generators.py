import sys
import os

import numpy as np

script_dir = os.path.dirname(__file__)

if sys.version_info[0] >= 3:
    xrange = range

from opensimplex import OpenSimplex
from minesim.GLSLComputer import *
from minesim.glsl_util import glsl_import_filter

def read_in_file(*shader_file):
    shader_file = open(script_dir+os.sep+os.sep.join(shader_file))
    shader_text = shader_file.read()
    shader_file.close()

    return shader_text

def read_in_shader(*shader_file):
    simplex_shader = read_in_file(*shader_file)
    simplex_shader = glsl_import_filter(simplex_shader,
                                        script_dir+
                                        os.sep+"shaders"+os.sep)
    return simplex_shader

def get_locations(bit_array  # type: np.ndarray
                  ):
    locations_out = np.transpose(np.nonzero(bit_array))
    return locations_out

def plains_gen(width, height, depth, min_z, max_z, turbulence=1):
    test_computer = GLSLComputer(read_in_shader("shaders", "compute2DNoise.glsl"),
                                 width=width, height=height, depth=depth,
                                 min_z=min_z, max_z=max_z, turbulence=turbulence)

    buff = test_computer.ctx.buffer(data = np.zeros(width*height*depth).astype(dtype=np.float32).tobytes())
    buff.bind_to_storage_buffer(1)

    test_computer.cpu.run(width,height,depth)

    simplex_out = np.frombuffer(buff.read(), dtype=np.float32).reshape((width,height,depth)) # type: np.ndarray
    simplex_out.setflags(write=True)
    return simplex_out


def stone_container_gen(width, height, depth):
    test_computer = GLSLComputer(read_in_shader("shaders", "computeContainer.glsl"),
                                 width=width, height=height, depth=depth)

    buff = test_computer.ctx.buffer(data = np.zeros(width*height*depth).astype(dtype=np.float32).tobytes())
    buff.bind_to_storage_buffer(1)

    test_computer.cpu.run(width,height,depth)

    simplex_out = np.frombuffer(buff.read(), dtype=np.float32).reshape((width,height,depth))
    simplex_out.setflags(write=True)
    return simplex_out

def cloud_layer_gen(width, height, depth, turbulence=1, density = 0.0, dissipation_rate=.1):
    test_computer = GLSLComputer(read_in_shader("shaders", "compute3DNoiseLayer.glsl"),
                                 width=width, height=height, depth=depth,
                                 turbulence=turbulence, density=density, dissipation_rate=dissipation_rate)

    buff = test_computer.ctx.buffer(data = np.zeros(width*height*depth).astype(dtype=np.float32).tobytes())
    buff.bind_to_storage_buffer(1)

    test_computer.cpu.run(width,height,depth)

    simplex_out = np.frombuffer(buff.read(), dtype=np.float32).reshape((width,height,depth))
    simplex_out.setflags(write=True)
    return simplex_out.astype(np.bool_)

def inverse_cloud_layer_gen(width, height, depth, turbulence=1, density = 0.0, dissipation_rate=.1):
    test_computer = GLSLComputer(read_in_shader("shaders", "compute3DNoiseLayer.glsl"),
                                 width=width, height=height, depth=depth,
                                 turbulence=turbulence, density=density, dissipation_rate=dissipation_rate)

    buff = test_computer.ctx.buffer(data = np.zeros(width*height*depth).astype(dtype=np.float32).tobytes())
    buff.bind_to_storage_buffer(1)

    test_computer.cpu.run(width,height,depth)

    simplex_out = 1 - np.frombuffer(buff.read(), dtype=np.float32).reshape((width,height,depth))
    simplex_out.setflags(write=True)
    return simplex_out



def restrict_visible(blocking_spaces,  # type: np.ndarray
                     occupied_spaces,  # type: np.ndarray
                     show_bounds = False
                     ):
    if not isinstance(blocking_spaces, np.ndarray) or not isinstance(occupied_spaces, np.ndarray):
        raise TypeError("inputs should be numpy ndarrays.")
    if blocking_spaces.ndim != 3 or occupied_spaces.ndim != 3:
        raise ValueError("inputs should be 3-dimensional arrays.")
    if blocking_spaces.shape[0] != occupied_spaces.shape[0] or \
       blocking_spaces.shape[1] != occupied_spaces.shape[1] or \
       blocking_spaces.shape[2] != occupied_spaces.shape[2]:
        raise ValueError("inputs arrays should have same shape.")

    test_computer = GLSLComputer(read_in_shader("shaders", "compute3DSurrounded.glsl"),
                                 width=blocking_spaces.shape[0],
                                 height=blocking_spaces.shape[1],
                                 depth=blocking_spaces.shape[2],
                                 show_bounds = show_bounds
                                 )

    buff_occupied = test_computer.ctx.buffer(data=occupied_spaces.astype(dtype=np.float32).tobytes())
    buff_occupied.bind_to_storage_buffer(0)

    buff_blocking = test_computer.ctx.buffer(data=blocking_spaces.astype(dtype=np.float32).tobytes())
    buff_blocking.bind_to_storage_buffer(1)

    buff_visible = test_computer.ctx.buffer(data=np.zeros(blocking_spaces.shape).astype(dtype=np.float32).tobytes())
    buff_visible.bind_to_storage_buffer(2)

    test_computer.cpu.run(*blocking_spaces.shape)

    visibility_array = np.frombuffer(
        buff_visible.read(),
        dtype=np.float32
    ).reshape(blocking_spaces.shape)

    visibility_array.setflags(write=True)
    return visibility_array

