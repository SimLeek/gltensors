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

                grid = []

                for i in range(65):
                    grid.append([i - 32, -32.0, 0.0, i - 32, 32.0, 0.0])
                    grid.append([-32.0, i - 32, 0.0, 32.0, i - 32, 0.0])

                grid = np.array(grid)

                self.grid = np.array(grid)

                self.vbo = self.ctx.buffer(grid.astype('f4').tobytes())

                self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, ['vert'])



        win = GridWindow()

        win.move(QtWidgets.QDesktopWidget().rect().center() - win.rect().center())
        win.show()
        app.exec_()
