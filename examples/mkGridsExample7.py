#!/bin/env python3

# conda: gridTools

# Gridtools library demonstration in
#  * Command line
#  * ipython
#  * jupyter lab console

import sys, os, logging
from gridtools.gridutils import GridUtils
from gridtools.datasource import DataSource

# Initialize a grid object
grd = GridUtils()
grd.printMsg("At this point, we have initialized a GridUtils() object.")
grd.printMsg("")

# We can turn on extra output from the module
grd.printMsg("Set print and logging messages to the DEBUG level.")
logFilename = '/home/cermak/mom6/configs/zOutput/LCC_20x30.log'
grd.setVerboseLevel(logging.DEBUG)
grd.setDebugLevel(0)
grd.setLogLevel(logging.DEBUG)
grd.deleteLogfile(logFilename)
grd.enableLogging(logFilename)

# Make sure we erase any previous grid, grid parameters and plot parameters.
grd.clearGrid()

# Specify the grid parameters
# gridMode should be 2.0 for supergrid
# Normally 30.0; 0.0 for debugging
gtilt = 30.0
grd.printMsg("Initial grid parameters are set:")
grd.setGridParameters({
    'projection': {
        'name': 'LambertConformalConic',
        'lon_0': 230.0,
        'lat_0': 40.0
    },
    'centerX': 230.0,
    'centerY': 40.0,
    'centerUnits': 'degrees',
    'dx': 20.0,
    'dxUnits': 'degrees',
    'dy': 30.0,
    'dyUnits': 'degrees',
    'tilt': gtilt,
    'gridResolution': 1.0,
    'gridMode': 2,
    'gridType': 'MOM6',
    'ensureEvenI': True,
    'ensureEvenJ': True
})
grd.printMsg("")

# This forms a grid in memory using the specified grid parameters
grd.printMsg("Make a grid with the grid parameters.")
grd.makeGrid()
grd.printMsg("")

# External data sources are required
ds = DataSource()

# Define a datasource or load from a catalog.
# ds.load_catalog('filename')
# For variableMap, any referenced variable prefixed with a dash
# is inverted before use.
ds.addDataset({
    'GEBCO_2020': {
            'url' : 'file:///home/cermak/mom6/bathy/gebco/GEBCO_2020.nc',
            'variableMap' : {
                    'lat': 'lat',
                    'lon': 'lon',
                    'depth' : '-elevation'
                }
        }
})

# Tell gridtools about our data sources
grd.useDataSources(ds)

grd.compute_bathymetric_roughness_h2('GEBCO_2020', maxMb=300)

grd.generate_conservative_regrid('GEBCO_2020', sourceVariable='depth', auxField=['land_mask'], nominal_depth=0.0)

grd.saveGrid(filename="/home/cermak/mom6/configs/zOutput/LLC_20x30_Example7.nc")
