import numpy as np

grid = []

for i in range(65):
    grid.append([i - 32, -32.0, 0.0, i - 32, 32.0, 0.0])
    grid.append([-32.0, i - 32, 0.0, 32.0, i - 32, 0.0])

grid = np.array(grid)

def setupForTesting(persp_win):
    persp_win.setVBO(grid.astype('f4').tobytes())
    persp_win.setVAO()