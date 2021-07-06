#!/usr/bin/env python

# Open the land mask editor for an existing
# ROMS grid.  When finished, save the model
# grid.

# This code requires that you start ipython --pylab
# first and then copy and paste the code below
# into the ipython iterpreter.

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

# When finished editing, copy and paste this command
# into ipython.
# romsObj.write_ROMS_grid(romsGrd, filename='grid_py.nc')
