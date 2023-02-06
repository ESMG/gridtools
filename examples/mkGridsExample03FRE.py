#!/usr/bin/env python

import sys, os, logging, cartopy
import numpy as np
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
    cmd = "%s --grid_type regular_lonlat_grid --nxbnds 2 --nybnds 2 --xbnds -140,-120 --ybnds 25,55 --nlon 40 --nlat 60" % (pgm)
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
    cmd = "%s --num_tiles 1 --dir ./ --mosaic_name ocean_mosaic --tile_file ocean_hgrid.nc" % (pgm)
    (stdout, stderr, rc) = sysObj.runCommand(cmd)
    if rc == 0:
        msg = "SUCCESS: %s" % (pgm)
        grd.printMsg(msg, level=logging.INFO)
    else:
        msg = "ERROR: Failed to run: %s" % (cmd)
        grd.printMsg(msg, level=logging.ERROR)
        sys.exit()
    cmd = "%s --num_tiles 1 --dir ./ --mosaic_name atmos_mosaic --tile_file atmos_hgrid.nc" % (pgm)
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

# Create a vertical grid
# This is an arbitrary vertical grid taken from another example.  The
# selection of bounds here do not necessarily make sense for this domain!
pgm = 'make_vgrid'
if grd.isAvailable(pgm):
    cmd = "%s --nbnds 3 --bnds 0.,220.,5500. --dbnds 10.,10.,367.14286 --center c_cell --grid_name ocean_vgrid" % (pgm)
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

# Create a useable GEBCO topographic dataset
# The program make_topog requires:
#  - missing_value must exist and be of type NC_DOUBLE, NC_FLOAT, NC_INT, NC_SHORT or NC_CHAR
#  - variable with topo/bathy info must be NC_DOUBLE, NC_FLOAT or NC_INT
#  - a vertical grid: ocean_vgrid.nc

if not(os.path.isfile('GEBCO_subset.nc')):

    msg = "Creating GEBCO subset for MOM6 model grid."
    grd.printMsg(msg, level=logging.INFO)

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
                'url' : 'file:///import/AKWATERS/jrcermakiii/bathy/gebco/GEBCO_2020.nc',
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

    # Load the dataset
    gebco = grd.openDataset("ds:GEBCO_2020")

    la = gebco.coords['lat']
    lo = gebco.coords['lon']

    # Subset GEBCO to the extent of the MOM6 model grid
    gebcoSubset =\
        gebco.loc[dict(lon=lo[(lo >= -150) & (lo <= -110)], lat=la[(la >= 20) & (la <= 60)])]

    # Need to use Numpy to assign a specific dtype to missing_value
    # otherwise (-9999) will yield a long integer.
    gebcoSubset['depth'].attrs['missing_value'] = np.array([-9999], dtype='int32')[0]

    # Update metadata
    gebcoSubset['depth'].attrs['standard_name'] = "height_below_reference_ellipsoid"
    gebcoSubset['depth'].attrs['long_name'] = "Depth relative to sea level"
    del gebcoSubset['depth'].attrs['sdn_parameter_urn']
    del gebcoSubset['depth'].attrs['sdn_parameter_name']
    del gebcoSubset['depth'].attrs['sdn_uom_urn']
    del gebcoSubset['depth'].attrs['sdn_uom_name']

    # Convert elevation=>depth to NC_INT(int32)
    gebcoSubset.to_netcdf('GEBCO_subset.nc', encoding =
            {'depth': {'dtype': 'int32'}})
else:
    msg = "The GEBCO subset for MOM6 model grid already exists."
    grd.printMsg(msg, level=logging.INFO)

# Create the topography for the MOM6 model grid
pgm = "make_topog"
if grd.isAvailable(pgm):
    cmd = "%s --verbose --mosaic ocean_mosaic.nc --topog_type realistic --scale_factor -1 --vgrid ocean_vgrid.nc --output ocean_topog.nc --topog_file GEBCO_subset.nc --topog_field depth" % (pgm)
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

# Read the MOM6 model grid
grd.openGrid('ocean_hgrid.nc')
grd.readGrid()

# Define plot parameters for this model grid
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
(figure, axes) = grd.plotGrid()

# Show the FRE model grids
msg = "Creating MOM6 model grid graphics."
grd.printMsg(msg, level=logging.INFO)
figure.savefig(os.path.join(wrkDir, 'MERC_20x30_Example3FRE.jpg'),
        dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', transparent=False, bbox_inches=None,
        pad_inches=0.1)

figure.savefig(os.path.join(wrkDir, 'MERC_20x30_Example3FRE.pdf'),
        dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', transparent=False, bbox_inches=None,
        pad_inches=0.1)

# Plot the diagnosed ocean topography
ocean_topog = grd.openDataset('ocean_topog.nc')

(figure, axes) = grd.plotGrid(
    showModelGrid=False,
    plotVariables={
        'depth': {
            'values': ocean_topog['depth'],
            'title': 'Diagnosed ocean topographic field from make_topog',
            'cbar_kwargs': {
                'orientation': 'horizontal',
            }
        }
    },
)
msg = "Creating MOM6 model grid diagnosed ocean topography graphic."
grd.printMsg(msg, level=logging.INFO)
figure.savefig(os.path.join(wrkDir, 'MERC_20x30_FREBathy.png'), dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape', transparent=False, bbox_inches=None, pad_inches=0.1)

