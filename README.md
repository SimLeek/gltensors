# MineSim

![example image](https://i.imgur.com/AjOOkhd.png)

## Setup

Please install [Anaconda 3.6](https://docs.anaconda.com/anaconda/install/linux).
I've found the libraries in Ubunutu's packages are often outdated,
and vtk is still hard to get working in Windows or other operating systems.

Then, in a terminal, do:
 * `source activate root` (or another environment)
 * Ubuntu: `sudo apt install libgl1-mesa-dev mesa-common-dev`
 * `pip install ModernGl opensimplex PyQt5`

For testing:
 * `source activate root` (or another environment)
 * `conda install -c conda-forge vtk python=3.6`