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
requiredPackages = []
# Process any package lines like:
# numpypi@git+https://github.com/jr3cermak/numpypi.git@dev#egg=numpypi
# Change to:
# pip@git+https://github.com/jr3cermak/numpypi.git@dev#egg=numpypi
# Allows python setup.py develop and python -m pip install -e . to work
for rPkg in required:
    # Ignore package comments
    if rPkg.find('#') == 0:
        continue
    atRef = rPkg.find('@')
    if atRef > -1:
        pkgName = rPkg[0:atRef]
        eggName = 'egg=%s' % (pkgName)
        if rPkg.find(eggName) > -1:
            nPkg = 'pip@%s' % (rPkg[atRef+1:])
            requiredPackages.append(nPkg)
    else:
        requiredPackages.append(rPkg)

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
    install_requires=requiredPackages
)
