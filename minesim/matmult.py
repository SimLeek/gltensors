import numpy as np
import math as m

def translate_mat(x, y, z, dtype=None):
    return np.matrix(
        [[1, 0, 0, x],
         [0, 1, 0, y],
         [0, 0, 1, z],
         [0, 0, 0, 1]],
        dtype
    )

def scale_mat(x, y, z, dtype=None):
    return np.matrix(
        [[x, 0, 0, 0],
         [0, y, 0, 0],
         [0, 0, z, 0],
         [0, 0, 0, 1]],
        dtype
    )

class Quaternion(object):
    """If you have a long string of quaternions you want to operate on one by one,
    use this python class. If you have a bunch to apply to separate vertices,
    use the glsl class."""

    def __init__(self, x,y,z,w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    @staticmethod
    def from_axis(x_axis, y_axis, z_axis, angle):
        # angle is in radians, because m.sin
        sina = m.sin(angle / 2)
        x = x_axis * sina
        y = y_axis * sina
        z = z_axis * sina
        w = m.cos(angle / 2)
        return Quaternion(x, y, z, w)

    def normalize(self):
        norm = m.sqrt(self.x**2 + self.y**2 + self.z**2 + self.w**2)
        if norm==0: return self
        self.x = self.x / norm
        self.y = self.y / norm
        self.z = self.z / norm
        self.w = self.w / norm
        return self

    def get_axis(self):
        normy = m.sqrt(self.x**2 + self.y**2 + self.z**2 + self.w**2)
        if normy ==0: return [0,0,0]
        w=self.w/normy
        norm = m.sqrt(1-w*w)
        x = self.x / norm
        y = self.y / norm
        z = self.z / norm
        return [x,y,z]

    def get_angle(self):
        angle = 2*m.acos(self.w)
        return angle

    def apply(self, x, y, z):
        v= np.array([x,y,z])
        qvr = np.array([self.x, self.y, self.z])
        return v+2.0*np.cross(np.cross(v,qvr)+self.w*v, qvr)
        #return (self*self.from_position(x,y,z)*(~self)).get_axis()

    @staticmethod
    def from_position(x, y, z):
        return Quaternion(x,y,z,0)

    # def __add__(self, other): # quat+quat (useful for infintesimal/approximate rotations)

    def __invert__(self): # ~quat
        norm = m.sqrt(self.x**2 + self.y**2 + self.z**2 + self.w**2)
        return Quaternion(-self.x/norm, -self.y/norm, -self.z/norm, self.w/norm)

    def __mul__(self, other): # quat*quat
        if (isinstance(other, Quaternion)):
            x=(self.w*other.x)+(self.x*other.w)+(self.y*other.z)-(self.z*other.y)
            y = (self.w * other.y) - (self.x * other.z) + (self.y * other.w) + (self.z * other.x)
            z = (self.w * other.z) + (self.x * other.y) - (self.y * other.x) + (self.z * other.w)
            w = (self.w * other.w) - (self.x * other.x) - (self.y * other.y) - (self.z * other.z)

            return Quaternion(x, y, z, w)
        else:
            return np.dot(_smol_quat_mat(self),np.array(other))


def _smol_quat_mat(q, dtype=None): # total from angle: 2 trig, 2 divisions (=1.33 mults), 15 multiplications, 12 additions
    _2x = 2 * q.x
    _2y = 2 * q.y
    _2z = 2 * q.z
    _2y2 = _2y*q.y
    _2x2 = _2x*q.x
    _2z2 = _2z*q.z
    _2xy = _2x*q.y
    _2xz = _2x*q.z
    _2xw = _2x*q.w
    _2yw = _2y*q.w
    _2yz = _2y*q.z
    _2zw = _2z*q.w
    '''return np.matrix([
        [1 - _2y2 - _2z2, _2xy - _2zw, _2xz + _2yw],
        [_2xy + _2zw, 1 - _2x2 - _2z2, _2yz - _2xw],
        [_2xz - _2yw, _2yz + _2xw, 1 - _2x2 - _2y2],
    ], dtype)'''

    return np.matrix([
            [1-_2y2-_2z2,  _2xy + _2zw,    _2xz - _2yw],
            [_2xy - _2zw,   1-_2x2-_2z2,    _2yz + _2xw],
            [_2xz + _2yw,   _2yz - _2xw,    1-_2x2-_2y2],
        ], dtype)

def quat_mat(q, dtype=None): # total from angle: 2 trig, 2 divisions (=1.33 mults), 15 multiplications, 12 additions
    _2x = 2 * q.x
    _2y = 2 * q.y
    _2z = 2 * q.z
    _2y2 = _2y*q.y
    _2x2 = _2x*q.x
    _2z2 = _2z*q.z
    _2xy = _2x*q.y
    _2xz = _2x*q.z
    _2xw = _2x*q.w
    _2yw = _2y*q.w
    _2yz = _2y*q.z
    _2zw = _2z*q.w
    return np.matrix([
        [1-_2y2-_2z2,  _2xy-_2zw,    _2xz+_2yw, 0],
        [_2xy+_2zw,   1-_2x2-_2z2,    _2yz-_2xw, 0],
        [_2xz-_2yw,   _2yz+_2xw,    1-_2x2-_2y2, 0],
        [0, 0, 0, 1]
    ], dtype)

"""def axis_angle_mat(x,y,z,angle, dtype): #2 trig, 24 multiplications, 7 additions: slower
    c = m.cos(angle)
    s = m.sin(angle)
    n = 1-c
    return np.matrix([
        [x*x*n+c,   x*y*n-z*s,  x*z*n+y*s],
        [y*x*n+z*s, y*y*n+c,    y*z*n-x*s],
        [z*x*n-y*s, z*y*n+x*s,  z*z*n+c]
    ])"""

def axis_angle_mat(x,y,z,angle, dtype=None):
    return quat_mat(Quaternion.from_axis(x,y,z,angle), dtype)

def scale_rot_trans_mat(xs, ys, zs, xt, yt, zt, xv,yv,zv,angle, dtype=None):
    return quat_mat(Quaternion.from_axis(xv,yv,zv,angle), dtype) * translate_mat(xt,yt,zt,dtype) * scale_mat(xs,ys,zs,dtype)

def rot_trans_mat(xt, yt, zt, xv,yv,zv,angle, dtype=None):
    return quat_mat(Quaternion.from_axis(xv,yv,zv,angle), dtype) * translate_mat(xt,yt,zt,dtype)

def perspective_mat(z_near, z_far, fov_y, ratio, dtype = None):  # type: (...)->np.matrix
    z_mul = (-2.0*z_near*z_far) / (z_far - z_near)
    y_mul = -1.0 * m.tan(fov_y)
    x_mul = y_mul / ratio
    f_mul = -(z_far+z_near)/(z_far-z_near)

    return np.matrix([
        [x_mul, 0, 0, 0],
        [0, y_mul, 0, 0],
        [0, 0, -1, z_mul],
        [0, 0, -1, 0]
    ], dtype)

def id_mat( dtype = None):
    return np.matrix([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype)

# send matrix to glsl:
# keep quaternion by multiplying constantly and applying that kept quaternion
#  (local translation): kept_matrix = perspective_mat*axis_angle_mat(kept quat)*translate_mat
#  (global translation): kept_matrix = perspective_mat*axis_angle_mat(inv to global)*translate_mat*axis_angle_mats

# todo: don't really need this until you're animating 3D models with lots of bones.
glsl = \
"""
#version 150
in vec4 gxl3d_Position;
uniform mat4 gxl3d_ViewProjectionMatrix;

struct Transform //translate and rotate
{
  vec4 position;
  vec4 axis_angle;
};
uniform Transform T;

vec4 quat_from_axis_angle(vec3 axis, float angle)
{
  vec4 qr;
  float half_angle = (angle * 0.5) * 3.14159 / 180.0;
  qr.x = axis.x * sin(half_angle);
  qr.y = axis.y * sin(half_angle);
  qr.z = axis.z * sin(half_angle);
  qr.w = cos(half_angle);
  return qr;
}

vec3 rotate_vertex_position(vec3 position, vec3 axis, float angle)
{
  vec4 q = quat_from_axis_angle(axis, angle);
  vec3 v = position.xyz;
  return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v);
}

void main()
{
  vec3 P = rotate_vertex_position(gxl3d_Position.xyz, T.axis_angle.xyz, T.axis_angle.w);
  P += T.position.xyz;
  gl_Position = gxl3d_ViewProjectionMatrix * vec4(P, 1);
}
"""

if __name__ == '__main__':
    quat = Quaternion.from_axis(1,0,0,m.pi/2.0)
    print(quat)
    loc = quat.apply(0,0,1)
    print(loc)