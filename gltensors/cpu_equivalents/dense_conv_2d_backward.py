import numpy as np


def dense_conv_backward_2d(
        inp_image: np.ndarray,
        kernel: np.ndarray, stride, padding,
        d_out_image: np.ndarray,
):
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

    d_inp_image = np.zeros_like(inp_image).astype(np.float32)
    d_kernel = np.zeros_like(kernel).astype(np.float32)

    height, width, colors = inp_image.shape
    kernel_height, kernel_width, colors_in, colors_out = kernel.shape
    kernel_stride_x, kernel_stride_y = stride
    kernel_padding_x, kernel_padding_y = padding
    i_f = int(np.floor(kernel_width / 2.0))
    j_f = int(np.floor(kernel_height / 2.0))

    for y in range(kernel_padding_y, height - kernel_padding_y,
                   kernel_stride_y):  # todo: add kernel_padding_y and kernel_stride_y fix to glsl
        for x in range(kernel_padding_x, width - kernel_padding_x,
                       kernel_stride_x):  # todo: add kernel_padding_x and kernel_stride_x fix to glsl
            output_select = np.asarray([y, x, 0])
            input_select = np.asarray(
                [y * kernel_stride_y, x * kernel_stride_x, 0]
            )
            for i in range(-np.int(np.floor(kernel_width / 2.0)), np.int(np.ceil(kernel_width / 2.0))):
                for j in range(-np.int(np.floor(kernel_height / 2.0)), np.int(np.ceil(kernel_height / 2.0))):
                    out_pixel_select = np.copy(output_select)
                    out_pixel_select += [j, i, 0]
                    for co in range(colors_out):
                        out_pixel_select[2] = co
                        for ci in range(colors_in):
                            kernel_select = np.asarray([j_f + j, i_f + i, ci, co])
                            kernel_select_t = np.asarray([j_f - j - 1, i_f - i - 1, ci, co])
                            input_select[2] = ci

                            d_inp_image[tuple(input_select)] += \
                                d_out_image[tuple(out_pixel_select)] * kernel[tuple(kernel_select_t)]
                            d_kernel[tuple(kernel_select)] += \
                                inp_image[tuple(input_select)] * d_out_image[tuple(out_pixel_select)]
    return d_inp_image, d_kernel


def dense_conv_backward_2d_fast(
        inp_image: np.ndarray,
        d_inp_image: np.ndarray,
        filter: np.ndarray,
        d_filter: np.ndarray,
        d_out_image: np.ndarray,
        strides=(1, 1),  # x, then y
        padding=(1, 1),
):
    """
    Forward convolution done entirely in Numpy. For speed, please re-implement in C++ or Rust.

    :param inp_image: The input image to be convolved
    :param kernel: The convolution kernel.
    :param stride: how many pixels in between each convolution
    :param padding: how much padding to expect (pre padded) on the border of the input image.
    :return: Convolved output.
    """
    INPUT_DIMENSIONS = 4
    HEIGHT_IDX = 2  # H
    WIDTH_IDX = 3  # W
    INPUT_CHANNELS_IDX = 1  # C
    OUTPUT_CHANNELS_IDX = 0  # K
    NUM_IMAGES_IDX = 0  # N

    inp_shape = inp_image.shape
    f_shape = filter.shape
    d_out_shape = d_out_image.shape

    if len(inp_shape) != INPUT_DIMENSIONS or len(f_shape) != INPUT_DIMENSIONS or len(d_out_shape) != INPUT_DIMENSIONS:
        raise RuntimeError("conv2d backward: input, filter, and output error must all have four dimensions.")

    fi = filter.copy()
    fi = np.flip(fi, (2, 3))

    N = inp_shape[NUM_IMAGES_IDX]
    H = inp_shape[HEIGHT_IDX]
    W = inp_shape[WIDTH_IDX]
    K = f_shape[OUTPUT_CHANNELS_IDX]
    C = f_shape[INPUT_CHANNELS_IDX]
    R = f_shape[HEIGHT_IDX]
    S = f_shape[WIDTH_IDX]
    P = d_out_shape[HEIGHT_IDX]
    Q = d_out_shape[WIDTH_IDX]

    d_inp_image[...] = 0
    d_filter[...] = 0

    for i in range(0, int((H-R)/strides[1])+1):  # todo: add kernel_padding_y and kernel_stride_y fix to glsl
        for j in range(0, int((W-S)/strides[0])+1):  # todo: add kernel_padding_x and kernel_stride_x fix to glsl
            out_select = d_out_image[:, :, i:i+R, j:j+S]
            y_i = i * strides[1]
            x_i = j * strides[0]
            for k in range(0, K):
                fi_slice = fi[k:k+1, :, :, :]
                inp_select = inp_image[:, :, y_i:y_i+R, x_i:x_i+S]
                prod_inp_img = np.sum(out_select * fi_slice, INPUT_CHANNELS_IDX)
                prod_inp_filt = np.sum(out_select * inp_select, INPUT_CHANNELS_IDX)
                d_filter[k, :, :, :] += prod_inp_filt
                d_inp_image[:, :, y_i:y_i+R, x_i:x_i+S] += prod_inp_img

