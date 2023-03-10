import os, sys
from setuptools import find_packages, setup
import gridtools
import pdb


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


# Use a tuned requirements.txt depending on
# which version is being used.
requirements_file = 'requirements.txt'

# Versions we will tune for will depend on support
# for esmf, esmpy and xesmf
# Support the last 3 minor versions: 3.10, 3.9, 3.8
# Default to 3.8
if sys.version_info.major == 3:
    if sys.version_info.minor >= 8 and sys.version_info.minor <= 10:
        requirements_file = f'requirements_{sys.version_info.major}_{sys.version_info.minor}.txt'

with open(requirements_file) as f:
    requiredPackages = f.read().splitlines()

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
    python_requires=">=3.8",
    install_requires=requiredPackages
)
