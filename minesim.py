import math as m
import struct
from enum import Enum

import ModernGL
import numpy as np
from PIL import Image
from PyQt5 import QtOpenGL, QtWidgets, QtCore
from PyQt5.QtGui import QCursor

import matmult as mm

global additional_dirs
additional_dirs = []

import os
if os.name=='nt': # really now, assimp...
    additional_dirs.append("C:\Program Files\Assimp\bin\x86")

import pyassimp as pya

class FlightControls(Enum):
    forward = 1
    back = 2
    left = 3
    right = 4
    roll_cw = 5
    roll_ccw = 6
    up = 7
    down = 8

class Instancer(object):
    def __init__(self, vao, num_instances, transforms):
        self.transforms = transforms
        self.num_instances = num_instances
        self.vao = vao

class PerspectiveWindow(QtOpenGL.QGLWidget):
    def __init__(self):
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        self.vao_instances = dict()
        super(PerspectiveWindow, self).__init__(fmt)

    def paintGL(self):
        self.ctx.viewport = (0, 0, self.width(), self.height())
        self.ratio = self.width() / self.height()
        self.p_mat = mm.perspective_mat(z_near=0.1, z_far=1000.0,
                                        ratio=self.ratio,
                                        fov_y=self.fov_y)
        self.stored_mview = np.transpose(mm.translate_mat(*self.cam_pos))*np.transpose(mm.quat_mat(self.cam_quat))
        self.model_view_matrix.value = tuple(self.stored_mview.flatten().tolist()[0])
        self.model_view_perspective_matrix.value = \
            tuple(((self.stored_mview)*np.transpose(self.p_mat)).flatten().tolist()[0])
        self.ctx.clear(0.9, 0.9, 0.9)
        # self.vao.render(ModernGL.LINES, 65 * 4)
        for filename in self.vao_instances:
            self.vao_instances[filename].vao.render(mode=ModernGL.TRIANGLES,instances=self.vao_instances[filename].num_instances)
        self.ctx.finish()

    def initializeGL(self):
        self.ctx = ModernGL.create_context()
        self.ctx.enable(ModernGL.DEPTH_TEST) #ignore assimp or moderngl getting normals wrong

        self.prog = self.ctx.program([
            self.ctx.vertex_shader('''
    #version 430 //because SSBOs :D

    #extension GL_ARB_shader_storage_buffer_object : require

    in vec4 vertex;
    in vec2 texture_coord;
    //in vec2 tex_coord;

    out vec2 v_tex_coord;
    uniform mat4 model_view_matrix;
    uniform mat4 model_view_perspective_matrix;

    //in normal;
    //out v_normal;
    //out v

    layout (std430, binding = 2) buffer shader_data
    {
        mat4 instance_transform_matrix[];
    };

    void main() {
        mat4 transform = instance_transform_matrix[gl_InstanceID];
        mat4 unused_mat = model_view_matrix;
        gl_Position = model_view_perspective_matrix * (vertex * transform);
        //v =  (model_view_matrix * (vertex * transform)).xyz; // Convert the vertex in the View space with the instanciation matrix (transform)
        //vec3 instanciednormal = (vec4(p3d_Normal,0.0) * transform).xyz;
        //mynormal = normalize(gl_NormalMatrix * instanciednormal);
        v_tex_coord = texture_coord;
    }
'''),
            self.ctx.fragment_shader('''
    #version 330

    uniform sampler2D texture_1;

    in vec2 v_tex_coord;

    out vec4 color;

    void main() {
        //color = vec4(.1,.1,.1,1.0);
        color = vec4(texture(texture_1, v_tex_coord).rgb, 1.0);
    }
'''),
        ])

        self.cam_quat = mm.Quaternion.from_axis(1,0,0,m.pi/4.0)
        self.cam_pos = np.array([3.0,3.0,3.0])
        self.ratio = self.width() / self.height()
        self.fov_y = 1.10714872
        self.p_mat = mm.perspective_mat(z_near=0.1, z_far=1000.0,
                                        ratio=self.ratio,
                                        fov_y=self.fov_y)

        # keep multiplications on right since we're row major order
        # load with glLoadTransposeMatrix
        # scratch that. It's one matrix, just transpose it once (3 times) on the cpu.
        self.model_view_matrix = self.prog.uniforms['model_view_matrix']
        # +.value -v
        self.stored_mview = np.transpose(mm.quat_mat(self.cam_quat) * mm.translate_mat(*self.cam_pos))
        self.model_view_matrix.value = tuple(self.stored_mview.flatten().tolist()[0])

        self.model_view_perspective_matrix = self.prog.uniforms['model_view_perspective_matrix']
        self.model_view_perspective_matrix.value = \
            tuple(((self.stored_mview) * np.transpose(self.p_mat)).flatten().tolist()[0])


        self.x_forms = bytearray()

        '''for i in range(20):
            x_forms += struct.pack('16f', *((mm.scale_rot_trans_mat(1.0+.1*i, 1.0+.1*i,1.0+.1*i,
                                                                 0,0,1*i,
                                                                 1,0,0,
                                                                 0, dtype = np.float32)).flatten().tolist()[0]))
'''
        '''for i in range(0, 65):
            grid += struct.pack('8f', i - 32, -32.0, 0.0, 1.0, i - 32, 32.0, 0.0, 1.0)
            grid += struct.pack('8f', -32.0, i - 32, 0.0, 1.0, 32.0, i - 32, 0.0, 1.0)'''

        '''grid = bytes()
        sx = 8
        sy = 8
        for i in range(int(-sx/2),int(sx/2)):
            for j in range(int(-sy/2), int(sy/2)):
                # t1
                grid += struct.pack('4f', i - 1, j-1.0, 0.0, 1.0)
                grid += struct.pack('2f', i - 1, j-1.0)
                grid += struct.pack('4f',i-1, j, 0.0, 1.0)
                grid += struct.pack('2f', i-1, j)
                grid += struct.pack('4f', i, j, 0.0, 1.0)
                grid += struct.pack('2f', i, j)
                # t2
                grid += struct.pack('4f', i, j, 0.0, 1.0)
                grid += struct.pack('2f', i, j)
                grid += struct.pack('4f', i, j-1, 0.0, 1.0)
                grid += struct.pack('2f', i, j-1)
                grid += struct.pack('4f', i - 1, j - 1.0, 0.0, 1.0)
                grid += struct.pack('2f', i - 1, j - 1.0)

        self.vbo = self.ctx.buffer(grid)
        self.vao = self.ctx.simple_vertex_array(prog, self.vbo, ['vertex', 'texture_coord']) # tex_coord'''

        #self.ctx.buffer(self.x_forms).bind_to_storage_buffer(binding=2)
        self.no_xforms = True

        self.setMouseTracking(True)
        self.center_x = self.geometry().x() + self.width() / 2
        self.center_y = self.geometry().y() + self.height() / 2


from MineSim import biome_generators


class ModelInstancer(PerspectiveWindow):
    def __init__(self):
        '''self.meshes = []
        self.materials = []
        self.textures = []'''

        self.model_scenes= dict()
        self.instance_positions = dict()

        super(ModelInstancer, self).__init__()



    def __del__(self): # in case of cyclic references, use weakref
        for filename in self.model_scenes:
            self.unload_models(filename)

    def unload_models(self, filename):
        if filename in self.model_scenes:
            try:
                pya.release(self.model_scenes[filename])
            except ImportError:
                pass # python is shutting down
        else:
            raise RuntimeWarning(str(filename)+" is not in the model set")

    def add_instance(self, filename, transformation_matrix):
        pass

    def load_models(self, filename):
        scene = pya.load(filename)
        self.model_scenes[filename] = scene

        gl_mesh = bytes()

        for mesh in scene.meshes:
            props_dict = dict()
            for key in dict.keys(mesh.material.properties):
                props_dict[key[0]] = key
                #print(key, mesh.material.properties[props_dict[key[0]]])
            self.tex_file = mesh.material.properties[props_dict['file']]

            img = Image.open(self.tex_file)
            texture = self.ctx.texture(img.size, 4, img.tobytes())
            texture.use()

            '''for v in range(len(mesh.vertices)//3):
                mesh.vertices[v * 3], mesh.vertices[v * 3 + 2] = copy.copy(mesh.vertices[v * 3+2]),\
                                                                 copy.copy(mesh.vertices[v * 3 ])'''

            # print(mesh.vertices)

            for v in range(len(mesh.vertices)):
                gl_mesh += struct.pack('4f', *mesh.vertices[v],1.0) # use 0.0 for skyboxes
                gl_mesh += struct.pack('2f', mesh.texturecoords[0][v][0], mesh.texturecoords[0][v][1])

            vbo = self.ctx.buffer(gl_mesh)
            vao = self.ctx.simple_vertex_array(self.prog, vbo, ['vertex', 'texture_coord'])  # tex_coord
            trans_list = []
            for x in range(200): # 1 decikilometer ftw
                for y in range(200):
                    trans_list.append(mm.translate_mat(*biome_generators.plains_top_inst_gen(x * 2, y * 2), np.float32))
                if x%200==0:
                    print(x*200)
            vao_instancer = Instancer(vao, 40000, trans_list)
            print("made")
            #todo: use compute shader to set matrices initially
            for x in range(40000):
                self.x_forms.extend(struct.pack('16f', *((vao_instancer.transforms[x]).flatten().tolist()[0])))
                if x%200==0:
                    print(x)
            print("packed")

            if self.no_xforms==True:
                self.ctx.buffer(self.x_forms).bind_to_storage_buffer(binding=2)
                self.no_xforms =False
            print("bound")

            self.vao_instances[filename] = vao_instancer
        '''for material in scene.materials:
            self.materials.append(material)
        for texture in scene.textures:
            self.textures.append(texture)'''

class UpdatingWindow(ModelInstancer):
    def __init__(self):
        self.restraining_mouse = True
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_event)
        self.update_timer.start(int(1000 / 60))  # 60 fps max

        self.updaters = []

        super(UpdatingWindow, self).__init__()

    def register_updaters(self, command):
        self.updaters.append(command)

    def update_event(self):
        for u in self.updaters:
            u()
        self.repaint()

class FlightController(UpdatingWindow):
    def __init__(self, flight_keys = None, flight_speed = 1, *args, **kw):
        self.flight_keys = flight_keys
        if self.flight_keys == None:
            self.flight_keys = dict()
            self.flight_keys[QtCore.Qt.Key_W] = FlightControls.forward
            self.flight_keys[QtCore.Qt.Key_S] = FlightControls.back
            self.flight_keys[QtCore.Qt.Key_A] = FlightControls.left
            self.flight_keys[QtCore.Qt.Key_D] = FlightControls.right
        self.active_controls = set()

        self.flight_speed = flight_speed

        super(FlightController, self).__init__()

        self.register_updaters(self.flight_update)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.restraining_mouse = not self.restraining_mouse
        self.flight_keypress(event)

    def keyReleaseEvent(self, event):
        pass
        self.flight_keyrelease(event)

    def flight_keypress(self, event):
        if event.key() == QtCore.Qt.Key_W:
            self.active_controls.add(FlightControls.forward)
        if event.key() == QtCore.Qt.Key_S:
            self.active_controls.add(FlightControls.back)
        if event.key() == QtCore.Qt.Key_A:
            self.active_controls.add(FlightControls.left)
        if event.key() == QtCore.Qt.Key_D:
            self.active_controls.add(FlightControls.right)
        if event.key() == QtCore.Qt.Key_Q:
            self.active_controls.add(FlightControls.roll_ccw)
        if event.key() == QtCore.Qt.Key_E:
            self.active_controls.add(FlightControls.roll_cw)
        if event.key() == QtCore.Qt.Key_Space:
            self.active_controls.add(FlightControls.up)
        if event.key() == QtCore.Qt.Key_Shift:
            self.active_controls.add(FlightControls.down)

    def flight_keyrelease(self, event):
        if event.key() == QtCore.Qt.Key_W:
            self.active_controls.remove(FlightControls.forward)
        if event.key() == QtCore.Qt.Key_S:
            self.active_controls.remove(FlightControls.back)
        if event.key() == QtCore.Qt.Key_A:
            self.active_controls.remove(FlightControls.left)
        if event.key() == QtCore.Qt.Key_D:
            self.active_controls.remove(FlightControls.right)
        if event.key() == QtCore.Qt.Key_Q:
            self.active_controls.remove(FlightControls.roll_ccw)
        if event.key() == QtCore.Qt.Key_E:
            self.active_controls.remove(FlightControls.roll_cw)
        if event.key() == QtCore.Qt.Key_Space:
            self.active_controls.remove(FlightControls.up)
        if event.key() == QtCore.Qt.Key_Shift:
            self.active_controls.remove(FlightControls.down)

    def flight_update(self):
        if FlightControls.forward in self.active_controls:
            look = self.cam_quat.apply(*[0, 0, 1])
            self.cam_pos+=look

        if FlightControls.back in self.active_controls:
            back = self.cam_quat.apply(*[0, 0, -1])
            self.cam_pos += back

        if FlightControls.left in self.active_controls:
            left = self.cam_quat.apply(*[-1, 0, 0])
            self.cam_pos += left

        if FlightControls.right in self.active_controls:
            right = self.cam_quat.apply(*[1, 0, 0])
            self.cam_pos += right

        if FlightControls.roll_cw in self.active_controls:
            look = self.cam_quat.apply(*[0, 0, 1])

            self.cam_quat = self.cam_quat * mm.Quaternion.from_axis(*look, .05)
            self.cam_quat.normalize()

        if FlightControls.roll_ccw in self.active_controls:
            look = self.cam_quat.apply(*[0, 0, 1])
            self.cam_quat = self.cam_quat * mm.Quaternion.from_axis(*look, -.05)
            self.cam_quat.normalize()

        if FlightControls.up in self.active_controls:
            up = self.cam_quat.apply(*[0, 1, 0])
            self.cam_pos += up

        if FlightControls.down in self.active_controls:
            down = self.cam_quat.apply(*[0, -1, 0])
            self.cam_pos += down



    def mouseMoveEvent(self, event):
        if self.restraining_mouse:
            # update global center in case window moved
            # int casting protects from stray .5 from odd screen sizes
            self.center_x = self.geometry().x() + int(self.width()/2)
            self.center_y = self.geometry().y() + int(self.height()/2)

            cursor_pos = event.globalPos()

            if self.center_x == cursor_pos.x() and self.center_y ==cursor_pos.y():
                return # cursor was re-centered.
            else:

                # get & normalize mouse movement
                move = [int(cursor_pos.x()-self.center_x), int(cursor_pos.y()-self.center_y)]

                # exponentiate for both precise and fast control
                '''exponent = 1.7
                divisor = 4.0
                x_exponent = exponent
                y_exponent = exponent
                if abs(move[0] / divisor) > 1:
                    x_exponent = 1.1
                if abs(move[1] / divisor) > 1:
                    y_exponent = 1.1

                move[0] = abs(move[0] / divisor) ** x_exponent if move[0] > 0 else -(
                abs(move[0] / divisor) ** x_exponent)
                move[1] = abs(move[1] / divisor) ** y_exponent if move[1] > 0 else -(
                abs(move[1] / divisor) ** y_exponent)'''

                # protect from large movements when entering
                '''if abs(move[0])>100 or abs(move[1])>100:
                    QCursor.setPos(self.center_x, self.center_y)
                    return'''

                # copy gpu values
                look = self.cam_quat.apply(*[0,0,1])
                #pointer = mm.Quaternion.from_position(move[0],0,move[1]).normalize()
                norm = m.sqrt(move[0]*move[0]+move[1]*move[1])
                x_p = -move[0]/norm
                y_p = move[1] / norm
                pointer = self.cam_quat.apply(*[x_p,y_p,0])
                # side = self.cam_quat.apply(1,0,0)

                mouse_look_prod = np.cross(look,pointer)
                mouse_norm = np.linalg.norm(mouse_look_prod)
                if mouse_norm!=0:
                    mouse_look_prod = (mouse_look_prod/mouse_norm).tolist()
                else:
                    mouse_look_prod = mouse_look_prod.tolist()
                print(norm)
                angle = norm*(self.fov_y/self.height()/2)

                self.cam_quat = self.cam_quat*mm.Quaternion.from_axis(*mouse_look_prod, angle)
                self.cam_quat.normalize()

                QCursor.setPos(self.center_x, self.center_y)

                self.repaint()

    def mousePressEvent(self, event):
        if not self.restraining_mouse:
            self.restraining_mouse = True
            self.center_x = self.geometry().x() + int(self.width() / 2)
            self.center_y = self.geometry().y() + int(self.height() / 2)
            QCursor.setPos(self.center_x, self.center_y)





app = QtWidgets.QApplication([])
window = FlightController()

window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
window.show()
window.load_models("grass block.dae")
app.exec_()