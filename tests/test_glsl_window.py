import unittest as ut
import minesim.glsl_window as glwin
from PyQt5 import QtWidgets

app = QtWidgets.QApplication([])

class TestGLSLWin(ut.TestCase):
    def testOpens(self):
        window = glwin.GLSLWindow("..\\tests\\empty.glsl","..\\tests\\empty.glsl",{})
        window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
        window.show()
        window.destroy()

    def testFailsRight(self):
        import subprocess
        # todo: get test working in linux
        result = subprocess.check_output('py -3 except_right_code_test.py', shell=True)
        self.assertIn(b"initializeGL", result)



