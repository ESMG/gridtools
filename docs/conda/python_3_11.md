# Python 3.11

These are notes for testing the 3.11 version of python and conda.

NOTE: There is a single package missing to completely support
python 3.11.

## Manual Installation

```
$ conda create -n gridTools python=3.11 panel=0.14.3 geoviews=1.5.0
# Do not install xesmf from conda, install from github repository
# MPI versions of esmf and esmpy must be used
$ conda install esmf=8.4.0=mpi_mpich_h7b33e6e_105 esmpy=8.4.0=mpi_mpich_py311hf216de5_102

$ conda install dask
$ conda install hvplot
$ conda install sphinx
$ conda install nodejs
$ conda install jupyterlab
$ conda install netcdf4
$ conda install cf_xarray=0.8.0 sparse=0.3.1 xarray=2023.2.0
# Latest numba does not support python 3.11
$ conda install numba
```

### Install xesmf

```
$ git clone https://github.com/pangeo-data/xESMF.git
$ cd xESMF
$ python -m pip install .
```

### Install gridtools

# In ~src/gridtools, move the requirments.txt file out of the
# way and replace with an empty file.

```
$ python -m pip install -e .
```

# PENDING

# Verify documentation still builds

## Documentation packages

```
$ conda install sphinxcontrib-bibtex
$ conda install sphinx_rtd_theme

# Side loaded packages
$ python pip -m install 
```
