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
    for y in range(kernel_padding_y, height - kernel_padding_y,
                   kernel_stride_y):  # todo: add kernel_padding_y and kernel_stride_y fix to glsl
        for x in range(kernel_padding_x, width - kernel_padding_x,
                       kernel_stride_x):  # todo: add kernel_padding_x and kernel_stride_x fix to glsl
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

                            out_pixels[tuple(output_select)] += kernel[tuple(kernel_select)] * inp_image[
                                tuple(in_pixel_select)]
    return out_pixels


def dense_conv_forward_2d_fast(
        inp_image: np.ndarray,
        filter: np.ndarray,
        output: np.ndarray,
        strides,
        padding):
    """
    Forward convolution done entirely in Numpy. For speed, please re-implement in C++ or Rust.

    :param inp_image: The input image to be convolved
    :param filter: The convolution kernel.
    :param strides: how many pixels in between each convolution
    :param padding: how much padding to expect (pre padded) on the border of the input image.
    :return: Convolved output.
    """
    INPUT_DIMENSIONS = 4
    HEIGHT_IDX = 2  # H
    WIDTH_IDX = 3  # W
    INPUT_CHANNELS_IDX = 1  # C
    OUTPUT_CHANNELS_IDX = 0  # K
    NUM_IMAGES_IDX = 0  # N

    x_shape = inp_image.shape
    f_shape = filter.shape
    o_shape = output.shape

    if len(x_shape) != INPUT_DIMENSIONS or len(f_shape) != INPUT_DIMENSIONS or len(o_shape) != INPUT_DIMENSIONS:
        raise RuntimeError("conv2d: input, filter, and output must all have four dimensions.")

    assert (x_shape[HEIGHT_IDX] % strides[1] == 0, "Input height is not evenly divisible by stride size.")
    assert (x_shape[WIDTH_IDX] % strides[0] == 0, "Input width is not evenly divisible by stride size.")
    assert (x_shape[INPUT_CHANNELS_IDX] == f_shape[INPUT_CHANNELS_IDX],
            "Number of channels in input does not match number channels expected by convolution.")
    assert (o_shape[OUTPUT_CHANNELS_IDX] == f_shape[OUTPUT_CHANNELS_IDX],
            "Number of channels in output does not match number channels expected by convolution.")

    N = x_shape[NUM_IMAGES_IDX]
    H = x_shape[HEIGHT_IDX]
    W = x_shape[WIDTH_IDX]
    K = f_shape[OUTPUT_CHANNELS_IDX]
    C = f_shape[INPUT_CHANNELS_IDX]
    R = f_shape[HEIGHT_IDX]
    S = f_shape[WIDTH_IDX]
    P = (x_shape[HEIGHT_IDX] - f_shape[HEIGHT_IDX]) / strides[1] + 1  # output height
    Q = (x_shape[WIDTH_IDX] - f_shape[WIDTH_IDX]) / strides[0] + 1  # output width

    assert (o_shape[HEIGHT_IDX] == P, f"Output height should be {P}.")
    assert (o_shape[WIDTH_IDX] == Q, f"Output width should be {Q}.")

    # output[...] = 0

    for i in range(0, (H - R) + 1, strides[1]):
        y = int(i / strides[1])
        for j in range(0, (W - S) + 1, strides[0]):
            x = int(j / strides[1])
            inp_view = inp_image[:, :, i:i + R, j:j + S]
            for k in range(0, K):
                f_slice = filter[k, :, :, :]
                prod = np.sum(inp_view * f_slice, (INPUT_CHANNELS_IDX, HEIGHT_IDX, WIDTH_IDX))
                output[:, k, y, x] = prod
