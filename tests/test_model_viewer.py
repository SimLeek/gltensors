import unittest as ut
from PyQt5 import QtWidgets
from gltensors.model_instancer import ModelViewer, model_dir
import gltensors.biome_generators as biogen
import os
import numpy as np


class TestPerspectiveWindow(ut.TestCase):
    def testRunsFull(self):
        app = QtWidgets.QApplication([])
        window = ModelViewer()
        # window.load_model_file_into_cache(os.path.dirname(os.path.realpath(__file__))\
        #                           + os.sep + 'blocks' + os.sep + 'cube.obj')

        plains = biogen.plains_gen(100, 100, 100, 30, 50, turbulence=0.01).astype(np.bool_)
        min_h = 0
        max_h = 35
        h = max_h - min_h
        dissipation = 0.05
        # us, but not them boolean operators to remove boolean arrays from other boolean arrays
        # if I run into long strings of operators like these, consider moving back to glsl.
        cave_caves = biogen.cloud_layer_gen(100, 100, h, 0.02, 0.0, 0) & ~biogen.cloud_layer_gen(100, 100, h, 0.1, 0.0,
                                                                                                 0)
        cave_caves = biogen.cloud_layer_gen(100, 100, h, 0.005, 0.0, dissipation) & ~cave_caves
        plains[0:100, 0:100, min_h:max_h] = plains[0:100, 0:100, min_h:max_h] & ~cave_caves
        visible_plains = biogen.restrict_visible(plains, plains, show_bounds=True)
        visible_locations = biogen.get_locations(visible_plains)

        window.load_model_file_into_positions(model_dir + os.sep + 'cube.obj',
                                              visible_locations)

        window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
        window.show()

        app.exec_()

    def testRunsSimple(self):
        app = QtWidgets.QApplication([])
        window = ModelViewer()
        window.load_model_file_into_cache(model_dir + os.sep + 'cube.obj')

        window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
        window.show()

        app.exec_()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = ModelViewer()

    box = biogen.cloud_layer_gen(100, 100, 100, turbulence=.1).astype(np.bool_)
    box[40:60, 40:60, :50] = 0
    box[40:60, 40:60, 50] = 1
    visible_plains = biogen.restrict_visible(box, box, show_bounds=True)
    visible_locations = biogen.get_locations(visible_plains)

    window.load_model_file_into_positions(model_dir + os.sep + 'cube.obj',
                                          visible_locations)

    window.set_pose([-98.8408158,  -99.12608922, -92.22389428,
                    -0.658406950671679, -0.24820071143414202, -0.23584931400634193, 0.670277401702866])

    window.move(QtWidgets.QDesktopWidget().rect().center() - window.rect().center())
    window.show()

    app.exec_()
