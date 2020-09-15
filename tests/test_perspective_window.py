import unittest as ut
from PyQt5 import QtWidgets
import gltensors.perspective_window as persp
from .data.perspectiveTesting import setupForTesting

class TestPerspectiveWindow(ut.TestCase):
    def testRuns(self):
        app = QtWidgets.QApplication([])

        win = persp.PerspectiveWindow(vertex_shader_file=persp.GLSLWindow.shader_vertex_perspective,
                 fragment_shader_file=persp.GLSLWindow.shader_fragment_black_and_white)
        win.wireframe = True
        setupForTesting(win)

        win.move(QtWidgets.QDesktopWidget().rect().center() - win.rect().center())
        win.show()
        app.exec_()