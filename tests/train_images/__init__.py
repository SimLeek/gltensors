from pathlib import Path
from PIL import Image
import numpy as np


def jpg_to_stero_npy(img_file: str):
    img = str(Path.joinpath(Path(__file__).parent, img_file))
    img = Image.open(img)
    img = np.asarray(img)
    l = img[:, :img.shape[1] // 2, ...]
    r = img[:, img.shape[1] // 2:, ...]
    return l, r


box_left, box_right = jpg_to_stero_npy("box_test.jpg")
box_left_2, box_right_2 = jpg_to_stero_npy("box_test_2.jpg")
tree_left, tree_right = jpg_to_stero_npy("tree_test.jpg")
waterfall_left, waterfall_right = jpg_to_stero_npy("waterfall_test.jpg")
cactus_left, cactus_right = jpg_to_stero_npy("cactus_test.jpg")

if __name__ == "__main__":
    from displayarray import breakpoint_display

    breakpoint_display(tree_left, tree_right)
