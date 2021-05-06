#!/bin/env python3

# conda: xesmfTools

# Grid toolset demonstration in
#  * Command line script form
#  * ipython

import sys, os, logging

#if (os.environ.get('LIBROOT')):
#    sys.path.append(os.environ.get('LIBROOT'))
sys.path.append('lib')

#from sysinfo import SysInfo
#info = SysInfo()
#info.show(vList=['platform','python','esmf','esmpy','xgcm','xesmf',
#                 'netcdf4','numpy','xarray',
#                 'cartopy','matplotlib',
#                 'jupyter_core','jupyterlab','notebook',
#                 'dask'])

from gridutils import GridUtils

# Initialize a grid object
grd = GridUtils()
grd.printMsg("At this point, we have initialized a GridUtils() object.")
grd.printMsg("")

# We can turn on extra output from the module
grd.printMsg("Set print and logging messages to the DEBUG level.")
logFilename = 'configs/test/LCC_20x30.log'
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
grd.showGridParameters()
grd.printMsg("")

# To set or update dictionary items in 'projection', you can use the dictionary format above with a direct assigment
# or use the subKey parameter as in below.
#grd.setGridParameters({
#    'name': 'LambertConformalConic',
#    'lon_0': 230.0,
#    'lat_0': 40.0
#}, subKey='projection')

# This forms a grid in memory using the specified grid parameters
grd.printMsg("Make a grid with the grid parameters.")
grd.makeGrid()

# Save the new grid to a netCDF file
grd.printMsg("Attempt to save the grid to a netCDF file.")
grd.saveGrid(filename="configs/test/LCC_20x30_script.nc")

# This prints out all the current grid parameters
# Note: for Lambert Conformal Conic grids, two additional projection parameters are computed.
#       First and second parallel for the grid (lat_1 and lat_2)
grd.printMsg("""
This shows the current grid parameters.  Note that for Lambert Conformal Grids, lat_1 and
lat_2 have been computed and added to the grid parameters.

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
        'jColor': 'k'
    }
)
grd.showPlotParameters()
grd.printMsg("")

# Projection may be specified separately
grd.setPlotParameters(
    {
        'name': 'NearsidePerspective',
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
figure.savefig('configs/test/LCC_20x30_script.jpg', dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', transparent=False, bbox_inches=None, pad_inches=0.1)

figure.savefig('configs/test/LCC_20x30_script.pdf', dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', transparent=False, bbox_inches=None, pad_inches=0.1)

