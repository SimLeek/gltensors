import unittest as ut
import minesim.perspective_window as persp

from PyQt5 import QtWidgets
from minesim.glsl_window import MyPyQtSlot

from minesim.matmult import id_mat
import struct

import numpy as np
class TestPerspectiveWindow(ut.TestCase):
    def testRuns(self):
        app = QtWidgets.QApplication([])

        win = persp.PerspectiveWindow()

        win.move(QtWidgets.QDesktopWidget().rect().center() - win.rect().center())
        win.show()
        app.exec_()

    def testGrid(self):
        app = QtWidgets.QApplication([])

        class GridWindow(persp.PerspectiveWindow):
            @MyPyQtSlot("bool")
            def initializeGL(self,
                             new_vertex_shader_file=None,
                             new_fragment_shader_file=None,
                             new_uniform_dict=None):
                super(GridWindow, self).initializeGL()
                self.grid = []

                for i in range(65):
                    self.grid.append([i - 32, -32.0, 5.0, 1.0,0.0,0.0, i - 32, 32.0, 5.0, 1.0,0.0,0.0])
                    self.grid.append([-32.0, i - 32, 5.0, 1.0,0.0,0.0, 32.0, i - 32, 5.0, 1.0,0.0,0.0])

                self.grid = np.array(self.grid)

                self.vbo = self.ctx.buffer(self.grid.astype('f4').tobytes())

                class vao_instance:
                    def __init__(self):
                        self.vao = win.ctx.simple_vertex_array(win.prog, win.vbo, ['vertex'])
                        self.num_instances = 1
                        self.num_vertices = 65 * 4

                self.ctx.wireframe = True
                self.x_forms.extend(struct.pack('16f', *((id_mat()).flatten().tolist()[0])))
                self.ctx.buffer(self.x_forms).bind_to_storage_buffer(binding=2)


                win.vao_instances[1] = vao_instance()

        win = GridWindow()

        win.move(QtWidgets.QDesktopWidget().rect().center() - win.rect().center())
        win.show()
        app.exec_()
