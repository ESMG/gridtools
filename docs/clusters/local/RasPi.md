# Raspberry Pi

These are notes for running grid tools on a Raspberry Pi
platform [Raspberry Pi 4 Model B Rev 1.4].  These notes
are based on running Ubuntu 20.04.2 LTS on a Pi with 8 GB
of RAM.

# nodejs 14.16.0

Installed locally.

# Python venv

```
python3 -m venv venv/base
source ~/venv/base/bin/activate
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools
python -m pip install certifi cython numpy
cd src/gridtools
python -m pip install -e .
```

# conda

Latest version: `Miniconda3-py39_4.9.2-Linux-aarch64.sh`

Conda based packages for Rasperry Pi are not fully supported.  Some
manual curation is required to obtain a stable software stack.

Conda does not support loading of xesmf or xgcm from conda-forge yet.
These packages have not been built for the aarch64 platform.

Do not install any base updates.  This will cause conda to segfault.
```
conda update -n base -c defaults conda
```

Setup the conda environment for gridtools:
```
conda create -c conda-forge -c defaults -n gridTools -q jupyterlab
conda activate gridTools
conda install -c conda-forge -c defaults -q certifi cython numpy geos
cd src/gridtools
python -m pip install -q -e .
```

# Jupyter

The process is pretty simple if the Pi is on the
same local network as your workstation.  If this
is the case, discover the IP address of the Pi.

```
jupyter lab --ip=192.168.131.52 --no-browser
```

Use the url link given with the IP address.

If you are using the Pi as your workstation,
either presented link will work.  The option
"--no-browser" can be dropped to attempt to
automatically start a browser on your Pi
workstation.

# ESMF

The ESMF package does compile on the RasPi platform
using version 8.1.1.

```
wget "https://github.com/esmf-org/esmf/archive/refs/tags/ESMF_8_1_1.tar.gz"
tar xzf ESMF_8_1_1.tar.gz
export ESMF_DIR=/home/cermak/workdir/software/esmf-ESMF_8_1_1
make script_info
make
make check
```

All checks pass for mpiuni.

A python virtual environment (venv) was created for a non-sudo
install of ESMPy and xESMF.

A very minimum start to a python virtual environment:
```
python3 -m venv venv/base
source venv/base/bin/activate
# Once the environment is active,
# python can be used instead of python3
```

# ESMPy

```
cd $ESMF_DIR/src/addon/ESMPy
python setup.py build --ESMFMKFILE=${ESMF_DIR}/lib/libO/Linux.gfortran.32.mpiuni.default/esmf.mk install
```

# xESMF

```
git clone https://github.com/pangeo-data/xESMF.git
cd xESMF
python -m pip install .
```

NOTE: Extensive testing of the installed software has yet to be done.
