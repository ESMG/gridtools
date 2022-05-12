# TEST: Generate a regular grid with one land point but with the attempt of
#       using the noLandMosaic=True option.
# Expected result: An ERROR should be generated as there is a land point
#     in the grid but asked to not generate a land mosaic file.  A land
#     mosaic file should exist.

import pytest
xfail = pytest.mark.xfail

from gridtools.gridutils import GridUtils
import os, glob
import numpy as np
import xarray as xr

def clean_output_directory(tmp_path, glob_patterns):

    # Make sure no matching glob patterns are found
    # before running this test

    for p in glob_patterns:
        mfiles = glob.glob(p)
        for mfile in mfiles:
            if os.path.isfile(mfile):
                os.unlink(mfile)

@xfail
def test_regular_grid_with_land_point(tmp_path):

    # Create a gridtools object
    grd = GridUtils()

    # Define a small 5x5 grid with 1000.0 meter resolution
    grd.setGridParameters({
        'projection': {
            'name': "Stereographic",
            'ellps': 'WGS84',
            'lon_0': 0.0,
            'lat_0': 90.0,
            'lat_ts': 75.0,
        },
        'centerX': 5.0,
        'centerY': 75.0,
        'cneterUnits': 'degrees',
        'dx': 5000.0,
        'dy': 5000.0,
        'dxUnits': 'meters',
        'dyUnits': 'meters',
        'gridResolution': 1000.0,
        'gridResolutionUnits': 'meters',
        'tilt': 0.0,
        'gridMode': 2,
        'gridType': 'MOM6',
        'ensureEvenI': True,
        'ensureEvenJ': True
    })

    grd.makeGrid()
    wrkDir = tmp_path
    clean_output_directory(tmp_path, ["*.nc"])
    grd.saveGrid(filename=os.path.join(wrkDir, "ocean_hgrid.nc"))

    h = 30. * np.ones((len(grd.grid.ny)//2, len(grd.grid.nx)//2))
    # Create a land point
    h[1,1] = 0.0
    m = np.ones((len(grd.grid.ny)//2, len(grd.grid.nx)//2))
    bathyGrids = xr.Dataset({'depth': (['ny', 'nx'], h),
                             'mask':  (['ny', 'nx'], m) })
    grd.writeOceanmask(bathyGrids, 'depth', 'mask',
                os.path.join(wrkDir, 'ocean_mask.nc'),
                MASKING_DEPTH=0.0)
    grd.writeLandmask(bathyGrids, 'depth', 'mask',
                os.path.join(wrkDir, 'land_mask.nc'),
                MASKING_DEPTH=0.0)
    bathyGrids.to_netcdf(os.path.join(wrkDir, 'ocean_topog.nc'),
                encoding=grd.removeFillValueAttributes(data=bathyGrids))
    grd.makeSoloMosaic(
        topographyGrid=bathyGrids['depth'],
        writeLandmask=True,
        writeOceanmask=True,
        inputDirectory=wrkDir,
        overwrite=True,
        noLandMosaic=True
    )

    # Examine output

    # Test fails if one of these files is missing
    files_present = ["atmos_mosaic_tile1Xland_mosaic_tile1.nc",\
        "atmos_mosaic_tile1Xocean_mosaic_tile1.nc",\
        "land_mosaic_tile1Xocean_mosaic_tile1.nc"]

    for file_to_check in files_present:
        full_path_file = os.path.join(tmp_path, file_to_check)
        if not(os.path.isfile(full_path_file)):
            assert False

    # Do some variable size and content checks
    file_to_check = "atmos_mosaic_tile1Xland_mosaic_tile1.nc"
    ds = xr.open_dataset(os.path.join(tmp_path,file_to_check))
    mosaic_length = (ds['tile1_cell'].shape)[0]
    if mosaic_length != 1:
        print("%s should have a length of 1 (%d)." % (file_to_check,\
            mosaic_length))
        assert False
    ds.close()

    file_to_check = "land_mosaic_tile1Xocean_mosaic_tile1.nc"
    ds = xr.open_dataset(os.path.join(tmp_path,file_to_check))
    mosaic_length = (ds['tile1_cell'].shape)[0]
    if mosaic_length != 24:
        print("%s should have a length of 24 (%d)." % (file_to_check,\
            mosaic_length))
        assert False
    ds.close()

    file_to_check = "ocean_hgrid.nc"
    ds = xr.open_dataset(os.path.join(tmp_path,file_to_check))
    if ds['tile'].dtype.kind != 'S':
        print("Variable 'tile' in %s should be of kind (S) string." %\
            (file_to_check))
        assert False
    if ds['tile'].dtype.itemsize != 5:
        print("Variable 'tile' in %s should have an itemsize of 5." %\
            (file_to_check))
        assert False

    assert True
