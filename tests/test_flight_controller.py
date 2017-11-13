import unittest as ut
from PyQt5 import QtWidgets
import minesim.flight_controller as flyer
from .data.perspectiveTesting import setupForTesting
import os

class TestPerspectiveWindow(ut.TestCase):
    def testRuns(self):
        app = QtWidgets.QApplication([])
        window = flyer.FlightController()
        window.wireframe = True
        setupForTesting(window)
        window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
        window.show()

        app.exec_()