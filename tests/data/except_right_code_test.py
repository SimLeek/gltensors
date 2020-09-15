import gltensors.glsl_window as glwin
import os
from PyQt5 import QtWidgets

app = QtWidgets.QApplication([])
window = glwin.GLSLWindow(os.sep.join(['data', 'empfty.glsl']),os.sep.join(['data', 'empty.glsl']),{})
window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
window.show()
window.destroy()
#app.exec_()