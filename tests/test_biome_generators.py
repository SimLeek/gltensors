import unittest

import gltensors.biome_generators as biogen

import numpy as np

import vtk

import trimesh
from trimesh.viewer.windowed import SceneViewer

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
    # todo: change this to a non-interactive test, like glsl_compute tests
    # todo: add interactive tests that require y/n == y to pass
    def testFullBiomeGen(self):
        plains = biogen.plains_gen( 500, 500, 100, 30, 50, turbulence=0.01).astype(np.bool_)
        min_h = 0
        max_h = 35
        h = max_h-min_h
        dissipation = 0.05
        # us, but not them boolean operators to remove boolean arrays from other boolean arrays
        # if I run into long strings of operators like these, consider moving back to glsl.
        cave_caves = biogen.cloud_layer_gen(500, 500, h, 0.02, 0.0, 0) & ~biogen.cloud_layer_gen(500, 500, h, 0.1, 0.0, 0)
        cave_caves = biogen.cloud_layer_gen(500, 500, h, 0.005, 0.0, dissipation) & ~cave_caves
        plains[0:500, 0:500, min_h:max_h] = plains[0:500, 0:500, min_h:max_h] & ~cave_caves
        visible_plains = biogen.restrict_visible(plains, plains, show_bounds=True)
        visible_locations = biogen.get_locations(visible_plains)
        mockmod = MockModel()
        mockmod.batch_blocks(visible_locations, 'grass')
        mockmod.show_cloud()

    def test_full_biome_trimesh(self):
        plains = biogen.plains_gen(500, 500, 100, 30, 50, turbulence=0.01).astype(np.bool_)
        min_h = 0
        max_h = 35
        h = max_h - min_h
        dissipation = 0.05
        # us, but not them boolean operators to remove boolean arrays from other boolean arrays
        # if I run into long strings of operators like these, consider moving back to glsl.
        cave_caves = biogen.cloud_layer_gen(500, 500, h, 0.02, 0.0, 0) & ~biogen.cloud_layer_gen(500, 500, h, 0.1, 0.0,
                                                                                                 0)
        cave_caves = biogen.cloud_layer_gen(500, 500, h, 0.005, 0.0, dissipation) & ~cave_caves
        plains[0:500, 0:500, min_h:max_h] = plains[0:500, 0:500, min_h:max_h] & ~cave_caves

        #plains = biogen.plains_gen(100, 100, 50, 30, 50, turbulence=0.025)
        mesh = trimesh.voxel.ops.matrix_to_marching_cubes(matrix=plains)
        #assert mesh.is_watertight
        trimesh.smoothing.filter_laplacian(mesh)
        #mesh.show(flags={'wireframe': True})
        s = trimesh.Scene([mesh])
        s.show(flags={'wireframe': False})

        #glb = trimesh.exchange.gltf.export_glb(s, include_normals=True)
        #with open("terrain.glb", "wb") as f:
        #    f.write(glb)

    def testVisibleGen(self):
        plains = biogen.cloud_layer_gen(100, 100, 50, 0.02, 0.0, 0)
        visible_plains = biogen.restrict_visible(plains, plains, show_bounds=True)
        visible_locations = biogen.get_locations(visible_plains)
        mockmod = MockModel()
        mockmod.batch_blocks(visible_locations, 'grass')
        mockmod.show_cloud()

    def testPlainsGen(self):
        mockmod = MockModel()
        mockmod.batch_blocks(
            biogen.get_locations(
                biogen.plains_gen( 100, 100, 100, 30, 50, turbulence=0.01)
            ), 'grass'
        )
        mockmod.show_cloud()

    def test_plains_trimesh(self):
        dots = biogen.plains_gen(100, 100, 100, 30, 50, turbulence=0.01)
        arr = np.asarray(dots, dtype=bool)

        mesh = trimesh.voxel.ops.matrix_to_marching_cubes(matrix=arr)
        assert mesh.is_watertight

        mesh.show(flags={'wireframe': True})
        s = trimesh.Scene([mesh])
        s.show(flags={'wireframe': True})

    def testStoneContainer(self):
        mockmod = MockModel()
        mockmod.batch_blocks(biogen.get_locations(biogen.stone_container_gen( 100, 100, 100)), 'grass')
        mockmod.show_cloud()

    def testCloudLayerGen(self):
        mockmod = MockModel()
        mockmod.batch_blocks(biogen.get_locations(biogen.cloud_layer_gen(100, 100, 100, 0.02, 0.0, .1)), 'grass')
        mockmod.show_cloud()

    def testFoamGen(self):
        mockmod = MockModel()
        mockmod.batch_blocks(biogen.get_locations(biogen.cloud_layer_gen(100, 100, 100, 0.02, 0.0, 0)), 'grass')
        mockmod.show_cloud()

    def testCaveDig(self):
        mockmod = MockModel()
        mockmod.batch_blocks(biogen.get_locations(biogen.inverse_cloud_layer_gen(100, 100, 100, 0.02, 0.5, .05)), 'grass')
        mockmod.show_cloud()