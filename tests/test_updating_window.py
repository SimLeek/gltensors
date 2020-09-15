import unittest as ut
from PyQt5 import QtWidgets
import gltensors.updating_window as upw
from .data.perspectiveTesting import setupForTesting

class TestPerspectiveWindow(ut.TestCase):
    def testRuns(self):
        app = QtWidgets.QApplication([])

        win = upw.UpdatingWindow()
        win.register_updaters(lambda: print("Test!"))

        win.move(QtWidgets.QDesktopWidget().rect().center() - win.rect().center())
        win.show()
        app.exec_()