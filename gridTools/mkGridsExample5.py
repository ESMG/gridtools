#!/usr/bin/env python

# This is the same as Example4 but in a python script instead of
# a notebook

import numpy as np
import xarray as xr

# IBCAO
# Working in cartesian coordinates, all values are in meters
# NOTE: To create a true MOM6 supergrid, the cell spacing
# is half the length of a full grid cell.
dx = 2500. / 2.
dy = 2500. / 2.
x = np.arange(-2902500., 2902500. + dx, dx, dtype=np.float32)
y = np.arange(-2902500., 2902500. + dy, dy, dtype=np.float32)

yy, xx = np.meshgrid(y, x)

from pyproj import CRS, Transformer

PROJSTRING = "+ellps=WGS84 +proj=stere +lat_0=90 +lat_ts=75"

# create the coordinate reference system
crs = CRS.from_proj4(PROJSTRING)
# create the projection from lon/lat to x/y
proj = Transformer.from_crs(crs.geodetic_crs, crs)

# compute the lon/lat
lon, lat = proj.transform(yy, xx, direction='INVERSE')

# Confirm we have the correct grid points and lat lon values
print(yy[0,0], xx[0,0], lat[0,0], lon[0,0])
print(yy[y.shape[0]-1, x.shape[0]-1], xx[y.shape[0]-1, x.shape[0]-1], lat[y.shape[0]-1, x.shape[0]-1], lon[y.shape[0]-1, x.shape[0]-1])

import os, sys
sys.path.append('lib')
from gridutils import GridUtils

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
    'gridResolution': 2500.0,
    'gridResolutionUnits': 'meters',
    'tilt': 0.0,
    'gridMode': 2,
    'gridType': 'MOM6',
    'ensureEvenI': True,
    'ensureEvenJ': True
})

grd.grid['x'] = (('nyp','nxp'), lon)
grd.grid['y'] = (('nyp','nxp'), lat)

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
        'title': 'Stereographic: IBCAO',
        'iColor': 'k',
        'jColor': 'k'
    }
)

grd.computeGridMetrics()

(figure, axes) = grd.plotGrid()
figure.savefig('configs/test/IBCAO_Example5_script.jpg')

print(grd.grid)
