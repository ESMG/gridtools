# Python 3.8

This provides information on support of the gridtools
library for python version 3.8.

## gridtools


### Prebuilt package list
```
$ conda create --name gridtools_py3_8 --file conda/gridtools_py3_8_linux_64.txt
$ conda activate gridtools_py3_8
$ cd src/gridtools
$ python -m pip install .
```

### Manual bootstrapping

```
$ conda create -n gridtools_py3_8 python=3.8 jupyterlab nodejs
$ conda activate gridtools_py3_8
$ conda install cartopy
$ conda install xarray
$ conda install panel
$ conda install hvplot
$ conda install geoviews
```

After bootstrapping:
```
$ conda list --explicit > gridtools_py3_8_linux_64.txt
```

## esmf, esmpy, xesmf

If regridding is needed, esmf and friends need to be installed.
Be sure to use an MPI version of esmf.

```
$ conda install esmf=8.4.1=mpi_mpich_h7b33e6e_100
```

This will have the effect of reinstalling basic libraries
for hdf and netcdf to support MPI operations for esmf.

```
  hdf5                            1.12.2-nompi_h4df4325_101 --> 1.12.2-mpi_mpich_h5d83325_1
  libnetcdf                        4.9.1-nompi_hd2e9713_102 --> 4.9.1-mpi_mpich_h5eb6f38_2
```
