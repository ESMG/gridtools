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

