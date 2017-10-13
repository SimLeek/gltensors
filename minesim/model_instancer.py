from minesim.perspective_window import PerspectiveWindow
from PIL import Image
from wavefront_reader import read_wavefront, read_objfile, read_mtlfile
import struct
import minesim.matmult as mm
import minesim.biome_generators as biogen
import numpy as np
import os

class Instancer(object):
    def __init__(self, vao, num_instances, transforms):
        self.transforms = transforms
        self.num_instances = num_instances
        self.vao = vao

class ModelInstancer(PerspectiveWindow):
    def __init__(self):
        '''self.meshes = []
        self.materials = []
        self.textures = []'''

        self.model_scenes= dict()
        self.instance_positions = dict()

        self.objs = dict()

        super(ModelInstancer, self).__init__()

    def add_instance(self, filename, transformation_matrix):
        pass

    def load_models(self, filename):
        obj = read_wavefront(filename)
        self.objs[filename] = obj

        gl_mesh = bytes()

        for mesh in obj.object_list:
            self.texture_image_file = mesh.material.map_Kd

            img = Image.open(os.path.join(os.path.dirname(filename), self.texture_image_file))
            texture = self.ctx.texture(img.size, 4, img.tobytes())
            texture.use()

            for f in mesh.faces:
                for v in range(len(f.vertices)):
                    gl_mesh += struct.pack('4f', *f.vertices[v], 1.0) # use 0.0 for skyboxes
                    gl_mesh += struct.pack('2f', *f.vertex_textures[v])

            vbo = self.ctx.buffer(gl_mesh)
            vao = self.ctx.simple_vertex_array(self.prog, vbo, ['vertex'])  # texture_coord
            trans_list = []
            plains = biogen.plains_gen(20, 20, 20, 10, 15, turbulence=0.01)
            for voxel in plains:
                trans_list.append(mm.translate_mat(*voxel, np.float32))

            vao_instancer = Instancer(vao, len(trans_list), trans_list)
            print("made")
            #todo: use compute shader to set matrices initially
            for x in range(len(trans_list)):
                self.x_forms.extend(struct.pack('16f', *((vao_instancer.transforms[x]).flatten().tolist()[0])))
                if x%200==0:
                    print(x)
            print("packed")

            if self.no_xforms==True:
                self.ctx.buffer(self.x_forms).bind_to_storage_buffer(binding=2)
                self.no_xforms =False
            print("bound")

            self.vao_instances[filename] = vao_instancer
