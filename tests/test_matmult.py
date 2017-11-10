import unittest as ut

import numpy as np
np.set_printoptions(threshold=np.nan)

class TestGLSLCPU(ut.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_id_mat(self):
