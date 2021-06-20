#!/bin/env python3

# conda: gridTools

import sys, os, logging
import cartopy
from gridtools.gridutils import GridUtils
from gridtools.datasource import DataSource

import pdb

# Setup a work directory
#wrkDir = '/home/cermak/mom6/configs/zOutput'
wrkDir = '/import/AKWATERS/jrcermakiii/configs/zOutput'
inputDir = os.path.join(wrkDir, "INPUT")

# Initialize a grid object
grd = GridUtils()

# We can turn on extra output from the module
grd.printMsg("Setting print and logging messages to the DEBUG level.")
logFilename = os.path.join(wrkDir, 'LCC_20x30.log')
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
grd.printMsg("Set grid parameters.")
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
    'tileName': 'tile1',
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

# Save the catalog just for demonstration
ds.saveCatalog(os.path.join(wrkDir, 'catalog.json'))
ds.saveCatalog(os.path.join(wrkDir, 'catalog.yaml'))

# Data sources cannot be in chunked mode for use in this routine
bathyFields = grd.computeBathymetricRoughness('ds:GEBCO_2020',
        maxMb=99, superGrid=False, useClipping=False,
        FixByOverlapQHGridShift=True,
        auxVariables=['hStd', 'hMin', 'hMax', 'depth'],
)

# This is needed to really convert the elevation field to depth
# The 'depth' field has to be requested as an auxVariables
grd.applyEvalMap('ds:GEBCO_2020', bathyFields)

# Write ocean_mask.nc and land_mask.nc based on existing field
grd.writeOceanmask(bathyFields, 'depth', 'mask',
        os.path.join(wrkDir, 'ocean_mask_Example7.nc'),
        MASKING_DEPTH=0.0)
grd.writeLandmask(bathyFields, 'depth', 'mask',
        os.path.join(wrkDir, 'land_mask_Example7.nc'),
        MASKING_DEPTH=0.0)

# Apply existing land mask which should not change anything
# The minimum depth will modify a couple points.   We save the
# new field as 'newDepth' to allow comparison with 'depth'.
bathyFields['newDepth'] = grd.applyExistingLandmask(bathyFields, 'depth',
        os.path.join(wrkDir, 'land_mask_Example7.nc'), 'mask',
        MASKING_DEPTH=0.0, MINIMUM_DEPTH=1000.0, MAXIMUM_DEPTH=-99999.0)
bathyFields['newDepth'].attrs['units'] = 'meters'
bathyFields['newDepth'].attrs['standard_name'] = 'topographic depth at Arakawa C h-points'

# Write fields out to a file
# TODO: provide a data source service hook?
bathyFields.to_netcdf(os.path.join(wrkDir, 'ocean_topog_Example7.nc'),
        encoding=grd.removeFillValueAttributes(data=bathyFields))

grd.saveGrid(filename=os.path.join(wrkDir, "LCC_20x30_Example7.nc"))

# Write out FMS related support files
grd.makeSoloMosaic(
    topographyGrid=bathyFields['newDepth'],
    writeLandmask=True,
    writeOceanmask=True,
    inputDirectory=inputDir,
    overwrite=True,
)
grd.saveGrid(filename=os.path.join(inputDir, "ocean_hgrid.nc"))

# Do some plotting!

# Set some plot parameters for the grid and topography

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
    }
)

# Plot original depth grid after running computeBathyRoughness()
(figure, axes) = grd.plotGrid(
    showModelGrid=False,
    plotVariables={
        'depth': {
            'values': bathyFields['depth'],
            'title': 'Original diagnosed bathymetric field'
        }
    },
)
figure.savefig(os.path.join(wrkDir, 'LCC_20x30_OrigBathy.png'), dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape', transparent=False, bbox_inches=None, pad_inches=0.1)

# Plot depth grid after we apply an existing landmask with minimum
# depth set to 1000 meters
(figure, axes) = grd.plotGrid(
    showModelGrid=False,
    plotVariables={
        'depth': {
            'values': bathyFields['newDepth'],
            'title': 'Bathymetric grid with 1000 meter minimum depth'
        }
    },
)
figure.savefig(os.path.join(wrkDir, 'LCC_20x30_MinBathy.png'), dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape', transparent=False, bbox_inches=None, pad_inches=0.1)

# Plot model grid showing land mask points as painted
# grid cells.

# Plot model grid showing ocean mask points as painted
# grid cells.
