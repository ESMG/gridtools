#!/usr/bin/env python

# conda: gridTools

import sys, os, logging
import cartopy
import numpy as np
import xarray as xr
from gridtools.gridutils import GridUtils
from gridtools.datasource import DataSource

# Test grid generation with small grid mercator which
# causes calculation issues grid metric angle_dx

# Setup a work directory
wrkDir = '/import/AKWATERS/jrcermakiii/configs/zOutput'
inputDir = os.path.join(wrkDir, "INPUT")

# Initialize a grid object
grd = GridUtils()

# We can turn on extra output from the module
grd.printMsg("Setting print and logging messages to the DEBUG level.")
logFilename = os.path.join(wrkDir, 'Mercator_angleDX_20x20.log')
grd.setVerboseLevel(logging.DEBUG)
grd.setDebugLevel(0)
grd.setLogLevel(logging.DEBUG)
grd.deleteLogfile(logFilename)
grd.enableLogging(logFilename)

# Make sure we erase any previous grid, grid parameters and plot parameters.
grd.clearGrid()

# Specify the grid parameters
# gridMode should be 2.0 for supergrid
gtilt = 0.0
grd.printMsg("Set grid parameters.")
grd.setGridParameters({
    'projection': {
        'name': 'Mercator',
        'lon_0': 0.0,
        'lat_0': 0.0,
        'lat_ts': 0.0,
        'ellps': 'WGS84'
    },
    'centerX': 0.0,
    'centerY': 0.0,
    'centerUnits': 'degress',
    'dx': 2.0,
    'dxUnits': 'degrees',
    'dy': 2.0,
    'dyUnits': 'degrees',
    'tilt': gtilt,
    'gridResolutionX': 0.1,
    'gridResolutionY': 0.1,
    'gridResolution': 0.1,
    'gridResolutionXUnits': 'degrees',
    'gridResolutionYUnits': 'degrees',
    'gridResolutionUnits': 'degrees',
    'gridMode': 2,
    'gridType': 'MOM6',
    'ensureEvenI': True,
    'ensureEvenJ': True,
    'tileName': 'tile1',
    'angleCalcMethod': 1
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
            'url' : 'file:///import/AKWATERS/jrcermakiii/bathy/gebco/2020/GEBCO_2020.nc',
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
ds.saveCatalog(os.path.join(wrkDir, 'catalog.yml'))

# Bathymetry grid variables filename
bathyGridFilename = os.path.join(wrkDir, 'ocean_topog.nc')

# The bathymetric roughness can take a while to run.
# If the file exists, we use that one instead of regenerating
# it.  If you want to test the routine again, erase the output
# file.
if os.path.isfile(bathyGridFilename):
    grd.printMsg("Using existing bathymetry file: %s" % (bathyGridFilename))
    bathyGrids = xr.open_dataset(bathyGridFilename)
else:
    # Data sources cannot be in chunked mode for use in this routine

    # NOTE: This uses the original workaround for diagnosing the
    # bathymetric roughness.  Please see mkGridsExample07b.ipynb
    # for the recommended method for computing bathymetric
    # roughness.  Please also read the manual for more details.
    bathyGrids = grd.computeBathymetricRoughness('ds:GEBCO_2020',
            maxMb=99, superGrid=False, useClipping=False,
            useQHGridShift=True, useOverlap=True,
            auxVariables=['hStd', 'hMin', 'hMax', 'depth'],
    )

    # This is needed to really convert the elevation field to depth
    # The 'depth' field has to be requested as an auxVariables
    grd.applyEvalMap('ds:GEBCO_2020', bathyGrids)

    # Write ocean_mask.nc and land_mask.nc based on existing field
    grd.writeOceanmask(bathyGrids, 'depth', 'mask',
            os.path.join(wrkDir, 'ocean_mask_write.nc'),
            MASKING_DEPTH=0.0)
    grd.writeLandmask(bathyGrids, 'depth', 'mask',
            os.path.join(wrkDir, 'land_mask_write.nc'),
            MASKING_DEPTH=0.0)

    # Apply existing land mask which should not change anything
    # The minimum depth will modify a couple points.   We save the
    # new field as 'newDepth' to allow comparison with 'depth'.
    bathyGrids['newDepth'] = grd.applyExistingLandmask(bathyGrids, 'depth',
            os.path.join(wrkDir, 'land_mask_write.nc'), 'mask',
            MASKING_DEPTH=0.0, MINIMUM_DEPTH=1000.0, MAXIMUM_DEPTH=-99999.0)
    bathyGrids['newDepth'].attrs['units'] = 'meters'
    bathyGrids['newDepth'].attrs['standard_name'] = 'topographic depth at Arakawa C h-points'

    # Write fields out to a file
    # TODO: provide a data source service hook?
    bathyGrids.to_netcdf(os.path.join(wrkDir, 'ocean_topog_write2.nc'),
            encoding=grd.removeFillValueAttributes(data=bathyGrids))

grd.saveGrid(filename=os.path.join(wrkDir, "Mercator_angleDX_20x20.nc"))

# Write out FMS related support files
grd.makeSoloMosaic(
    topographyGrid=bathyGrids['newDepth'],
    writeLandmask=True,
    writeOceanmask=True,
    inputDirectory=inputDir,
    overwrite=True,
)

# The FMS coupler (v1) does not like the 'tile' variable
grd.saveGrid(filename=os.path.join(inputDir, "ocean_hgrid.nc"), noTile=True)

# Do some plotting!

# Set some plot parameters for the grid and topography
grd.printMsg("---")
grd.printMsg("Plotting original diagnosed bathymetric field.")
grd.printMsg("---")
grd.setPlotParameters(
    {
        'figsize': (8,8),
        'projection': {
            'name': 'NearsidePerspective',
            'lat_0': 0.0,
            'lon_0': 0.0
        },
        'extent': [-90.0, 90.0, -20.0, 20.0],
        'iLinewidth': 1.0,
        'jLinewidth': 1.0,
        'showGridCells': True,
        'title': "Nearside Perspective: 20x20 with %.1f degree tilt" % (gtilt),
        'iColor': 'k',
        'jColor': 'k',
        'transform': cartopy.crs.PlateCarree(),
        'satelliteHeight': 35785831.0,
    }
)

# Plot original depth grid after running computeBathyRoughness()
(figure, axes) = grd.plotGrid(
    showModelGrid=False,
    plotVariables={
        'depth': {
            'values': bathyGrids['depth'],
            'title': 'Original diagnosed bathymetric field',
            'cbar_kwargs': {
                'orientation': 'horizontal',
            }
        }
    },
)
figure.savefig(os.path.join(wrkDir, '20x20_OrigBathy.png'), dpi=None,
        facecolor='w', edgecolor='w', orientation='landscape',
        transparent=False, bbox_inches=None, pad_inches=0.1)

# Plot depth grid after we apply an existing landmask with minimum
# depth set to 1000 meters
grd.printMsg("---")
grd.printMsg("Plotting original diagnosed bathymetric field with")
grd.printMsg("MINIMUM_DEPTH=1000.0.")
grd.printMsg("---")
(figure, axes) = grd.plotGrid(
    showModelGrid=False,
    plotVariables={
        'depth': {
            'values': bathyGrids['newDepth'],
            'title': 'Bathymetric grid with 1000 meter minimum depth',
            'cbar_kwargs': {
                'orientation': 'horizontal',
            }
        }
    },
)
figure.savefig(os.path.join(wrkDir, '20x20_MinBathy.png'), dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape', transparent=False, bbox_inches=None, pad_inches=0.1)
