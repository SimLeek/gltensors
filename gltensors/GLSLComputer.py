import moderngl
import warnings

class GLSLComputer(object):
    def __init__(self, compute_shader, require=450, info=False, **named_args):
        # todo: manually or automatically selecting GPUs requires setting the extensions:
        #  automatic:
        #   AMD_gpu_association
        #   AmdPowerXpressRequestHighPerformance
        #  manual:
        #   WGL_NV_gpu_affinity
        #   AMD_gpu_association
        #  This will require another backend.
        #  For now, you can select GPU by using NVidia or AMD control panels.

        self.ctx = moderngl.create_standalone_context(require=require)

        self.compute_info = {}
        for a, b in self.ctx.info.items():
            if 'COMPUTE' in a:
                self.compute_info[a] = b

        self.cpu = self.ctx.compute_shader(compute_shader)

        for name, value in named_args.items():
            if name in self.cpu:
                self.cpu[name].value = value
            else:
                warnings.warn(f'{name} is not in kernel. Please remove unused variables.')
