#!/bin/env python3

# conda: gridTools

# This demonstrates creation of a grid using
# gridtools in a Mercator projection.  This
# grid should be comparable to a similar
# grid created by FRE-NCtools.

# NOTE: This script takes a VERY long time
# to run.

import sys, os, logging, cartopy
import xarray as xr
from gridtools.gridutils import GridUtils
from gridtools.datasource import DataSource

# Set a place to read/write files
wrkDir = '/import/AKWATERS/jrcermakiii/configs/zOutput'
inputDir = os.path.join(wrkDir, 'INPUT')

# Initialize a grid object
grd = GridUtils()
grd.printMsg("At this point, we have initialized a GridUtils() object.")
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

# We can turn on extra output from the module
grd.printMsg("Set print and logging messages to the DEBUG level.")
logFilename = os.path.join(wrkDir, 'MERC_20x30_Example3.log')
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
grd.printMsg("Initial grid parameters are set:")
grd.setGridParameters({
    'projection': {
        'name': 'Mercator',
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
    'gridResolution': 1.0,
    'gridResolutionUnits': 'degrees',
    'gridMode': 2.0,
    'gridType': 'MOM6',
    'ensureEvenI': True,
    'ensureEvenJ': True,
    'tileName': 'tile1',
    'angleCalcMethod': 0
})
grd.showGridParameters()
grd.printMsg("")

# To set or update dictionary items in 'projection', you can use the dictionary format above with a direct assigment
# or use the subKey parameter as in below.
#grd.setGridParameters({
#    'name': 'Mercator',
#    'lon_0': 230.0,
#    'lat_0': 40.0
#}, subKey='projection')

# This forms a grid in memory using the specified grid parameters
grd.printMsg("Make a grid with the grid parameters.")
grd.makeGrid()

# Save the new grid to a netCDF file
grd.printMsg("Attempt to save the grid to a netCDF file.")
grd.saveGrid(filename=os.path.join(wrkDir, "MERC_20x30_Example3.nc"))

# This prints out all the current grid parameters
grd.printMsg("""
This shows the current grid parameters.

""")
grd.showGridParameters()
grd.printMsg("")

# You can show the data summary from xarray for the grid
grd.printMsg("This shows the xarray structure for the recently created grid:")
grd.printMsg("%s" % (grd.grid))
grd.printMsg("")

# Define plot parameters so we can see what the grid looks like
grd.printMsg("Setup plotting parameters for showing the grid on a map:")
grd.setPlotParameters(
    {
        'figsize': (8,8),
        'projection': {
            'name': 'Mercator',
            'lat_0': 40.0,
            'lon_0': 230.0
        },
        'extent': [-160.0 ,-100.0, 20.0, 60.0],
        'iLinewidth': 1.0,
        'jLinewidth': 1.0,
        'showGridCells': True,
        'title': "Mercator: 1.0 deg x 1.0 deg",
        'satelliteHeight': 35785831.0,
        'transform': cartopy.crs.PlateCarree(),
        'iColor': 'k',
        'jColor': 'k'
    }
)
grd.showPlotParameters()
grd.printMsg("")

# Projection may be specified separately
grd.setPlotParameters(
    {
        'name': 'Mercator',
        'lat_0': 40.0,
        'lon_0': 230.0
    }, subKey='projection'
)

# When we call plotGrid() we have two python objects returned
# Figure object - you have control whether to show the
#   figure or save the contents to an output file
# Axes object - you can further fine tune plot parameters,
#   titles, axis, etc prior to the final plotting of the figure.
#   Some items may be configured via the figure object.
grd.printMsg('''
Place a call to actually plot the grid using plotGrid().  This function returns
a figure and axes object that can be further modified before displaying or saving
the plot.
''')
(figure, axes) = grd.plotGrid()

# You can save the figure using the savefig() method on the
# figure object.  Many formats are possible.
grd.printMsg("Save the figure in two different formats: jpg and pdf.")
figure.savefig(os.path.join(wrkDir, 'MERC_20x30_Example3.jpg'),
        dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', transparent=False, bbox_inches=None,
        pad_inches=0.1)

figure.savefig(os.path.join(wrkDir, 'MERC_20x30_Example3.pdf'),
        dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', transparent=False, bbox_inches=None,
        pad_inches=0.1)

# Create ocean_topog method 1: computeBathymetricRoughness()

# Bathymetry grid variables filename
bathyGridFilename = os.path.join(wrkDir, 'ocean_topog_Example3_computeBathymetricRoughness.nc')

# The bathymetric roughness can take a while to run.
# If the file exists, we use that one instead of regenerating
# it.  If you want to test the routine again, erase the output
# file.
if os.path.isfile(bathyGridFilename):
    bathyGrids = xr.open_dataset(bathyGridFilename)
else:
    # This routine cannot utilize data sources that are in chunked mode
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
            os.path.join(wrkDir, 'ocean_mask_Example3.nc'),
            MASKING_DEPTH=0.0)
    grd.writeLandmask(bathyGrids, 'depth', 'mask',
            os.path.join(wrkDir, 'land_mask_Example3.nc'),
            MASKING_DEPTH=0.0)

    # Write fields out to a file
    # TODO: provide a data source service hook?
    bathyGrids.to_netcdf(bathyGridFilename,
            encoding=grd.removeFillValueAttributes(data=bathyGrids))

# Clip any negative depths to zero
bathyGrids['depth'] = xr.where(bathyGrids['depth'] < 0.0, 0.0, bathyGrids['depth'])

# Plot original depth grid after running computeBathyRoughness()
(figure, axes) = grd.plotGrid(
    showModelGrid=False,
    plotVariables={
        'depth': {
            'values': bathyGrids['depth'],
            'title': 'GEBCO 2020: computeBathyRoughness()',
            'cbar_kwargs': {
                'orientation': 'horizontal',
            }
        }
    },
)

figure.savefig(os.path.join(wrkDir, 'MERC_20x30_Bathy_Example3_computeBathyRoughness.png'),
        dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape', transparent=False, bbox_inches=None, pad_inches=0.1)

# Create ocean_topog method 2: regridTopo()

resultGrids = grd.regridTopo('ds:GEBCO_2020', topoVarName='depth', periodic=False)

resultGrids.to_netcdf(os.path.join(wrkDir, 'ocean_topog_Example3_regridTopo.nc'),
        encoding=grd.removeFillValueAttributes(data=resultGrids))

# Plot the new bathy grid
(figure, axes) = grd.plotGrid(
    showModelGrid=False,
    plotVariables={
        'depth': {
            'values': resultGrids['depth'],
            'title': 'GEBCO 2020: GridUtils.regridTopo()',
            'cbar_kwargs': {
                'orientation': 'horizontal',
            }
        }
    },
)

figure.savefig(os.path.join(wrkDir, 'MERC_20x30_Bathy_Example3_regridTopo.png'),
        dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape', transparent=False, bbox_inches=None, pad_inches=0.1)

# The original routine leaves an artifact around the grid edge.  This can
# be fixed by extending the grid by one grid point, recomputing and
# then clipping the extended result.

extGrd = grd.extendGrid(2, 2, 2, 2)

# Put the extended grid into a gridtools grid.  Attach it to
# the same data source as above.
grd2 = GridUtils()
grd2.useDataSource(ds)
grd2.readGrid(local=extGrd)

resultGridsExt = grd2.regridTopo('ds:GEBCO_2020', topoVarName='depth', periodic=False)

# Subset the result grid back to the original grid
resultGrids2 = xr.Dataset()
resultGrids2['depth'] = resultGridsExt['depth'][1:-1,1:-1]
resultGrids2['ocean_mask'] = resultGridsExt['ocean_mask'][1:-1,1:-1]

resultGrids2.to_netcdf(os.path.join(wrkDir, 'ocean_topog_Example3_regridTopo_ext.nc'),
        encoding=grd2.removeFillValueAttributes(data=resultGrids2))

# Plot the new bathy grid
(figure, axes) = grd.plotGrid(
    showModelGrid=False,
    plotVariables={
        'depth': {
            'values': resultGrids2['depth'],
            'title': 'GEBCO 2020: GridUtils.regridTopo() with an extended grid',
            'cbar_kwargs': {
                'orientation': 'horizontal',
            }
        }
    },
)

figure.savefig(os.path.join(wrkDir, 'MERC_20x30_Bathy_Example3_regridTopo_ext.png'),
        dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape', transparent=False, bbox_inches=None, pad_inches=0.1)
