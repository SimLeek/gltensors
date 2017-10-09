from pyparsing import Word, Combine, Literal, Optional, nums, CaselessLiteral, White, alphanums, Group, OneOrMore

import re

class Object3D(object):
    def __init__(self):
        self.vertices = []

    def set_name(self, name):
        self.name = name

    def add_vertex(self, x, y, z):
        self.vertices.append((x,y,z))

    def set_material_file(self, filename):
        self.material_file = filename

mtllib_id = Literal('mtllib')
o_id = Literal('o')
v_id = Literal('v')
vt_id = Literal('vt')
vn_id = Literal('vn')
usemtl_id = Literal('usemtl')
s_id = Literal('s')
f_id = Literal('f')

filename = Combine(Word(alphanums)+Literal('.')+Word(alphanums))
mtllib = Combine(mtllib_id + White(' ') + filename)

object = Combine(o_id+ White(' ')+Word(alphanums))

plus_minus = Literal('+') | Literal('-')
number = Word(nums)
integer = Combine(Optional(plus_minus) + number)
point = Literal('.')
e = CaselessLiteral('E')
float_num = Combine(integer+
                    Optional(point + Optional(number))+
                    Optional(e + integer)
                    ).leaveWhitespace()
vertex = Combine(v_id + White(' ') +
                 float_num + White(' ') +
                 float_num + White(' ') +
                 float_num)

vertex_texture = Combine(vt_id + White(' ') +
                 float_num + White(' ') +
                 Optional(float_num + White(' ')) +
                 Optional(float_num))

vertex_normal = Combine(vn_id + White(' ') +
                 float_num + White(' ') +
                 float_num + White(' ') +
                 float_num)


usemtl = Combine(usemtl_id + White(' ') + Word(alphanums))

smoothing_group = Combine(s_id + White(' ') + Word(alphanums))

slash = Literal('/')

face_vertex = Combine(integer + slash +
                      Optional(integer) + slash +
                      Optional(integer))

face = Combine(f_id + White(' ') + OneOrMore(Group(face_vertex) + Optional(White(' '))))

def import_obj(file):
    the_object = Object3D() # type:Object3D
    with open(file) as f:
        lines = f.readlines()
        for line in lines:
            # discard comments
            comment = re.compile("#.*")
            line = comment.split(line)
            line = line[0]

            mtllib_line = mtllib.searchString(line)
            if len(mtllib_line)>0:
                mtllib_line = mtllib_line[0]
                the_file = filename.searchString(mtllib_line)[0][0]
                the_object.set_material_file(the_file)

            o_line = object.searchString(line)
            if len(o_line)>0:
                o_line = o_line[0]
                name = Word(alphanums).searchString(o_line)[1][0]
                the_object.set_name(name)

            v_line = vertex.searchString(line)
            if len(v_line)>0:
                v_line = v_line[0]
                x, y, z = float_num.searchString(v_line)
                the_object.add_vertex(float(x[0]), float(y[0]), float(z[0]))

            vt_line = vertex_texture.searchString(line)
            if len(vt_line) > 0:
                vt_line = vt_line[0]
                xyz = float_num.searchString(vt_line)
                print(float(xyz[0][0]),
                      float(xyz[1][0]) if len(xyz) > 1 else None,
                      float(xyz[2][0]) if len(xyz) > 2 else None,
                      )
                #the_object.add_vertex_texture(float(x[0]), float(y[0]), float(z[0]))

            vn_line = vertex_normal.searchString(line)
            if len(vn_line) > 0:
                vn_line = vn_line[0]
                x, y, z = float_num.searchString(vn_line)
                print(float(x[0]), float(y[0]), float(z[0]))
                #the_object.add_vertex(float(x[0]), float(y[0]), float(z[0]))

            usemtl_line = usemtl.searchString(line)
            if len(usemtl_line) > 0:
                usemtl_line = usemtl_line[0]
                name = Word(alphanums).searchString(usemtl_line)[1][0]
                print(name)
                #the_object.set_name(name)

            smoothing_group_line = smoothing_group.searchString(line)
            if len(smoothing_group_line) > 0:
                smoothing_group_line = smoothing_group_line[0]
                name = Word(alphanums).searchString(smoothing_group_line)[1][0]
                print(name)
                # the_object.set_name(name)

            face_line = face.searchString(line)
            if len(face_line) > 0:
                face_line = face_line[0]
                for face_v in face_vertex.searchString(face_line):
                    print(face_v) # todo: use regex to split the line here and get the parts

            #words = line.split()
            #for word in words:
            #    print(word)



if __name__=="__main__":
    import_obj("blocks/cube.obj")