from enum import Enum


class FlightControls(Enum):
    forward = 1
    back = 2
    left = 3
    right = 4
    roll_cw = 5
    roll_ccw = 6
    up = 7
    down = 8


import gltensors.matmult as mm
import math as m
import numpy as np

from gltensors.updating_window import UpdatingWindow
from gltensors.perspective_window import PerspectiveWindow, VrPerspectiveWindow

from PyQt5 import QtCore
from PyQt5.QtGui import QCursor

try:
    from virtualreality.util import driver

    class VrController(UpdatingWindow, VrPerspectiveWindow):
        def __init__(self,
                     vertex_shader_file=PerspectiveWindow.shader_vertex_perspective,
                     fragment_shader_file=PerspectiveWindow.shader_fragment_black_and_white,
                     *args, **kw):
            super(VrController, self).__init__(vertex_shader_file=vertex_shader_file,
                                               fragment_shader_file=fragment_shader_file,
                                               **kw)
            self.myDriver = driver.DummyDriverReceiver(57)
            self.register_updaters(self.vr_update)
            self.myDriver.start()
            self.original_quat=mm.Quaternion(-0.29609551923914257, 0.6352982400150031, 0.6521352103614712, 0.28886546544566705)
            self.original_pose = np.asarray([-36.64364585, -176.81920739,  -79.70142023])

        def vr_update(self):
            data = self.myDriver.get_pose()
            hmd = data[:13]
            cntl1 = data[13 : 13 + 22]
            cntl2 = data[13 + 22 : 13 + 22 + 22]
            x, y, z, w, rx, ry, rz = hmd[:7]
            ry = -ry
            rx = -rx
            rz = -rz
            self.cam_quat = self.original_quat*mm.Quaternion(rx, ry, rz, w)
            self.cam_pos = self.original_pose + np.asarray([x,y,z])

            if not self.myDriver.alive:
                self.myDriver.close()

except ImportError:
    VrController = None


class FlightController(UpdatingWindow, VrPerspectiveWindow):
    def __init__(self, flight_keys=None, flight_speed=1,
                 vertex_shader_file=PerspectiveWindow.shader_vertex_perspective,
                 fragment_shader_file=PerspectiveWindow.shader_fragment_black_and_white,
                 *args, **kw):
        self.flight_keys = flight_keys
        if self.flight_keys == None:
            self.flight_keys = dict()
            self.flight_keys[QtCore.Qt.Key_W] = FlightControls.forward
            self.flight_keys[QtCore.Qt.Key_S] = FlightControls.back
            self.flight_keys[QtCore.Qt.Key_A] = FlightControls.left
            self.flight_keys[QtCore.Qt.Key_D] = FlightControls.right
        self.active_controls = set()

        self.flight_speed = flight_speed

        super(FlightController, self).__init__(vertex_shader_file=vertex_shader_file,
                                               fragment_shader_file=fragment_shader_file,
                                               **kw)

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
            self.cam_pos += look

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

        # print(f"cam_pos: {self.cam_pos}")
        # print(f"cam_quat: {self.cam_quat.x, self.cam_quat.y, self.cam_quat.z, self.cam_quat.w}")

    def mouseMoveEvent(self, event):
        if self.restraining_mouse:
            # update global center in case window moved
            # int casting protects from stray .5 from odd screen sizes
            self.center_x = self.geometry().x() + int(self.width() / 2)
            self.center_y = self.geometry().y() + int(self.height() / 2)

            cursor_pos = event.globalPos()

            if self.center_x == cursor_pos.x() and self.center_y == cursor_pos.y():
                return  # cursor was re-centered.
            else:

                # get & normalize mouse movement
                move = [int(cursor_pos.x() - self.center_x), int(cursor_pos.y() - self.center_y)]

                # copy gpu values
                look = self.cam_quat.apply(*[0, 0, 1])
                # pointer = mm.Quaternion.from_position(move[0],0,move[1]).normalize()
                norm = m.sqrt(move[0] * move[0] + move[1] * move[1])
                x_p = -move[0] / norm
                y_p = move[1] / norm
                pointer = self.cam_quat.apply(*[x_p, y_p, 0])
                # side = self.cam_quat.apply(1,0,0)

                mouse_look_prod = np.cross(look, pointer)
                mouse_norm = np.linalg.norm(mouse_look_prod)
                if mouse_norm != 0:
                    mouse_look_prod = (mouse_look_prod / mouse_norm).tolist()
                else:
                    mouse_look_prod = mouse_look_prod.tolist()
                # print(norm)
                angle = norm * (self.fov_y / self.height() / 2)

                self.cam_quat = self.cam_quat * mm.Quaternion.from_axis(*mouse_look_prod, angle)
                self.cam_quat.normalize()

                QCursor.setPos(self.center_x, self.center_y)

                self.repaint()

    def mousePressEvent(self, event):
        if not self.restraining_mouse:
            self.restraining_mouse = True
            self.center_x = self.geometry().x() + int(self.width() / 2)
            self.center_y = self.geometry().y() + int(self.height() / 2)
            QCursor.setPos(self.center_x, self.center_y)
