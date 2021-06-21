#!/bin/env python3

# conda: gridTools

import sys, os, logging
import cartopy
from gridtools.gridutils import GridUtils
from gridtools.datasource import DataSource

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
grd.printMsg("Set initial grid parameters.")
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
    'ensureEvenJ': True,
    'tileName': 'tile1'
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
            'url' : 'file:/import/AKWATERS/jrcermakiii/bathy/gebco/GEBCO_2020.nc',
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
resultGrids = grd.regridTopo('ds:GEBCO_2020', topoVarName='depth', periodic=False)

# Save the model grid
grd.saveGrid(filename=os.path.join(wrkDir, "LCC_20x30_Example8.nc"))

# Write fields out to a file
# TODO: provide a data source service hook?
resultGrids.to_netcdf(os.path.join(wrkDir, 'ocean_topog_Example8.nc'),
        encoding=grd.removeFillValueAttributes(data=resultGrids))

# Do some plotting!

# Set plot parameters for the grid and topography

grd.setPlotParameters(
    {
        'figsize': (8,8),
        'projection': {
            'name': 'NearsidePerspective',
            'lat_0': 40.0,
            'lon_0': 230.0
        },
        'extent': [-160.0 ,-100.0, 20.0, 60.0],
        'iLinewidth': 1.0,
        'jLinewidth': 1.0,
        'showGridCells': True,
        'title': "Nearside Perspective: 20x30 with %.1f degree tilt" % (gtilt),
        'iColor': 'k',
        'jColor': 'k',
        'transform': cartopy.crs.PlateCarree(),
        'satellite_height': 35785831.0,
    }
)

# Plot the new bathy grid
(figure, axes) = grd.plotGrid(
    showModelGrid=False,
    plotVariables={
        'depth': {
            'values': resultGrids['depth'],
            'title': 'GEBCO 2020 applied to GridUtils.regridTopo()',
            'cbar_kwargs': {
                'orientation': 'horizontal',
            }
        }
    },
)

figure.savefig(os.path.join(wrkDir, 'LCC_20x30_Bathy_Example8.png'), dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape', transparent=False, bbox_inches=None, pad_inches=0.1)

