from PyQt5 import QtOpenGL, QtWidgets, QtCore
from PyQt5.QtGui import QCursor

import math as m
import minesim.matmult as mm
import numpy as np
import ModernGL

import os

import logging

import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
l = logging.getLogger('perspective_window')
l.setLevel(logging.DEBUG)

class PerspectiveWindow(QtOpenGL.QGLWidget):
    def __init__(self):
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(4, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        self.vao_instances = dict()
        super(PerspectiveWindow, self).__init__(fmt)

    def paintGL(self):
        self.ctx.viewport = (0, 0, self.width(), self.height())
        #self.ctx.wireframe = True
        self.ratio = self.width() / self.height()
        self.p_mat = mm.perspective_mat(z_near=0.1, z_far=1000.0,
                                        ratio=self.ratio,
                                        fov_y=self.fov_y)
        self.stored_mview = np.transpose(mm.translate_mat(*self.cam_pos))*np.transpose(mm.quat_mat(self.cam_quat))
        self.model_view_perspective_matrix.value = \
            tuple(((self.stored_mview)*np.transpose(self.p_mat)).flatten().tolist()[0])
        self.ctx.clear(0.9, 0.9, 0.9)
        for filename in self.vao_instances:
            self.vao_instances[filename].vao.render(mode=ModernGL.TRIANGLES,instances=self.vao_instances[filename].num_instances)
        self.ctx.finish()

    def initializeGL(self):
        self.ctx = ModernGL.create_context()

        self.ctx.enable(ModernGL.DEPTH_TEST) #ignore assimp or moderngl getting normals wrong

        script_dir = os.path.dirname(__file__)

        shader_file = open(script_dir + "/shaders/perspective_vertex.glsl")
        vertex_shader = shader_file.read()
        shader_file.close()

        shader_file = open(script_dir + "/shaders/perspective_fragment.glsl")
        fragment_shader = shader_file.read()
        shader_file.close()

        self.prog = self.ctx.program([
            self.ctx.vertex_shader(vertex_shader),
            self.ctx.fragment_shader(fragment_shader),
        ])

        self.cam_quat = mm.Quaternion.from_axis(1,0,0,m.pi/4.0)
        self.cam_pos = np.array([3.0,3.0,3.0])
        self.ratio = self.width() / self.height()
        self.fov_y = 1.10714872
        self.p_mat = mm.perspective_mat(z_near=0.1, z_far=1000.0,
                                        ratio=self.ratio,
                                        fov_y=self.fov_y)

        # keep multiplications on right since we're row major order
        # load with glLoadTransposeMatrix
        # scratch that. It's one matrix, just transpose it once (3 times) on the cpu.
        self.stored_mview = np.transpose(mm.quat_mat(self.cam_quat) * mm.translate_mat(*self.cam_pos))

        self.model_view_perspective_matrix = self.prog.uniforms['model_view_perspective_matrix']

        self.model_view_perspective_matrix.value = \
            tuple(((self.stored_mview) * np.transpose(self.p_mat)).flatten().tolist()[0])


        self.x_forms = bytearray()

        #self.ctx.buffer(self.x_forms).bind_to_storage_buffer(binding=2)
        self.no_xforms = True

        self.setMouseTracking(True)
        self.center_x = self.geometry().x() + self.width() / 2
        self.center_y = self.geometry().y() + self.height() / 2