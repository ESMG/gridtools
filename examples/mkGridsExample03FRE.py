import sys, os, logging
from gridtools.gridutils import GridUtils
from gridtools.datasource import DataSource
from gridtools.sysinfo import SysInfo

# Initialize a grid object
grd = GridUtils()
sysObj = SysInfo()

# Define a place to write example files
# FRE-NCtools will write files in the current directory
# so we need to switch to that directory first.
wrkDir = '/import/AKWATERS/jrcermakiii/configs/FRE'
os.chdir(wrkDir)

# This makes the horizontal_grid.nc file
pgm = 'make_hgrid'
if grd.isAvailable(pgm):
    cmd = '%s --grid_type regular_lonlat_grid --nxbnds 2 --nybnds 2 --xbnds -140,-120 --ybnds 25,55 --nlon 40 --nlat 60' % (pgm)
    (stdout, stderr, rc) = sysObj.runCommand(cmd)
    if rc == 0:
        msg = "SUCCESS: %s" % (pgm)
        grd.printMsg(msg, level=logging.INFO)
    else:
        msg = "ERROR: Failed to run: %s" % (cmd)
        grd.printMsg(msg, level=logging.ERROR)
        sys.exit()
else:
    msg = "Executable not found: %s" % (pgm)
    grd.printMsg(msg, level=logging.ERROR)
    sys.exit()

# Ocean and Atmosphere are on the same grid
# Copy horizontal_grid.nc to ocean_hgrid.nc and atmos_hgrid.nc
cmd = "cp horizontal_grid.nc ocean_hgrid.nc"
(stdout, stderr, rc) = sysObj.runCommand(cmd)
cmd = "cp horizontal_grid.nc atmos_hgrid.nc"
(stdout, stderr, rc) = sysObj.runCommand(cmd)

# Create solo mosaic files
pgm = 'make_solo_mosaic'
if grd.isAvailable(pgm):
    cmd = "make_solo_mosaic --num_tiles 1 --dir ./ --mosaic_name ocean_mosaic --tile_file ocean_hgrid.nc"
    cmd = "make_solo_mosaic --num_tiles 1 --dir ./ --mosaic_name atmos_mosaic --tile_file atmos_hgrid.nc"
else:
    msg = "Executable not found: %s" % (pgm)
    grd.printMsg(msg, level=logging.ERROR)
    sys.exit()

# Create a vertical grid
# This is an arbitrary vertical grid taken from another example.  The
# selection of bounds here do not necessarily make sense for this domain!
pgm = 'make_vgrid'
if grd.isAvailable(pgm):
    cmd = "make_vgrid --nbnds 3 --bnds 0.,220.,5500. --dbnds 10.,10.,367.14286 --center c_cell --grid_name ocean_vgrid"
else:
    msg = "Executable not found: %s" % (pgm)
    grd.printMsg(msg, level=logging.ERROR)
    sys.exit()

# Create a useable GEBCO topographic dataset

