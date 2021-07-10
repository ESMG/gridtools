# Generate a test grid here and print out
# the sha256sum answers for comparison.
def test_import():
    try:
        import sys, os, logging
        from gridtools.gridutils import GridUtils

        grd = GridUtils()

        gtilt = 30.0
        grd.setGridParameters({
            'projection': {
                'name': 'LambertConformalConic',
                'ellps': 'WGS84',
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
            'gridMode': 2.0,
            'gridType': 'MOM6',
            'ensureEvenI': True,
            'ensureEvenJ': True,
            'tileName': 'tile1',
        })

        grd.makeGrid()

        print("PROJECTION:")
        print("  ", grd.grid.attrs['proj'])

        varsToPrint = ['x', 'y', 'dx', 'dy', 'angle_dx', 'area']
        for var in varsToPrint:
            print("** %s: " % (var))
            print(grd.grid[var])

        assert "gridtools" == "gridtools"
    except:
        assert "failed" == "gridutils"
