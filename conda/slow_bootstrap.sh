# Use this technique to slowly bootstrap
# an environment.
# conda create -y -q -n gridTools python==3.7.10
# conda activate gridTools
conda install -q -y geoviews=1.9.1
conda install -q -y cartopy colorama colorcet
conda install -q -y conda coverage cython
conda install -q -y dask datashader docutils=0.16
conda install -q -y hvplot
conda install -q -y jupyterlab
conda install -q -y matplotlib
conda install -q -y m2r2 netCDF4
conda install -q -y nodejs numba numpy
conda install -q -y owslib pandas panel
conda install -q -y param pip pooch
conda install -q -y pyct pykdtree pyproj
conda install -q -y pyqt pyqt5-sip pytest
conda install -q -y requests scipy sphinx
conda install -q -y sphinx_rtd_theme sphinxcontrib-bibtex xarray
conda install -q -y xesmf xgcm
conda install -q -y anyio coverage json5
conda install -q -y sniffio
conda install -q -y nbclassic
conda install -q -y requests-unixsocket websocket-client
