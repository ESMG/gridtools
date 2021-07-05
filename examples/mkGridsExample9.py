#!/usr/bin/env python

# Open the land mask editor for an existing
# ROMS grid

# This code at present has to be copy and pasted
# into ipython prompt started at the command
# line: ipython --pylab

import os, sys
from gridtools.gridutils import GridUtils
from gridtools.grids import roms
from pyproj import Proj
import cartopy.crs as ccrs

# Set a place to write files
os.environ["ROMS_GRIDID_FILE"] = "/import/AKWATERS/jrcermakiii/configs/ROMS/gridid.txt"
wrkDir = '/import/AKWATERS/jrcermakiii/configs/zOutput'
inputDir = os.path.join(wrkDir, 'INPUT')

grd = GridUtils()

romsObj = roms.ROMS()
romsGrd = romsObj.get_ROMS_grid('ARCTIC6')

PROJSTRING = "+proj=stere +lon_0=160.0"
map_crs = ccrs.Stereographic(central_latitude=90.0, central_longitude=160.0)

plotObj = romsObj.edit_mask_mesh(romsGrd.hgrid, crs=map_crs)

# Still need to port the ability to save the
# edited mask.

# When finished editing, uncomment and run this cell
# romsObj.write_ROMS_grid(romsGrd, filename='grid_py.nc')
