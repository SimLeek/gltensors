import ModernGL
from ModernGL.ext.examples import run_example
import numpy as np
import minesim.matmult as mm
import math as m
"""
    Renders a blue triangle
"""
from PyQt5 import QtOpenGL, QtCore,QtWidgets
from functools import wraps
import ModernGL
import os
import traceback
import types

from minesim.glsl_window import *
#https://stackoverflow.com/a/19015654/782170
def MyPyQtSlot(*args):
    if len(args) == 0 or isinstance(args[0], types.FunctionType):
        args = []
    @QtCore.pyqtSlot(*args)
    def slotdecorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args)
            except:
                print("Uncaught Exception in slot[{}].".format(func.__name__))
                traceback.print_exc()
        return wrapper

    return slotdecorator

class PerspectiveWindow(GLSLWindow):

    def __init__(self):
        super(PerspectiveWindow, self).__init__(vertex_shader_file = os.path.dirname(os.path.realpath(__file__))+os.sep+'shaders'+os.sep+'perspective_vertex.glsl',
                                                fragment_shader_file = os.path.dirname(os.path.realpath(__file__))+os.sep+'shaders'+os.sep+'perspective_fragment.glsl',
                                                uniform_dict = None
        )

    @MyPyQtSlot("bool")
    def initializeGL(self,
            new_vertex_shader_file=None,
            new_fragment_shader_file=None,
            new_uniform_dict = None):
        super(PerspectiveWindow, self).initializeGL(
            new_vertex_shader_file=None,
            new_fragment_shader_file=None,
            new_uniform_dict = None)

        self.cam_quat = mm.Quaternion.from_axis(m.sqrt(2), m.sqrt(m.sqrt(2)),  m.sqrt(m.sqrt(2)), -m.pi / 4.0)
        self.cam_pos = np.array([3.0, 3.0, 3.0])
        self.ratio = self.width() / self.height()
        self.fov_y = 1.10714872
        self.p_mat = mm.perspective_mat(z_near=0.1, z_far=1000.0,
                                        ratio=self.ratio,
                                        fov_y=self.fov_y)

        self.stored_mview = np.transpose(mm.quat_mat(self.cam_quat) * mm.translate_mat(*self.cam_pos))

        self.model_view_perspective_matrix = self.prog.uniforms['model_view_perspective_matrix']

        self.model_view_perspective_matrix.value = \
            tuple(((self.stored_mview) * np.transpose(self.p_mat)).flatten().tolist()[0])

        grid = []

        for i in range(65):
            grid.append([i - 32, -32.0, 0.0, i - 32, 32.0, 0.0])
            grid.append([-32.0, i - 32, 0.0, 32.0, i - 32, 0.0])

        grid = np.array(grid)

        self.vbo = self.ctx.buffer(grid.astype('f4').tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, ['vert'])

    @MyPyQtSlot("bool")
    def paintGL(self):
        self.ctx.viewport = (0,0, self.width(), self.height())
        self.ctx.clear(1.0, 1.0, 1.0)

        self.p_mat = mm.perspective_mat(z_near=0.1, z_far=1000.0,
                                        ratio=self.ratio,
                                        fov_y=self.fov_y)
        self.stored_mview = np.transpose(mm.translate_mat(*self.cam_pos)) * np.transpose(mm.quat_mat(self.cam_quat))
        self.model_view_perspective_matrix.value = \
            tuple(((self.stored_mview) * np.transpose(self.p_mat)).flatten().tolist()[0])

        self.vao.render(ModernGL.LINES)

