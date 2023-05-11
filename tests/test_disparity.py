import time

from displayarray import display
from tests.data import test_image_1
import os
from gltensors.glsl_util import glsl_import_filter
import gltensors.GLSLComputer as glcpu
import numpy as np
from gltensors.biome_generators import read_in_shader

class DisparityComputer(object):
    def __init__(self):
        self.test_computer = None
        self.width = self.height = None
        self.first_frame = True
        self.in_channels = None
        self.disparity_shader = None
        self._last_disp_out = None
        self.t0=time.time()
        self.t1=time.time()

    def compute(self, img_l, img_r):
        if self.first_frame:
            self.height = img_l.shape[0]
            self.width = img_l.shape[1]
            self.in_channels = img_l.shape[2]

            shader_file = os.sep.join(['shaders', 'disp_2d_forward.glsl'])
            self.disparity_shader = read_in_shader(shader_file)
            #shader_file.close()

            self.test_computer = glcpu.GLSLComputer(self.disparity_shader,
                                               width=self.width,
                                               height=self.height,
                                               in_channels=self.in_channels,
                                               )

            self.first_frame = False

            buff_disp_in = self.test_computer.ctx.buffer(data=np.zeros((self.height, self.width)).astype(dtype=np.int).tobytes())
            buff_disp_in.bind_to_storage_buffer(2)
        elif self._last_disp_out is not None:
            buff_disp_in = self.test_computer.ctx.buffer(data=self._last_disp_out.tobytes())
            buff_disp_in.bind_to_storage_buffer(2)
        else:
            raise NotImplementedError('WTF? How?')

        self.t1 =time.time()
        buff_t = self.test_computer.ctx.buffer(data=np.asarray(self.t1-self.t0).astype(dtype=np.float32).tobytes(), dynamic=True)
        buff_t.bind_to_storage_buffer(4)
        self.t0=self.t1

        buff_l = self.test_computer.ctx.buffer(data=img_l.astype(dtype=np.float32).tobytes(), dynamic=True)
        buff_l.bind_to_storage_buffer(0)

        buff_r = self.test_computer.ctx.buffer(data=img_r.astype(dtype=np.float32).tobytes(), dynamic=True)
        buff_r.bind_to_storage_buffer(1)

        buff_disp_out = self.test_computer.ctx.buffer(
            data=np.zeros((self.height, self.width)).astype(dtype=np.int).tobytes(), dynamic=True)
        buff_disp_out.bind_to_storage_buffer(3)

        self.test_computer.cpu.run(self.height, self.width)

        self._last_disp_out = np.frombuffer(buff_disp_out.read(), dtype=np.int).reshape((self.height, self.width))

        buff_t.release()
        buff_l.release()
        buff_r.release()
        buff_disp_in.release()
        buff_disp_out.release()

        return self._last_disp_out

from tests.train_images import box_left_2, box_right_2
#import torch
#from visualize.right_from_left import right_from_left
from displayarray import display
from sparsepyramids.edge_pyramid import edge
import torch.nn.functional as F
#from loss_functions.img_diff import pyramidal_loss

def rgb_to_grayscale(t: np.ndarray):
    assert t.shape[-1] == 3

    # assuming bgr from opencv
    b = t[..., 0:1]
    g = t[..., 1:2]
    r = t[..., 2:3]

    o = 0.299 * r + 0.587 * g + 0.114 * b
    return o

def limit_image_for_display(t: np.ndarray):
    # todo: move to displayarray
    #t[t<0]=-1
    t = t.astype(np.float32)
    t = np.squeeze(t)
    t = (t-np.min(t)) / (np.max(t)-np.min(t) + 1e-7)
    return t

def test_run_grayscale():
    torch_left_image = tree_left
    torch_right_image = tree_right

    torch_left_image = rgb_to_grayscale(torch_left_image)
    torch_right_image = rgb_to_grayscale(torch_right_image)

    d = display()
    dc = DisparityComputer()

    while True:
        disp = dc.compute(torch_left_image, torch_right_image)

        d.update(limit_image_for_display(disp), 'disparity')
        d.update(np.squeeze(torch_left_image)/255, 'left')
        d.update(np.squeeze(torch_right_image)/255, 'right')

def test_run_rgb():
    torch_left_image = box_left_2
    torch_right_image = box_right_2


    d = display()
    dc = DisparityComputer()

    while True:
        disp = dc.compute(torch_left_image, torch_right_image)

        d.update(limit_image_for_display(disp), 'disparity')
        d.update(np.squeeze(torch_left_image)/255, 'left')
        d.update(np.squeeze(torch_right_image)/255, 'right')

from sparsepyramids.edge_pyramid import image_to_edge_pyramid

def format_torch_img_for_np(img):
    img = torch.permute(img, (0,2,3,1))
    img = torch.squeeze(img)
    img = img.detach().cpu().numpy()
    return img

import torch
from torch.autograd import Variable
from sparsepyramids.recursive_pyramidalize import apply_func_to_nested_tensors, RecursiveChanDepyramidalize2D

def format_np_img_for_torch(img):
    if len(img.shape)==2:
        grab = torch.from_numpy(
            img[np.newaxis, np.newaxis, ...].astype(np.float32) / 255.0
        )
        img = Variable(grab).cuda()
    elif len(img.shape)==3:
        grab = torch.from_numpy(
            img[np.newaxis, ...].astype(np.float32) / 255.0
        )
        grab = torch.permute(grab, (0, 3, 1, 2))
        img = Variable(grab).cuda()
    else:
        raise NotImplementedError
    return img

from tests.train_images import cactus_left, cactus_right, tree_left, tree_right, waterfall_left, waterfall_right
import cv2
from displayarray import breakpoint_display
import pytest

def test_run_wls(capsys):
    wsize = 7
    max_disp = 64
    sigma = 1.5
    lmbda = 8000.0
    tree_l = cv2.cvtColor(cactus_left, cv2.COLOR_BGR2GRAY)
    tree_r = cv2.cvtColor(cactus_right, cv2.COLOR_BGR2GRAY)

    t0 = t1 = time.time()
    d = display()
    with capsys.disabled():
        while True:

            left_matcher = cv2.StereoBM_create(max_disp, wsize)
            right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)
            left_disp = left_matcher.compute(tree_l, tree_r)
            right_disp = right_matcher.compute(tree_r, tree_l)

            # Now create DisparityWLSFilter
            wls_filter = cv2.ximgproc.createDisparityWLSFilter(left_matcher)
            wls_filter.setLambda(lmbda)
            wls_filter.setSigmaColor(sigma)
            filtered_disp = wls_filter.filter(left_disp, tree_l, disparity_map_right=right_disp)
            d.update(limit_image_for_display(filtered_disp), 'depth')

            t1 = time.time()
            print(f'framerate: {1.0/(t1 - t0)}')
            t0 = t1

#import torch.nn.functional as f
#f.linear()

def test_run_grayscale_pyramid_edge(capsys):
    torch_left_image = cactus_left
    torch_right_image = cactus_right

    torch_left_image_orig = rgb_to_grayscale(torch_left_image)
    torch_right_image_orig = rgb_to_grayscale(torch_right_image)

    torch_left_image_orig = format_np_img_for_torch(torch_left_image_orig)
    torch_right_image_orig = format_np_img_for_torch(torch_right_image_orig)

    torch_left_image_pad = F.pad(torch_left_image_orig, [1,1,1,1])
    torch_right_image_pad = F.pad(torch_right_image_orig, [1,1,1,1])

    torch_left_image_p = image_to_edge_pyramid(torch_left_image_pad)
    torch_right_image_p = image_to_edge_pyramid(torch_right_image_pad)

    chan_dp = RecursiveChanDepyramidalize2D()
    torch_left_image = chan_dp.forward(torch_left_image_p)
    torch_right_image = chan_dp.forward(torch_right_image_p)

    #torch_left_image = torch_left_image / (torch.norm(torch_left_image, dim=1) + 1e-6)
    #torch_right_image = torch_right_image / (torch.norm(torch_right_image, dim=1) + 1e-6)

    torch_left_image = torch.cat((torch_left_image_orig, torch_left_image), dim=1)
    torch_right_image = torch.cat((torch_right_image_orig, torch_right_image), dim=1)

    #torch_left_image = torch_left_image[:, 6:, ...]
    #torch_right_image = torch_right_image[:, 6:, ...]



    torch_left_image = format_torch_img_for_np(torch_left_image)
    torch_right_image = format_torch_img_for_np(torch_right_image)

    d = display()
    dc = DisparityComputer()
    t0 = t1 = time.time()
    with capsys.disabled():
        while True:
            disp = dc.compute(torch_left_image, torch_right_image)

            d.update(limit_image_for_display(disp), 'disparity')
            d.update(np.squeeze(torch_left_image[..., 0:3]), 'left')
            d.update(np.squeeze(torch_right_image[..., 0:3]), 'right')

            t1 = time.time()
            print(f'framerate: {1.0 / (t1 - t0)}')
            t0 = t1

