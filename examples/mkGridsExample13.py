#!/usr/bin/env python3

import os, sys
from gridtools.gridutils import GridUtils
from gridtools.grids import roms

# A grid definition needs to exist to reference a ROMS grid.
# The direct filename is used, not the gridid.txt file.
# Grid definitions are preceeded by two comment lines (#)
# Excerpt from gridid.txt:
'''
# gridid definition file
#
id      = CORAL
name    = CORAL
grdfile = /Volumes/R1/ROMS/CORAL/Grid/coral_grd.nc
N       = 50
grdtype = roms
Vtrans  = 2
theta_s = 7
theta_b = 0.1
Tcline  = 250
#
#
id      = ARCTIC6
name    = ARCTIC6
grdfile = /home/cermak/workdir/configs/Arctic6/roms/grid_Arctic_6.nc
N       = 75
grdtype = roms
Vtrans  = 4
theta_s = 7
theta_b = 2
Tcline  = 250
'''

# This is needed to read a ROMS grid if openGrid()/readGrid() are used.
os.environ["ROMS_GRIDID_FILE"] = "/import/AKWATERS/jrcermakiii/configs/ROMS/gridid.txt"

# Define where output should be written
wrkDir = '/home/cermak/workdir/configs/Arctic6'

# We are writing output of the grid conversion to the INPUT directory normally
# used for MOM6.  When MOM6 is run, it is looking for model grid usually from
# the INPUT.
inputDir = os.path.join(wrkDir, 'INPUT')

# Initialize the gridtools module
grd = GridUtils()

# Read the ROMS grid directly using openDataset() and assign
# the gridType of ROMS.
# Do not use openGrid()/readGrid().

# DO NOT USE THIS
# grd.openGrid(None, gridType='ROMS', gridid='ARCTIC6')
# grd.readGrid()

# USE openDataset()/readGrid()
romsGrid = grd.openDataset("/home/cermak/workdir/configs/Arctic6/roms/grid_Arctic_6.nc")
grd.readGrid(gridType="ROMS", local=romsGrid)

# Convert the ROMS grid to MOM6
# The grid type will be changed from ROMS to MOM6.
# A ROMS grid may have topography defined in the vertical grid.
# Either 'h' or 'hraw' may be used.  It may not exist.

# NOTE: For this particular grid, the default angle_dx calcuations
# were incorrect. Alternate methods can be triggered with the
# angleCalcMethod keyword option.  See:
grd.convertGrid('MOM6',
        overwrite=True,
        writeTopography=True,
        writeMosaic=True,
        writeLandmask=True,
        writeOceanmask=True,
        writeCouplerMosaic=True,
        writeExchangeGrids=True,
        inputDirectory=inputDir,
        topographyVariable='h',
        angleCalcMethod=1
)

# Add projection metadata to the converted grid
arcticGridPROJ = "+proj=stere +lat_0=90 +lon_0=-160.0 +R=6370000"
grd.grid.attrs['proj'] = arcticGridPROJ

# Finally, save the ocean_hgrid.nc
grd.saveGrid(directory=inputDir, filename='ocean_hgrid.nc')
