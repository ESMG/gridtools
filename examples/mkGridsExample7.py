#!/bin/env python3

# conda: gridTools

# Gridtools library demonstration in
#  * Command line
#  * ipython
#  * jupyter lab console

import sys, os, logging
from gridtools.gridutils import GridUtils
from gridtools.datasource import DataSource
import pdb

# Initialize a grid object
grd = GridUtils()

# We can turn on extra output from the module
grd.printMsg("Setting print and logging messages to the DEBUG level.")
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
    'GEBCO_2020': {
            'url' : 'file:///home/cermak/mom6/bathy/gebco/GEBCO_2020.nc',
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

# Save data source catalog
#ds.saveCatalog('/home/cermak/mom6/configs/zOutput/catalog.json')
#ds.saveCatalog('/home/cermak/mom6/configs/zOutput/catalog.yaml')

# Clear the catalog
#ds.clearCatalog()

# Re-read one of the catalog files above
#ds.loadCatalog('/home/cermak/mom6/configs/zOutput/catalog.yaml')
#ds.loadCatalog('/home/cermak/mom6/configs/zOutput/catalog.json')

# Data sources cannot be in chunked mode for use in this routine
bathyFields = grd.computeBathymetricRoughness('GEBCO_2020',
        maxMb=99, superGrid=False, useClipping=False,
        FixByOverlapQHGridShift=True, auxFields=['hStd', 'hMin', 'hMax', 'depth'])

# This is needed to really convert the elevation field to depth
# The 'depth' field has to be requested as an auxFields
grd.applyEvalMap('GEBCO_2020', bathyFields)

#bathyFields = grd.openDataset('FILE:/home/cermak/mom6/configs/zOutput/ocean_topog_Example7.nc')

# Write ocean_mask.nc and land_mask.nc based on existing field
grd.writeOceanMask(bathyFields, 'depth', 'ocean_mask',
        '/home/cermak/mom6/configs/zOutput/ocean_mask_Example7.nc',
        MASKING_DEPTH=0.0)
grd.writeLandMask(bathyFields, 'depth', 'land_mask',
        '/home/cermak/mom6/configs/zOutput/land_mask_Example7.nc',
        MASKING_DEPTH=0.0)

# Apply existing land mask which should not change anything
# The minimum depth will modify a couple points.   We save the
# new field as 'newDepth' to allow comparison with 'depth'.
bathyFields['newDepth'] = grd.applyExistingLandMask(bathyFields, 'depth',
        '/home/cermak/mom6/configs/zOutput/land_mask_Example7.nc', 'land_mask',
        MASKING_DEPTH=0.0, MINIMUM_DEPTH=1000.0, MAXIMUM_DEPTH=-99999.0)

#grd.updateExchangeGrids(bathFields, 'depth')

# Write fields out to a file
# TODO: provide a data source service hook?
bathyFields.to_netcdf('/home/cermak/mom6/configs/zOutput/ocean_topog_Example7.nc',
        encoding=grd.removeFillValueAttributes(data=bathyFields))

grd.saveGrid(filename="/home/cermak/mom6/configs/zOutput/LCC_20x30_Example7.nc")

# Do some plotting!
