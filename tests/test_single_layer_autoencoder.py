from displayarray import display
import numpy as np
from tests.data import test_image_1
import os
import gltensors.GLSLComputer as glcpu


def test_denoise_cpu():
    d = display(test_image_1, size=(1, 1))

    edge_kernel = np.random.randint(0, 256, (3, 3, 3, 3)).astype(dtype=np.float32) / 127.0

    kernel_height = kernel_width = 3
    kernel_stride_x = kernel_stride_y = 1

    kernel_padding_x = kernel_padding_y = 1
    kernel_dilation_x = kernel_dilation_y = 0

    first_frame = True

    width = height = None

    forward_computer = backward_computer = None

    buffkd = buffo = None

    in_channels = None

    while d:
        if d.frames:
            frame = next(iter(d.frames.values()))[0].astype(np.float32) / 256.0
            noise = np.random.randint(0, 256, frame.shape).astype(dtype=np.float32) / 256.0
            noised_frame = frame + noise
            d.update(noised_frame, 'noised frame')

            if first_frame:
                height = frame.shape[0]
                width = frame.shape[1]
                in_channels = frame.shape[2]
                shader_file = open(
                    os.path.abspath(os.sep.join(['..', 'gltensors', 'shaders', 'dense_conv_forward_2d.glsl'])))
                forward_shader = shader_file.read()
                shader_file.close()

                shader_file = open(
                    os.path.abspath(os.sep.join(['..', 'gltensors', 'shaders', 'dense_conv_2d_backward.glsl'])))
                backward_shader = shader_file.read()
                shader_file.close()

                forward_computer = glcpu.GLSLComputer(forward_shader,
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

                backward_computer = glcpu.GLSLComputer(backward_shader,
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

            forward_computer = glcpu.GLSLComputer(forward_shader,
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

            buffk_f = forward_computer.ctx.buffer(data=edge_kernel.astype(dtype=np.float32).tobytes())
            buffk_f.bind_to_storage_buffer(1)

            buffi_f = forward_computer.ctx.buffer(data=frame.astype(dtype=np.float32).tobytes())
            buffi_f.bind_to_storage_buffer(0)

            buffo_f = forward_computer.ctx.buffer(data=np.zeros_like(frame).astype(dtype=np.float32).tobytes())
            buffo_f.bind_to_storage_buffer(2)

            forward_computer.cpu.run(height, width)
            forward_computer.ctx.finish()

            out_img = np.frombuffer(buffo_f.read(), dtype=np.float32).reshape((height, width, in_channels))

            d.update(out_img, 'out img')

            out_error = out_img - frame

            backward_computer = glcpu.GLSLComputer(backward_shader,
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

            buffk_b = backward_computer.ctx.buffer(data=edge_kernel.astype(dtype=np.float32).tobytes())
            buffk_b.bind_to_storage_buffer(8)

            buffkd = backward_computer.ctx.buffer(data=np.zeros_like(edge_kernel).astype(dtype=np.float32).tobytes())
            buffkd.bind_to_storage_buffer(5)

            buffi_b = backward_computer.ctx.buffer(frame.astype(dtype=np.float32).tobytes())
            buffi_b.bind_to_storage_buffer(7)

            buffid = backward_computer.ctx.buffer(data=np.zeros_like(frame).astype(dtype=np.float32).tobytes())
            buffid.bind_to_storage_buffer(4)

            buffod = backward_computer.ctx.buffer(data=out_error.astype(dtype=np.float32).tobytes())
            buffod.bind_to_storage_buffer(6)

            backward_computer.cpu.run(height, width)
            backward_computer.ctx.finish()

            ind_out = np.frombuffer(buffid.read(), dtype=np.float32).reshape((height, width, in_channels))
            kd_out = np.frombuffer(buffkd.read(), dtype=np.float32).reshape(edge_kernel.shape)

            d.update(out_error, 'out err')
            d.update(ind_out, 'in err')
            print(kd_out)
            edge_kernel -= kd_out / 1.0e7

            buffk_f.release()
            buffi_f.release()
            buffo_f.release()
            buffk_b.release()
            buffkd.release()
            buffid.release()
            buffod.release()
