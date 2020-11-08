from setuptools import setup, find_packages
from virtualreality import __version__

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="gltensors",
    version=__version__,
    author="SimLeek <simulator.leek@gmail.com>",
    author_email="",
    description="OpenGL tensors (pytorch mixin WIP)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/okawo80085/hobo_vr",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: C++",
        "Programming Language :: Python :: 3.7",
        "Topic :: Multimedia :: Graphics :: Viewers",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
    ],
    install_requires=[
        "ModernGL",
        "pytest",
        "vtk",
        "opensimplex",
        "PyQt5"
    ],
    extras_require={
        "camera": ["displayarray", "opencv-python"]},
    python_requires=">=3.7",
)
