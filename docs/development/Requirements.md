# Software Requirements

These are the high level packages required for
the gridtools library.  It is not an exhasutive
list.  There may be smaller dependencies that need
to be installed.

For grid generation, the required packages are:
 * cartopy
 * matplotlib
 * numba
 * numpy
 * pyproj
 * pandas
 * scipy
 * xarray

For the grid generation application:
 * bokeh
 * datashader
 * jupyterlab
 * panel

For the jupyter grid editor application:
 * geoviews >= 1.9

For regridding operations:
 * xesmf
 * xgcm

For parallel and additional memory management options:
 * dask

Development tools:
 * coverage
 * docutils==0.16
 * pip
 * pytest
 * sphinx
 * sphinx-rtd-theme (called `sphinx_rtd_theme` for conda)

To generate PDF version of the documentation, a good
portion of the latex software will need to be installed.

If you are using the **conda** environment, there is
a python module as well called **conda**.

Package/Environment management:
 * conda
