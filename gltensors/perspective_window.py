import moderngl
import numpy as np
import gltensors.matmult as mm
import math as m
"""
    Renders a blue triangle
"""
from PyQt5 import QtOpenGL, QtCore,QtWidgets
from functools import wraps
import moderngl
import os
import traceback
import types

from gltensors.glsl_window import *
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
    wireframe = False


    def __init__(self,
                 vertex_shader_file=GLSLWindow.shader_vertex_perspective,
                 fragment_shader_file=GLSLWindow.shader_fragment_textured,
                 **kw
                 ):
        super(PerspectiveWindow, self).__init__(vertex_shader_file = vertex_shader_file,
                                                fragment_shader_file = fragment_shader_file,
        )
        self.vao = None
        self.vbo = None

    @MyPyQtSlot("bool")
    def initializeGL(self,
            new_vertex_shader_file=None,
            new_fragment_shader_file=None,
            new_uniform_dict = None):
        super(PerspectiveWindow, self).initializeGL(
            new_vertex_shader_file=None,
            new_fragment_shader_file=None,
            new_uniform_dict = None)
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.cam_quat = mm.Quaternion.from_axis(m.sqrt(2), m.sqrt(m.sqrt(2)),  m.sqrt(m.sqrt(2)), -m.pi / 4.0)
        self.cam_pos = np.array([3.0, 3.0, 3.0])
        self.ratio = self.width() / self.height()
        self.fov_y = m.pi/3# todo: limit fov to w/in 1% of 90 deg, 180 deg at most
        self.p_mat = mm.perspective_mat(z_near=0.1, z_far=1000.0,
                                        ratio=self.ratio,
                                        fov_y=self.fov_y)

        self.stored_mview = np.transpose(mm.quat_mat(self.cam_quat) * mm.translate_mat(*self.cam_pos))

        self.model_view_perspective_matrix = self.prog['model_view_perspective_matrix']

        self.model_view_perspective_matrix.value = \
            tuple(((self.stored_mview) * np.transpose(self.p_mat)).flatten().tolist())

        self.vbo = self.ctx.buffer(self.vbo_data)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, *self.vao_input_list)

    def setVBO(self, data):
        self.vbo_data = data

    def setVAO(self, input_list=('vert',)):
        self.vao_input_list = input_list

    @MyPyQtSlot("bool")
    def paintGL(self):
        self.ctx.viewport = (0,0, self.width(), self.height())
        self.ctx.clear(1.0, 1.0, 1.0)


        self.p_mat = mm.perspective_mat(z_near=0.1, z_far=1000.0,
                                        ratio=self.ratio,
                                        fov_y=self.fov_y)
        self.stored_mview = np.matmul(np.transpose(mm.translate_mat(*self.cam_pos)), np.transpose(mm.quat_mat(self.cam_quat)))
        self.model_view_perspective_matrix.value = \
            tuple((np.matmul(self.stored_mview, np.transpose(self.p_mat))).flatten(order='C'))

        if self.wireframe:
            self.vao.render(moderngl.LINES)
        else:
            self.vao.render(moderngl.TRIANGLES)


