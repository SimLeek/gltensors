import unittest

import MineSim.biome_generators as biogen

import matplotlib
#matplotlib.use('gtk3cairo')
matplotlib.use('qt5agg') # best so far!

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np



def convertToNumber (s):
    return int.from_bytes(s.encode(), 'little')

def convertToColor(s):
    i = convertToNumber (s)
    return ((i/(255**2))%1.0, (i/255)%(1.0), i%1.0)

class MockModel(object):
    def __init__(self):
        self.dots = []
        pass

    def add_block(self, position, type, immediate = False):
        self.dots.append((*position, convertToColor(type)))

    def show_scatter(self):
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1, projection='3d')
        for dot in self.dots:
            #swap y and z to match glsl
            ax.scatter(dot[0], dot[1], dot[2], c=dot[3], marker='.')

        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.set_zlabel('Y')

        plt.show()

    def show_wire(self):
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1, projection='3d')
        # swap y and z to match glsl
        ax.plot_wireframe([dot[0] for dot in self.dots],
                          [dot[1] for dot in self.dots],
                          [dot[2] for dot in self.dots])

        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.set_zlabel('Y')

        plt.show()


class TestBiomeGenerators(unittest.TestCase):
    def testPlainsGenSmall(self):
        mockmod = MockModel()
        biogen.plains_gen(mockmod, 10, 1, None)
        mockmod.show_scatter()

    def testPlainsGenLarge(self):
        mockmod = MockModel()
        biogen.plains_gen(mockmod, 100, 1, None)
        mockmod.show_wire()

    def testStoneContainer(self):
        mockmod = MockModel()
        biogen.stone_container_gen(mockmod, 5, 1, 5, height=3)
        mockmod.show_scatter()

    def testCloudLayerGen(self):
        pass