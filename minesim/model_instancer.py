from minesim.flight_controller import FlightController
from minesim.glsl_window import MyPyQtSlot
from PIL import Image
from wavefront_reader import read_wavefront, read_objfile, read_mtlfile
import struct
import minesim.matmult as mm
import minesim.biome_generators as biogen
import numpy as np
import os

class ModelViewer(FlightController):
    def __init__(self, fragment_shader_file=FlightController.shader_fragment_textured,
                 *args, **kw):
        '''self.meshes = []
        self.materials = []
        self.textures = []'''

        self.model_scenes= dict()
        self.instance_positions = dict()

        self.objs = dict()

        super(ModelViewer, self).__init__(fragment_shader_file=fragment_shader_file ,*args, **kw)

    def add_instance(self, filename, transformation_matrix):
        pass

    def load_model_file_into_cache(self, filename):
        obj = read_wavefront(filename)
        self.objs[filename] = obj

        self.gl_mesh = bytes()

        for mesh in obj.object_list:
            self.texture_image_file = mesh.material.map_Kd
            self.img = Image.open(os.path.join(os.path.dirname(filename), self.texture_image_file))

            for f in mesh.faces:
                for v in range(len(f.vertices)): #todo: add functions for modifying these verts
                    self.gl_mesh += struct.pack('4f', *f.vertices[v], 1.0) # use 0.0 for skyboxes
                    self.gl_mesh += struct.pack('2f', *f.vertex_textures[v])

    def load_model_file_into_positions(self, filename, positions):
        obj = read_wavefront(filename)
        self.objs[filename] = obj

        self.gl_mesh = bytearray()

        for mesh in obj.object_list:
            self.texture_image_file = mesh.material.map_Kd
            self.img = Image.open(os.path.join(os.path.dirname(filename), self.texture_image_file))

            for p in positions:  # todo: SPEED ISSUE! use a glsl cpu to get this quickly
                for f in mesh.faces:
                    for v in range(len(f.vertices)):  # todo: add functions for modifying these verts
                        self.gl_mesh.extend(struct.pack('4f',
                                                    p[0]*2 + f.vertices[v][0],
                                                    p[1]*2 + f.vertices[v][1],
                                                    p[2]*2 + f.vertices[v][2],
                                                    1.0))  # use 0.0 for skyboxes
                        self.gl_mesh.extend(struct.pack('2f', *f.vertex_textures[v]))

    def setup_gl_objects(self):
        self.setVBO(self.gl_mesh)
        self.setVAO(('vert', 'texture_coord'))

    @MyPyQtSlot("bool")
    def initializeGL(self, *args, **kw):
        self.setup_gl_objects()
        super(ModelViewer, self).initializeGL(self, *args, **kw)

        texture = self.ctx.texture(self.img.size, 4, self.img.tobytes())
        texture.use()  # todo: instead, append this to the list of textures



if __name__ == '__main__':
    from PyQt5 import QtWidgets
    import os
    app = QtWidgets.QApplication([])
    window = ModelViewer()
    #window.load_model_file_into_cache(os.path.dirname(os.path.realpath(__file__))\
    #                           + os.sep + 'blocks' + os.sep + 'cube.obj')

    plains = biogen.plains_gen(500, 500, 100, 30, 50, turbulence=0.01).astype(np.bool_)
    min_h = 0
    max_h = 35
    h = max_h - min_h
    dissipation = 0.05
    # us, but not them boolean operators to remove boolean arrays from other boolean arrays
    # if I run into long strings of operators like these, consider moving back to glsl.
    cave_caves = biogen.cloud_layer_gen(500, 500, h, 0.02, 0.0, 0) & ~biogen.cloud_layer_gen(500, 500, h, 0.1, 0.0, 0)
    cave_caves = biogen.cloud_layer_gen(500, 500, h, 0.005, 0.0, dissipation) & ~cave_caves
    plains[0:500, 0:500, min_h:max_h] = plains[0:500, 0:500, min_h:max_h] & ~cave_caves
    visible_plains = biogen.restrict_visible(plains, plains, show_bounds=True)
    visible_locations = biogen.get_locations(visible_plains)



    window.load_model_file_into_positions(os.path.dirname(os.path.realpath(__file__))\
                               + os.sep + 'blocks' + os.sep + 'cube.obj',
                                          visible_locations)

    window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
    window.show()

    script_dir = os.path.dirname(__file__)

    app.exec_()