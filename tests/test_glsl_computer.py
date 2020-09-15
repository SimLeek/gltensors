import unittest as ut
import gltensors.GLSLComputer as glcpu
from gltensors.glsl_util import glsl_import_filter
import os
import difflib
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

class TestGLSLCPU(ut.TestCase):
    def setUp(self):
        self.maxDiff = None

    def testSimplexNoise(self):
        shader_file = open(os.path.abspath(os.sep.join(['..','gltensors','shaders','compute2DNoise.glsl'])))
        simplex_shader = shader_file.read()
        shader_file.close()

        simplex_shader = glsl_import_filter(simplex_shader, os.path.abspath(os.sep.join(['..','gltensors','shaders'])))

        test_computer = glcpu.GLSLComputer(simplex_shader,
                                     height=20, depth=20,
                                     min_z=5, max_z=10)

        buff = test_computer.ctx.buffer(data=np.zeros(20 * 20 * 20).astype(dtype=np.float32).tobytes())
        buff.bind_to_storage_buffer(1)
        # buff.write()

        test_computer.cpu.run(20, 20, 20)

        simplex_out = np.frombuffer(buff.read(), dtype=np.float32).reshape((20, 20, 20))

        f = open(os.sep.join(["data","glsl_cpu_simplex_noise_expected"]))
        diff = difflib.ndiff(f.read(), repr(simplex_out))
        for i, s in enumerate(diff):
            if s[0] == ' ':
                continue
            elif s[0] == '-':
                assert False, f"array does not match file: {repr(simplex_out)}"
            elif s[0] == '+':
                assert False, f"array does not match file: {repr(simplex_out)}"
        f.close()
        test_computer.ctx.release()
