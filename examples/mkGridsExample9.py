#!/usr/bin/env python

# Open the land mask editor for an existing
# ROMS grid

import os, sys
from gridtools.gridutils import GridUtils
from gridtools.grids import roms
from pyproj import Proj
import cartopy.crs as ccrs

# Set a place to write files
os.environ["PYROMS_GRIDID_FILE"] = "/import/AKWATERS/jrcermakiii/configs/Arctic6/roms/gridid.txt"
wrkDir = '/import/AKWATERS/jrcermakiii/configs/zOutput'
inputDir = os.path.join(wrkDir, 'INPUT')

grd = GridUtils()

romsObj = roms.ROMS()
romsGrd = romsObj.get_ROMS_grid('ARCTIC6')

PROJSTRING = "+proj=stere +lon_0=160.0"
map = Proj(PROJSTRING, preserve_units=False)
crs = ccrs.Stereographic(central_latitude=90.0, central_longitude=160.0)
#map = cartopy.crs.NorthPolarStereo(central_longitude=160.0)

#breakpoint()
romsObj.edit_mask_mesh(romsGrd.hgrid, proj=map, crs=crs)
