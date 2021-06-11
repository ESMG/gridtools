#!/bin/env python3

# conda: gridTools

import sys, os, logging
from gridtools.gridutils import GridUtils
from gridtools.datasource import DataSource
import pdb

# This example exercises the routine written by
# James Simkins to generate a ocean topography
# and ocean mask with a ocean fraction.

# We utilize the 20x30 example grid along the
# California coast.

# Setup a work directory
#wrkDir = '/home/cermak/mom6/configs/zOutput'
wrkDir = '/import/AKWATERS/jrcermakiii/configs/zOutput'

# Initialize a grid object
grd = GridUtils()

# We can turn on extra output from the module
grd.printMsg("Setting print and logging messages to the DEBUG level.")
logFilename = os.path.join(wrkDir, 'LCC_20x30_Example8.log')
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
        'lat_0': 40.0,
        'ellps': 'WGS84'
    },
    'centerX': 230.0,
    'centerY': 40.0,
    'centerUnits': 'degrees',
    'dx': 20.0,
    'dxUnits': 'degrees',
    'dy': 30.0,
    'dyUnits': 'degrees',
    'tilt': gtilt,
    'gridResolutionX': 1.0,
    'gridResolutionY': 1.0,
    'gridResolution': 1.0,
    'gridResolutionXUnits': 'degrees',
    'gridResolutionYUnits': 'degrees',
    'gridResolutionUnits': 'degrees',
    'gridMode': 2,
    'gridType': 'MOM6',
    'ensureEvenI': True,
    'ensureEvenJ': True
})
grd.printMsg("")

# This forms a grid in memory using the specified grid parameters
grd.makeGrid()
grd.printMsg("")

# External data sources are required
# This creates an empty data source catalog
ds = DataSource()

# Connect the catalog to the grid object
grd.useDataSource(ds)

# For variableMap, matching variable values will be renamed to the
# variable key.  For evalMap, variables in the expression need
# to be in brackets.  If the key is new, a new field will be
# created with the given expression.
ds.addDataSource({
    '/GEBCO_2020': {
            'url' : 'file:///import/AKWATERS/jrcermakiii/bathy/gebco/GEBCO_2020.nc',
            'variableMap' : {
                    'lat': 'lat',
                    'lon': 'lon',
                    'depth' : 'elevation'
                },
            'evalMap': {
                    'depth' : '-[depth]'
                }
        }
})

# Exercise topoutils.TopoUtils.regridTopo() function

resultFields = grd.regridTopo('ds:///GEBCO_2020', topoVarName='depth')

# Write fields out to a file
# TODO: provide a data source service hook?
resultFields.to_netcdf(os.path.join(wrkDir, 'ocean_topog_Example8.nc'),
        encoding=grd.removeFillValueAttributes(data=resultFields))

grd.saveGrid(filename=os.path.join(wrkDir, "LCC_20x30_Example8.nc"))

# Do some plotting!
