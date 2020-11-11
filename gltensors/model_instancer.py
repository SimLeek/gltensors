from gltensors.flight_controller import FlightController, VrController
from gltensors.glsl_window import MyPyQtSlot
from PIL import Image
import struct
import gltensors.matmult as mm
import gltensors.biome_generators as biogen
import numpy as np
import os
from gltensors import model_loader
import gltensors.GLSLComputer as glcpu

model_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'blocks'
shader_dir = os.sep.join([os.path.dirname(os.path.realpath(__file__)), '..', 'gltensors', 'shaders'])

class ModelViewer(FlightController):
    def __init__(self, fragment_shader_file=FlightController.shader_fragment_textured,
                 vertex_shader_file=FlightController.shader_vertex_perspective_vr,
                 *args, **kw):
        # todo: vertex barrel distort won't work on textures.
        #  For full barrel, project onto its own texture and distort that.

        self.model_scenes = dict()
        self.instance_positions = dict()

        self.objs = dict()
        super(ModelViewer, self).__init__(fragment_shader_file=fragment_shader_file,
                                          vertex_shader_file=vertex_shader_file,
                                          uniform_dict={'BarrelPower': .8}, *args, **kw)

    def set_pose(self, pose):
        self.cam_pos = pose[:3]
        self.cam_quat.x, self.cam_quat.y, self.cam_quat.z, self.cam_quat.w = pose[3:]

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

        if len(positions)>1:
            shader_file = open(
                os.path.abspath(os.sep.join([shader_dir, 'mesh_pack_shader.glsl'])))
            mesh_pack_shader = shader_file.read()
            shader_file.close()
            mesh_packer = glcpu.GLSLComputer(
                mesh_pack_shader,
                num_faces=obj0['num_faces']
            )
            buff_v = mesh_packer.ctx.buffer(data=obj0['v'].astype(dtype=np.float32).tobytes())
            buff_v.bind_to_storage_buffer(0)

            buff_t = mesh_packer.ctx.buffer(data=obj0['vt'].astype(dtype=np.float32).tobytes())
            buff_t.bind_to_storage_buffer(1)

            buff_p = mesh_packer.ctx.buffer(data=positions.astype(dtype=np.float32).tobytes())
            buff_p.bind_to_storage_buffer(2)

            buff_c = mesh_packer.ctx.buffer(data=np.ones(len(positions)*4).astype(dtype=np.float32).tobytes())
            buff_c.bind_to_storage_buffer(3)

            buff_o = mesh_packer.ctx.buffer(data=np.zeros((10*len(obj0['v'][0])*obj0['num_faces']*len(positions))).astype(dtype=np.float32).tobytes())
            buff_o.bind_to_storage_buffer(4)

            mesh_packer.cpu.run(len(positions), obj0['num_faces'])
            mesh_packer.ctx.finish()

            self.gl_mesh = np.frombuffer(buff_o.read(), dtype=np.float32).tobytes('A')

            buff_v.release()
            buff_t.release()
            buff_p.release()
            buff_c.release()
            buff_o.release()
            mesh_packer.ctx.release()
        else:
            for p in positions:
                for f in range(obj0['num_faces']):
                    verts = np.copy(obj0['v'][f])
                    verts += (np.transpose(p) * 2)
                    texs = obj0['vt'][f]
                    self.gl_mesh += struct.pack('4f', *verts, 1.0)  # use 0.0 for skyboxes
                    self.gl_mesh += struct.pack('2f', *texs)
                    self.gl_mesh += struct.pack('4f', 1.0, 1.0, 1.0, 1.0)

    def setup_gl_objects(self):
        self.setVBO(self.gl_mesh)
        self.setVAO(('vert', 'texture_coord', 'rgba_multiplier'))

    @MyPyQtSlot("bool")
    def initializeGL(self, *args, **kw):
        self.setup_gl_objects()
        super(ModelViewer, self).initializeGL(self, new_uniform_dict=self.uniform_dict, *args, **kw)

        texture = self.ctx.texture(self.img.size, 4, self.img.tobytes())
        texture.use()  # todo: instead, append this to the list of textures
