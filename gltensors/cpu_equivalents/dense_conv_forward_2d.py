import numpy as np


def dense_conv_forward_2d(inp_image: np.ndarray, kernel: np.ndarray, stride, padding):
    """
    Forward convolution done entirely in Numpy. For speed, please re-implement in C++ or Rust.

    :param inp_image: The input image to be convolved
    :param kernel: The convolution kernel.
    :param stride: how many pixels in between each convolution
    :param padding: how much padding to expect (pre padded) on the border of the input image.
    :return: Convolved output.
    """
    assert len(inp_image.shape) == 3, 'single 2D images only. No batches.'
    assert len(kernel.shape) == 4

    height, width, colors = inp_image.shape
    kernel_height, kernel_width, colors_in, colors_out = kernel.shape
    kernel_stride_x, kernel_stride_y = stride
    kernel_padding_x, kernel_padding_y = padding
    i_f = int(np.floor(kernel_width / 2.0))
    j_f = int(np.floor(kernel_height / 2.0))

    out_pixels = np.zeros((height, width, colors_out))
    for y in range(kernel_padding_y, height - kernel_padding_y, kernel_stride_y):  # todo: add kernel_padding_y and kernel_stride_y fix to glsl
        for x in range(kernel_padding_x, width - kernel_padding_x, kernel_stride_x):  # todo: add kernel_padding_x and kernel_stride_x fix to glsl
            output_select = [y, x, 0]
            input_select = np.asarray(
                [y * kernel_stride_y, x * kernel_stride_x, 0]
            )
            for i in range(-np.int(np.floor(kernel_width / 2.0)), np.int(np.ceil(kernel_width / 2.0))):
                for j in range(-np.int(np.floor(kernel_height / 2.0)), np.int(np.ceil(kernel_height / 2.0))):
                    in_pixel_select = np.copy(input_select)
                    in_pixel_select += [j, i, 0]
                    for co in range(colors_out):
                        output_select[2] = co
                        for ci in range(colors_in):
                            in_pixel_select[2] = ci
                            kernel_select = np.asarray([j_f + j, i_f + i, ci, co])

                            out_pixels[tuple(output_select)] += kernel[tuple(kernel_select)] * inp_image[tuple(in_pixel_select)]
    return out_pixels
