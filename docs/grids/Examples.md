# Examples

Grid examples have been provided to demonstrate the utility of
the grid generation software.

The python gridtools library uses a default radius of GRS80
or 6.378137e6 meters.  The ROMS grids are based on a radius
of 6370.e3 meters if passed through the pyroms conversion
script.

# Lambert Conformal Conic

## NEP7

This grid description was provided by Kate Hedstrom.

This grid is Lambert Conformal Conic.
Grid resolution is 10km (10000 meters)
The LCC attributes are:
    Standard parallel latitudes: 40.0 and 60.0 North (lat_1, lat_2)
    Central longitude: -91.0 West (lon_0)
    Central latitude: unknown (seems ok for plotting)
    Corner points: (-130,0N) (-220,70N)

PROJ: `+proj=lcc +lat_1=40.0 +lat_2=60.0 +lon_0=-91.0`

## Pacific

The code creates a grid in spherical coordinates.  It appears the final
grid is in Lambert Conformal Conic.  The code allows a tilt to be provided
as input.

This example recreates the the grid demonstrated by Niki Zadah's
[jupyter notebook](https://github.com/nikizadehgfdl/grid_generation/blob/dev/jupynotebooks/regional_grid_spherical.ipynb).

# North Polar Stereo
 
## Arctic6

This grid description was provided by Kate Hedstrom.

This grid is in the North Polar Stereo projection.
This grid has a central longitude of 160.0 West.
The true scale latitude is unknown. Kate thinks it might be 90N?
Having true scale latitude unset for plotting seems to work.

PROJ: `+proj=stere +lat_0=90 +lon_0=-160.0 +R=6370000`

## IBCAO

IBCAO is a North Polar Stero projection grid.  The
[technical reference](https://www.ngdc.noaa.gov/mgg/bathymetry/arctic/IBCAO_TechnicalReference.PDF)
describes the grid in full detail.  See page 9 for grid format.

A Polarstereographic projection with the true scale at
75 °N is “preserved” in the Cartesian grid. The horizontal
datum is World Geodetic System (WGS84).

The center of the grid is the North Pole.

Grid corners:
```text
   X        Y      lon       lat
-------- -------- ------ -------------
-2902500 +2902500 -135.0 +53:49:1.4687
+2902500 +2902500 +135.0 +53:49:1.4687
-2902500 -2902500  -45.0 +53:49:1.4687
+2902500 -2902500  +45.0 +53:49:1.4687
```

PROJ: `+proj=stere +lat_0=90 +lat_ts=75.0 +lon_0=0.0 +ellps=WGS84`
