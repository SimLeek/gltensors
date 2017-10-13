import unittest

import minesim.biome_generators as biogen

import numpy as np

import vtk


def convertToNumber (s):
    return int.from_bytes(s.encode(), 'little')

def convertToColor(s):
    i = convertToNumber (s)
    return ((i/(255**2))%1.0, (i/255)%(1.0), i%1.0)

#todo: create 3d testing library for point clouds
class MockModel(object):
    def __init__(self):
        self.dots = []
        pass

    def add_block(self, position, type, immediate = False):
        self.dots.append((*position, convertToColor(type)))

    def batch_blocks(self, array_in, type):
        self.dots = array_in


    def show_cloud(self):
        points = vtk.vtkPoints()

        vertices = vtk.vtkCellArray()

        for d in self.dots:
            p = points.InsertNextPoint((d[0], d[1], d[2]))
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(p)

        cloud = vtk.vtkPolyData()

        cloud.SetPoints(points)
        cloud.SetVerts(vertices)

        # Visualize
        mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            mapper.SetInput(cloud)
        else:
            mapper.SetInputData(cloud)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetPointSize(2)

        renderer = vtk.vtkRenderer()
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.AddRenderer(renderer)
        renderWindowInteractor = vtk.vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(renderWindow)

        renderer.AddActor(actor)

        renderWindow.Render()
        renderWindowInteractor.Start()



class TestBiomeGenerators(unittest.TestCase):
    def testPlainsGen(self):
        mockmod = MockModel()
        mockmod.batch_blocks(biogen.plains_gen( 100, 100, 100, 30, 50, turbulence=0.01), 'grass')
        mockmod.show_cloud()

    def testStoneContainer(self):
        mockmod = MockModel()
        biogen.stone_container_gen(mockmod, 5, 1, 5, height=3)
        mockmod.show_cloud()

    def testCloudLayerGen(self):
        mockmod = MockModel()
        biogen.cloud_layer_gen(mockmod,100, 1, None)
        mockmod.show_cloud()

    def testFoamGen(self):
        mockmod = MockModel()
        biogen.foam_gen(mockmod, 100, 1, 0)
        mockmod.show_cloud()

    def testCaveDig(self):
        self.fail()