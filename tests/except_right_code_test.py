import minesim.glsl_window as glwin
from PyQt5 import QtWidgets

app = QtWidgets.QApplication([])
window = glwin.GLSLWindow("..\\tests\\empfty.glsl","..\\tefsts\\empty.glsl",{})
window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
window.show()
window.destroy()
#app.exec_()