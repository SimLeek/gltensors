import unittest as ut
import minesim.perspective_window as persp

from PyQt5 import QtWidgets

class TestPerspectiveWindow(ut.TestCase):
    def testRuns(self):
        app = QtWidgets.QApplication([])

        win = persp.PerspectiveWindow()

        win.move(QtWidgets.QDesktopWidget().rect().center() - win.rect().center())
        win.show()
        app.exec_()