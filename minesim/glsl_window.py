from PyQt5 import QtOpenGL, QtCore
from functools import wraps
import ModernGL
import os
import traceback
import types
import minesim.matmult as mm

if False:
    import numpy as np
    from typing import Dict, Any

#https://stackoverflow.com/a/19015654/782170
def MyPyQtSlot(*args):
    if len(args) == 0 or isinstance(args[0], types.FunctionType):
        args = []
    @QtCore.pyqtSlot(*args)
    def slotdecorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args)
            except:
                print("Uncaught Exception in slot[{}].".format(func.__name__))
                traceback.print_exc()
        return wrapper

    return slotdecorator

class GLSLWindow(QtOpenGL.QGLWidget):
    shader_fragment_black_and_white = os.path.dirname(os.path.realpath(__file__))\
                                      + os.sep + 'shaders' + os.sep + 'black_and_white_fragment.glsl'
    shader_fragment_textured = os.path.dirname(os.path.realpath(__file__))\
                               + os.sep + 'shaders' + os.sep + 'texture_fragment.glsl'

    shader_vertex_perspective = os.path.dirname(os.path.realpath(__file__))\
                               + os.sep + 'shaders' + os.sep + 'perspective_vertex.glsl'


    fmt = QtOpenGL.QGLFormat()
    fmt.setVersion(4,3)
    fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
    fmt.setSampleBuffers(True)

    def __init__(self,
                 vertex_shader_file=None,
                 fragment_shader_file=None,
                 uniform_dict=None  # type: Dict[str, Any]
                 ):
        super(GLSLWindow, self).__init__(self.fmt)

        self.ctx = None  # type: ModernGL.Context

        self.script_dir = os.path.dirname(__file__)

        if vertex_shader_file is not None:
            self.vertex_shader = os.path.realpath(vertex_shader_file)
        else:
            self.vertex_shader = None
        if fragment_shader_file is not None:
            self.fragment_shader = os.path.realpath(fragment_shader_file)
        else:
            self.fragment_shader = None



        self.uniform_dict = uniform_dict

    def read_shader(self, shader_filename):
        shader_file = open(shader_filename)
        shader_text = shader_file.read()
        shader_file.close()
        return shader_text

    @MyPyQtSlot("bool")
    def paintGL(self):
        self.ctx.viewport = (0, 0, self.width(), self.height())
        self.ratio = self.width()*1.0 / self.height()

    @MyPyQtSlot("bool")
    def initializeGL(self,
                     new_vertex_shader_file=None,
                     new_fragment_shader_file=None,
                     new_uniform_dict = None):
        self.ctx = ModernGL.create_context()

        if new_fragment_shader_file:
            self.fragment_shader = new_fragment_shader_file
        if new_vertex_shader_file:
            self.vertex_shader = new_vertex_shader_file
        if self.vertex_shader is not None:
            vertex_shader = self.read_shader(self.vertex_shader)
        if self.fragment_shader is not None:
            fragment_shader = self.read_shader(self.fragment_shader)

        if self.vertex_shader is not None and self.fragment_shader is not None:
            self.prog = self.ctx.program([
                self.ctx.vertex_shader(vertex_shader),
                self.ctx.fragment_shader(fragment_shader)
            ])

            if self.uniform_dict is not None:
                for name, value in self.uniform_dict.items():
                    self.prog.uniforms[name].value = value
