import os
from setuptools import find_packages, setup
import gridtools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements-base.txt') as f:
    requiredBase = f.read().splitlines()

with open('requirements-post.txt') as f:
    requiredPost = f.read().splitlines()

required = requiredBase + requiredPost

setup(
    name="gridtools", # Replace with your own username
    version=gridtools.__version__,
    author="James Simkins",
    author_email="james.simkins@rutgers.edu",
    maintainer="Rob Cermak",
    maintainer_email="rob.cermak@gmail.com",
    description="A collection of grid generation tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ESMG/gridtools",
    project_urls={
        "Bug Tracker": "https://github.com/ESMG/gridtools/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
    ],
    packages=find_packages(exclude=['conda','docs','examples']),
    python_requires=">=3.6",
    install_requires=required
)
