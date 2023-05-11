import numpy as np

left_line = np.arange(100)
right_line = np.arange(35, 135)

'''
left_line = np.zeros([100])
left_line[35]=1
right_line = np.zeros([100])
right_line[10]=1
'''
left_img = left_line[None, None, None, ...]
right_img = right_line[None, None, None, ...]
