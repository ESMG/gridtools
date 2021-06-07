# Test that we get the proper coordinates to/from points
# associated with corners of the IBCAO grid

def test_ibcao_wgs84():
    import numpy as np
    import xarray as xr
    from pyproj import CRS, Transformer

    PROJSTRING = "+ellps=WGS84 +proj=stere +lat_0=90 +lat_ts=75"

    # create the coordinate reference system
    crs = CRS.from_proj4(PROJSTRING)
    # create the projection from lon/lat to x/y
    proj = Transformer.from_crs(crs.geodetic_crs, crs)

    yy = [
        -2902500.0,
        -2902500.0,
        2902500.00,
        2902500.00
    ]
    xx = [
        -2902500.0,
        2902500.0,
        -2902500.0,
        2902500.0
    ]

    # compute the lon/lat
    lon, lat = proj.transform(yy, xx, direction='INVERSE')

    print(lon)
    print(lat)

