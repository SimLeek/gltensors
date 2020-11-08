import gltensors.glsl_window as glwin
from PyQt5 import QtCore, QtOpenGL

class UpdatingWindow(glwin.GLSLWindow):
    def __init__(self, refresh_rate_ms = int(1000 / 60), **kw):
        self.restraining_mouse = True
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_event)
        self.update_timer.start(refresh_rate_ms)

        self.updaters = []

        super(UpdatingWindow, self).__init__(**kw)

    def register_updaters(self, command):
        self.updaters.append(command)

    def update_event(self):
        for u in self.updaters:
            u()
        self.repaint()
        #self.updateGL()