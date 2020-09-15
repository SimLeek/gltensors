from displayarray import display
import numpy as np
import itertools
import math as m
from typing import List
import gltensors.GLSLComputer as glcpu
import os
from gltensors.glsl_util import glsl_import_filter
from tests.data import test_image_1, test_image_smol, test_image_smol_smol


def center_surround_tensor(ndim,  # type: int
                           center_in,  # type: List[int]
                           center_out,  # type: List[int]
                           surround_in,  # type: List[int]
                           surround_out  # type: List[int]
                           ):
    """Generates a multi-channel center center surround matrix. Useful for isolating or enhancing edges.

    Note: center-surround tensors with 11 or more dimensions may take a while to generate. Make sure you cache those.

    :param ndim: number of dimensions
    :param center_in: input tensor of ints representing colors to look for in the center
    :param center_out: input tensor representing colors to output when more center is detected
    :param surround_in: tensor representing colors to look for outside of center
    :param surround_out: tensor representing colors to output when more surround color is detected
    """
    assert ndim >= 1

    center_surround = np.ndarray(shape=[3 for _ in range(ndim)] + [len(center_in), len(center_out)])

    total = 0
    for tup in itertools.product(*[range(3) for _ in range(ndim)]):
        inv_manhattan_dist = sum([abs(t - 1) for t in tup])
        if inv_manhattan_dist == 0:
            center_surround[tup] = [[0 for _ in center_out] for _ in center_in]
        else:
            euclidian_dist = 1. / m.sqrt(inv_manhattan_dist)
            center_surround[tup] = [[o * i * euclidian_dist for o in surround_out] for i in surround_in]
            total += euclidian_dist
    center_index = tuple([1 for _ in range(ndim)])
    center_surround[center_index] = [[o * i * total for o in center_out] for i in center_in]
    return center_surround


def normalize_tensor_positive_negative(tensor,  # type: np.ndarray
                                       positive_value=1.0,
                                       negative_value=1.0,
                                       epsilon=1e-12):
    """ Normalizes a tensor so values above zero all add up to positive_value, and values below zero add up to
    -negative_value.

    :param tensor: Input tensor to normalize.
    :param positive_value: Positive parts of the tensor will sum up to this value.
    :param negative_value: Negative parts of the tensor will sum up to this value.
    :return: Normalized tensor.
    """
    sum_pos = max(sum([abs(x) if x > 0 else 0 for x in np.nditer(tensor)]), epsilon)
    sum_neg = max(sum([abs(x) if x < 0 else 0 for x in np.nditer(tensor)]), epsilon)
    for tup in itertools.product(*[range(x) for x in tensor.shape]):
        if tensor[tup] > 0:
            tensor[tup] *= positive_value / sum_pos
        if tensor[tup] < 0:
            tensor[tup] *= negative_value / sum_neg
    return tensor


def midget_rgc(n  # type: int
               ):  # type: (...)->np.ndarray
    """Returns a tensor that can convolve a color image for better edge_orientation_detector detection.

    Based off of human retinal ganglian cells.

    :param n: number of dimensions
    :return: tensor used for convolution
    """
    d = 1.
    out = \
        center_surround_tensor(n, center_in=[d, 0, 0], center_out=[d, 0, 0],
                               surround_in=[-d, 0, 0], surround_out=[d, 0, 0]) + \
        center_surround_tensor(n, center_in=[0, d, 0], center_out=[0, d, 0],
                               surround_in=[0, -d, 0], surround_out=[0, d, 0]) + \
        center_surround_tensor(n, center_in=[0, 0, d], center_out=[0, 0, d],
                               surround_in=[0, 0, -d], surround_out=[0, 0, d])

    return normalize_tensor_positive_negative(out, 4.0, -2)


def test_forward_edge_detect_glsl():
    d = display(test_image_1, size=(1, 1))

    first_frame = True

    edge_kernel = midget_rgc(2)

    kernel_height = kernel_width = 3
    kernel_stride_x = kernel_stride_y = 1

    kernel_padding_x = kernel_padding_y = 1
    kernel_dilation_x = kernel_dilation_y = 0

    width = height = None

    test_computer = None

    buffi = buffo = None

    while d:
        if d.frames:
            frame = next(iter(d.frames.values()))
            if first_frame:
                height = frame[0].shape[0]
                width = frame[0].shape[1]
                in_channels = frame[0].shape[2]

                shader_file = open(
                    os.path.abspath(os.sep.join(['..', 'gltensors', 'shaders', 'dense_conv_forward_2d.glsl'])))
                simplex_shader = shader_file.read()
                shader_file.close()

                simplex_shader = glsl_import_filter(simplex_shader,
                                                    os.path.abspath(os.sep.join(['..', 'gltensors', 'shaders'])))

                test_computer = glcpu.GLSLComputer(simplex_shader,
                                                   width=width,
                                                   height=height,
                                                   in_channels=in_channels,
                                                   out_channels=in_channels,
                                                   kernel_width=kernel_width,
                                                   kernel_height=kernel_height,
                                                   kernel_stride_x=kernel_stride_x,
                                                   kernel_stride_y=kernel_stride_y,
                                                   kernel_padding_x=kernel_padding_x,
                                                   kernel_padding_y=kernel_padding_y,
                                                   kernel_dilation_x=kernel_dilation_x,
                                                   kernel_dilation_y=kernel_dilation_y
                                                   )

                first_frame = False

                buffk = test_computer.ctx.buffer(data=edge_kernel.astype(dtype=np.float32).tobytes())
                buffk.bind_to_storage_buffer(1)

            buffi = test_computer.ctx.buffer(data=frame[0].astype(dtype=np.float32).tobytes(), dynamic=True)
            buffi.bind_to_storage_buffer(0)

            buffo = test_computer.ctx.buffer(
                data=np.zeros_like(frame[0]).astype(dtype=np.float32).tobytes(), dynamic=True)
            buffo.bind_to_storage_buffer(2)

            # buffi.write(d.frames['0'][0].astype(dtype=np.float32).tobytes())
            # buffo.clear()

            test_computer.cpu.run(height, width)

            edge_out = np.frombuffer(buffo.read(), dtype=np.float32).reshape((height, width, in_channels))

            d.update(edge_out / edge_out.max(), 'blur')

            buffi.release()
            buffo.release()


from gltensors.cpu_equivalents.dense_conv_forward_2d import dense_conv_forward_2d


def test_forward_rgc_cpu():
    d = display(test_image_smol, size=(1, 1))

    edge_kernel = midget_rgc(2)

    kernel_stride_x = kernel_stride_y = 1

    kernel_padding_x = kernel_padding_y = 1
    kernel_dilation_x = kernel_dilation_y = 0

    while d:
        if d.frames:
            frame = next(iter(d.frames.values()))

            in_frame = frame[0].astype(dtype=np.float32)

            edge_out = dense_conv_forward_2d(in_frame, edge_kernel,
                                             (kernel_stride_x, kernel_stride_y), (kernel_padding_x, kernel_padding_y))

            d.update(edge_out / 256.0, 'blur')


def test_backpropogate_diffs():
    d = display(test_image_1, size=(1, 1))

    first_frame = True

    edge_kernel = np.zeros_like(midget_rgc(2))

    kernel_height = kernel_width = 3
    kernel_stride_x = kernel_stride_y = 1

    kernel_padding_x = kernel_padding_y = 1
    kernel_dilation_x = kernel_dilation_y = 0

    width = height = None

    test_computer = None

    buffkd = buffo = None

    while d:
        if d.frames:
            if first_frame:
                height = d.frames['0'][0].shape[0]
                width = d.frames['0'][0].shape[1]
                in_channels = d.frames['0'][0].shape[2]

                shader_file = open(
                    os.path.abspath(os.sep.join(['..', 'gltensors', 'shaders', 'dense_conv_2d_backward.glsl'])))
                simplex_shader = shader_file.read()
                shader_file.close()

                simplex_shader = glsl_import_filter(simplex_shader,
                                                    os.path.abspath(os.sep.join(['..', 'gltensors', 'shaders'])))

                test_computer = glcpu.GLSLComputer(simplex_shader,
                                                   width=width,
                                                   height=height,
                                                   in_channels=in_channels,
                                                   out_channels=in_channels,
                                                   kernel_width=kernel_width,
                                                   kernel_height=kernel_height,
                                                   kernel_stride_x=kernel_stride_x,
                                                   kernel_stride_y=kernel_stride_y,
                                                   kernel_padding_x=kernel_padding_x,
                                                   kernel_padding_y=kernel_padding_y,
                                                   kernel_dilation_x=kernel_dilation_x,
                                                   kernel_dilation_y=kernel_dilation_y
                                                   )

                first_frame = False

                buffk = test_computer.ctx.buffer(data=edge_kernel.astype(dtype=np.float32).tobytes())
                buffk.bind_to_storage_buffer(4)

                buffkd = test_computer.ctx.buffer(data=edge_kernel.astype(dtype=np.float32).tobytes())
                buffkd.bind_to_storage_buffer(1)

            buffi = test_computer.ctx.buffer(
                np.random.randint(0, 127, d.frames['0'][0].shape).astype(dtype=np.float32).tobytes(), dynamic=True)
            buffi.bind_to_storage_buffer(3)

            buffid = test_computer.ctx.buffer(data=np.zeros_like(d.frames['0'][0]).astype(dtype=np.float32).tobytes(),
                                              dynamic=True)
            buffid.bind_to_storage_buffer(0)

            buffod = test_computer.ctx.buffer(
                data=np.random.randint(0, 127, d.frames['0'][0].shape).astype(dtype=np.float32).tobytes(), dynamic=True)
            buffod.bind_to_storage_buffer(2)

            test_computer.cpu.run(height, width)

            ind_out = np.frombuffer(buffid.read(), dtype=np.float32).reshape((height, width, in_channels))
            kd_out = np.frombuffer(buffkd.read(), dtype=np.float32).reshape(edge_kernel.shape)

            buffi.release()
            buffid.release()
            buffod.release()


from gltensors.cpu_equivalents.dense_conv_2d_backward import dense_conv_backward_2d


def test_backpropogate_diffs_cpu():
    d = display(test_image_smol, size=(1, 1))

    edge_kernel = np.random.randint(0, 127, midget_rgc(2).shape).astype(dtype=np.float32) / 127.0

    kernel_stride_x = kernel_stride_y = 1

    kernel_padding_x = kernel_padding_y = 1
    kernel_dilation_x = kernel_dilation_y = 0

    while d:
        if d.frames:
            frame = next(iter(d.frames.values()))[0].astype(np.float32)
            out_error = np.random.randint(0, 127, frame.shape).astype(dtype=np.float32) / 127.0

            d_inp_image, d_kernel = dense_conv_backward_2d(frame,
                                                           edge_kernel,
                                                           (kernel_stride_x, kernel_stride_y),
                                                           (kernel_padding_x, kernel_padding_y),
                                                           out_error)

            d.update(out_error, 'out err')
            d.update(d_inp_image / d_inp_image.max(), 'in err')
            print(d_kernel)


def test_denoise_cpu():
    d = display(test_image_smol_smol, size=(1, 1))

    edge_kernel = np.random.randint(0, 127, midget_rgc(2).shape).astype(dtype=np.float32) / 127.0

    kernel_stride_x = kernel_stride_y = 1

    kernel_padding_x = kernel_padding_y = 1
    kernel_dilation_x = kernel_dilation_y = 0

    while d:
        if d.frames:
            frame = next(iter(d.frames.values()))[0].astype(np.float32)/256.0
            noise = np.random.randint(0, 127, frame.shape).astype(dtype=np.float32)/256.0
            noised_frame = frame + noise
            d.update(noised_frame, 'noised frame')

            out_img = dense_conv_forward_2d(noised_frame,
                                            edge_kernel,
                                            (kernel_stride_x, kernel_stride_y),
                                            (kernel_padding_x, kernel_padding_y))
            d.update(out_img, 'out img')

            out_error = out_img - frame
            d_inp_image, d_kernel = dense_conv_backward_2d(frame,
                                                           edge_kernel,
                                                           (kernel_stride_x, kernel_stride_y),
                                                           (kernel_padding_x, kernel_padding_y),
                                                           out_error)

            d.update(out_error, 'out err')
            d.update(d_inp_image / d_inp_image.max(), 'in err')
            print(d_kernel)
            edge_kernel -= d_kernel/1.0e4


if __name__ == '__main__':
    test_forward_edge_detect_glsl()
