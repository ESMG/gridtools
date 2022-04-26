#!/usr/bin/env python

# mini IBCAO
# Creates a grid of 20x20 with a
# supergrid of 41x41

import os, sys, cartopy
from gridtools.gridutils import GridUtils

# Set a place to read/write files
wrkDir = '/import/AKWATERS/jrcermakiii/configs/zOutput'
inputDir = os.path.join(wrkDir, 'INPUT')

grd = GridUtils()
grd.clearGrid()

# Define IBCAO grid for gridtools library
grd.setGridParameters({
    'projection': {
        'name': "Stereographic",
        'ellps': 'WGS84',
        'lon_0': 0.0,
        'lat_0': 90.0,
        'lat_ts': 75.0,
    },
    'centerX': 0.0,
    'centerY': 90.0,
    'cneterUnits': 'degrees',
    'dx': 5805000.0,
    'dy': 5805000.0,
    'dxUnits': 'meters',
    'dyUnits': 'meters',
    'gridResolution': 290250.0,
    'gridResolutionUnits': 'meters',
    'tilt': 0.0,
    'gridMode': 2,
    'gridType': 'MOM6',
    'ensureEvenI': True,
    'ensureEvenJ': True,
    'angleCalcMethod': 0
})

grd.makeGrid()

# Save the new grid to a netCDF file
grd.printMsg("Attempt to save the grid to a netCDF file.")
grd.saveGrid(filename=os.path.join(wrkDir, "STE_miniIBCAO_bad_angledx_Example6.nc"))

grd.setPlotParameters(
    {
        'figsize': (8,8),
        'projection': {
            'name': 'Stereographic',
            'lon_0': 0.0,
            'lat_0': 90.0
        },
        'extent': [-180, 180, 60, 90],
        'iLinewidth': 1.0,
        'jLinewidth': 1.0,
        'showGrid': True,
        'showGridCells': False,
        'title': 'Stereographic: mini IBCAO',
        'iColor': 'y',
        'jColor': 'k',
        'transform': cartopy.crs.PlateCarree()
    }
)

(figure, axes) = grd.plotGrid()
figure.savefig(os.path.join(wrkDir, 'IBCAO_Example6.jpg'))

print(grd.grid)

# This demonstrates that using angleCalcMethod=0 for this grid
# is incorrect.

(figure, axes) = grd.plotGrid(
    showModelGrid=False,
    plotVariables={
        'angledx': {
            'values': grd.grid['angle_dx'],
            'title': 'Stereographic: mini IBCAO: angle_dx(0)',
            'cbar_kwargs': {
                'orientation': 'horizontal',
            }
        }
    },
)

figure.savefig(os.path.join(wrkDir, 'IBCAO_angleDX0_Example6.png'), dpi=None,
        facecolor='w', edgecolor='w',
        orientation='landscape', transparent=False, bbox_inches=None, pad_inches=0.1)

# Retry with angleCalcMethod=1

grd = GridUtils()
grd.clearGrid()

# Define IBCAO grid for gridtools library
grd.setGridParameters({
    'projection': {
        'name': "Stereographic",
        'ellps': 'WGS84',
        'lon_0': 0.0,
        'lat_0': 90.0,
        'lat_ts': 75.0,
    },
    'centerX': 0.0,
    'centerY': 90.0,
    'cneterUnits': 'degrees',
    'dx': 5805000.0,
    'dy': 5805000.0,
    'dxUnits': 'meters',
    'dyUnits': 'meters',
    'gridResolution': 290250.0,
    'gridResolutionUnits': 'meters',
    'tilt': 0.0,
    'gridMode': 2,
    'gridType': 'MOM6',
    'ensureEvenI': True,
    'ensureEvenJ': True,
    'angleCalcMethod': 1
})

grd.makeGrid()

grd.setPlotParameters(
    {
        'figsize': (8,8),
        'projection': {
            'name': 'Stereographic',
            'lon_0': 0.0,
            'lat_0': 90.0
        },
        'extent': [-180, 180, 60, 90],
        'iLinewidth': 1.0,
        'jLinewidth': 1.0,
        'showGrid': True,
        'showGridCells': False,
        'title': 'Stereographic: mini IBCAO',
        'iColor': 'y',
        'jColor': 'k',
        'transform': cartopy.crs.PlateCarree()
    }
)

# Save the new grid to a netCDF file
grd.printMsg("Attempt to save the grid to a netCDF file.")
grd.saveGrid(filename=os.path.join(wrkDir, "STE_miniIBCAO_Example6.nc"))

(figure, axes) = grd.plotGrid(
    showModelGrid=False,
    plotVariables={
        'angledx': {
            'values': grd.grid['angle_dx'],
            'title': 'Stereographic: mini IBCAO: angle_dx(1)',
            'cbar_kwargs': {
                'orientation': 'horizontal',
            }
        }
    },
)

figure.savefig(os.path.join(wrkDir, 'IBCAO_angleDX1_Example6.png'), dpi=None,
        facecolor='w', edgecolor='w',
        orientation='landscape', transparent=False, bbox_inches=None, pad_inches=0.1)
