# pyroms

[pyroms](https://github.com/ESMG/pyroms)

This is a legacy software library for specific use with ROMS grids.  

# Notes

NOTE: This is a very limited environment with netcdf4 and matplotlib's basemap
to review former functionality.  This should be migrated ASAP to utilize modern
libraries.

```
# The current path is your SRC directory
$ git clone https://github.com/ESMG/pyroms.git
# The cloned directory is ${SRC}/pyroms
```

Install the pyroms conda environment. This installs the appropriate fortran
compiler for netcdf.

If you need scrip.so:
```
$ cd ${SRC}/pyroms/pyroms/external/scrip/source
# edit makefile
# change PREFIX = /usr/local
# to     PREFIX ?= /usr/local
$ export PREFIX=$CONDA_PREFIX
$ make DEVELOP=1
$ cp scrip.cpython-38-x86_64-linux-gnu.so ${SRC}/pyroms/pyroms/pyroms/
```

Using pyroms:
```
# define the location of gridid.txt
# edit gridid.txt to point to Arctic6 nc file
$ export PYROMS_GRIDID_FILE=/home/cermak/gridtools/gridTools/configs/Arctic6/roms/gridid.txt
```

For now the only known working way to run editmask.py is via:
```
$ ipython --pylab
```

Cut and paste line by line into the interactive command above.  The last line
in editmask.py saves any edits made to the grid.

However, this should also work in jupyterlab via ipympl which is untested at
the moment.
