import unittest as ut
import minesim.GLSLComputer as glcpu
from minesim.glsl_util import glsl_import_filter

import numpy as np
np.set_printoptions(threshold=np.nan)

class TestGLSLCPU(ut.TestCase):
    def setUp(self):
        self.maxDiff = None

    def testSimplexNoise(self):
        shader_file = open("../minesim/shaders/compute2DNoise.glsl")
        simplex_shader = shader_file.read()
        shader_file.close()

        simplex_shader = glsl_import_filter(simplex_shader, "../minesim/shaders/")

        test_computer = glcpu.GLSLComputer(simplex_shader,
                                     width=20, height=20, depth=20,
                                     min_z=5, max_z=10)

        buff = test_computer.ctx.buffer(data=np.zeros(20 * 20 * 20).astype(dtype=np.float32).tobytes())
        buff.bind_to_storage_buffer(1)
        # buff.write()

        test_computer.cpu.run(20, 20, 20)

        simplex_out = np.frombuffer(buff.read(), dtype=np.float32).reshape((20, 20, 20))

        f = open("glsl_cpu_simplex_noise_expected")
        self.assertMultiLineEqual(f.read(), repr(simplex_out))
