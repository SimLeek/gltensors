from gltensors.flight_controller import FlightController
from gltensors.glsl_window import MyPyQtSlot
from PIL import Image
import struct
import gltensors.matmult as mm
import gltensors.biome_generators as biogen
import numpy as np
import os
from gltensors import model_loader

model_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'blocks'


class ModelViewer(FlightController):
    def __init__(self, fragment_shader_file=FlightController.shader_fragment_textured,
                 *args, **kw):
        '''self.meshes = []
        self.materials = []
        self.textures = []'''

        self.model_scenes = dict()
        self.instance_positions = dict()

        self.objs = dict()

        super(ModelViewer, self).__init__(fragment_shader_file=fragment_shader_file, *args, **kw)

    def add_instance(self, filename, transformation_matrix):
        pass

    def load_model_file_into_cache(self, filename):
        obj = model_loader.read_wavefront(filename)
        self.objs[filename] = obj

        self.gl_mesh = bytes()

        obj0 = next(iter(obj.values()))

        self.texture_image_file = obj0['material']['map_Kd']
        self.img = Image.open(os.path.join(os.path.dirname(filename), self.texture_image_file))

        for f in range(obj0['num_faces']):
            verts = obj0['v'][f]
            texs = obj0['vt'][f]
            self.gl_mesh += struct.pack('4f', *verts, 1.0)  # use 0.0 for skyboxes
            self.gl_mesh += struct.pack('2f', *texs)
            self.gl_mesh += struct.pack('4f', 0.8, 0.8, 0.2, 1.0)

    def load_model_file_into_positions(self, filename, positions):
        obj = model_loader.read_wavefront(filename)
        self.objs[filename] = obj

        self.gl_mesh = bytearray()

        obj0 = next(iter(obj.values()))

        self.texture_image_file = obj0['material']['map_Kd']
        self.img = Image.open(os.path.join(os.path.dirname(filename), self.texture_image_file))

        i=0
        i_max = len(positions)
        j=0
        j_sqrt = np.sqrt(i_max)
        for p in positions:  # todo: SPEED ISSUE! use a glsl cpu to get this quickly
            col = i/i_max
            col2 = j/j_sqrt
            for f in range(obj0['num_faces']):
                verts = np.copy(obj0['v'][f])
                verts += (np.transpose(p)*2)
                texs = obj0['vt'][f]
                self.gl_mesh += struct.pack('4f', *verts, 1.0)  # use 0.0 for skyboxes
                self.gl_mesh += struct.pack('2f', *texs)
                self.gl_mesh += struct.pack('4f', col2,col,col,1.0)
            i+=1
            j+=1
            if j>j_sqrt:
                j=0


    def setup_gl_objects(self):
        self.setVBO(self.gl_mesh)
        self.setVAO(('vert', 'texture_coord', 'rgba_multiplier'))

    @MyPyQtSlot("bool")
    def initializeGL(self, *args, **kw):
        self.setup_gl_objects()
        super(ModelViewer, self).initializeGL(self, *args, **kw)

        texture = self.ctx.texture(self.img.size, 4, self.img.tobytes())
        texture.use()  # todo: instead, append this to the list of textures
