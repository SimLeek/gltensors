import unittest as ut
import minesim.glsl_window as glwin
from sys import platform
from PyQt5 import QtWidgets
import os

app = QtWidgets.QApplication([])

class TestGLSLWin(ut.TestCase):
    def testOpens(self):
        window = glwin.GLSLWindow(os.sep.join(['data', 'empty.glsl']),os.sep.join(['data', 'empty.glsl']),{})
        window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
        window.show()
        window.destroy()

    def testFailsRight(self):
        import subprocess
        result = ""
        if platform == "linux" or platform == "linux2":
            result = subprocess.check_output(
                [
                    'python3',
                    os.sep.join(['data', 'except_right_code_test.py'])
                ],
                stderr=subprocess.STDOUT
            )
        elif platform == "win32" or platform ==  "cygwin":
            result = subprocess.check_output(
                [
                    'py -3',
                    os.sep.join(['data', 'except_right_code_test.py'])
                ],
                stderr=subprocess.STDOUT
            )
        self.assertIn(b"FileNotFoundError", result)



