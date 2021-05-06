# GridUtils

Welcome to the user manual for the GridUtils python library.  This library
provides a one stop shop for grid preparation and manipulation software.
The [design](../development/Design.md) for this library is to keep it
simple and provide a variety of usage patterns.  Work is ongoing with a
laundry list of [TODO](../development/TODO.md) items.

This library currently returns a netCDF file that should be
compatible with a typical `ocean_hgrid.nc` input file.

# Under the hood

The library makes use of xarray for input and output (IO).  Several
open source libraries are used for manipulation of grid and
associated grid fields (boundary files and forcing fields).  The
primary storage format is netCDF.  The dask library is leveraged
where possible.  The library also leverages the geospatial
library pyproj where possible.

# Getting Started

This project assumes the user is familiar with using python as a
programming language.  To get started with using this library, the
first step is [instantiation](https://www.tutorialspoint.com/Explain-Inheritance-vs-Instantiation-for-Python-classes)
of the library's class with a python variable that will point to
the python object.  This also assumes the library has been installed
and is accessible.

```
from gridtools import GridUtils

grd = GridUtils()
```

The `grd` variable or object's functions and methods can not be
used to create or load the users grid and leverage the library's
tools for other available operations.

If working with more than one grid at one time, it is advised to
create or instantiate more than one object.  Use one object for
each grid in use in a single program.

The user manual and examples will refer to this `grd` object
frequently.

In the application form of this library, once all the notebook
cells have run, there is a `grd` object that can be accessed by
adding cells at the bottom of the notebook.  Manipulation of the
`grd` object outside the application can have unexpected
consequences.  The application can only work with one grid at
one time.

Additional details about the application not covered by the
internal application help menu can be found in the
[application](Application.md) portion of the user manual.

Additional details may be gleamed from the internal python
documentation using the built-in
[help()](https://docs.python.org/3/library/functions.html#help)
function.  After importing GridUtils or any library, the internal
help is displayed by using `help(GridUtils)` in a python script or
in a notebook cell.  This also works for individual methods or
functions.

## Feedback

The library provides feedback to the user and the developers by
providing messages back to the screen or logging them to files.
As the library is utilized, it will emit warnings or error as
needed.  If you want to increase or decrease the verbosity
of these messages, please see the [logging](Logging.md) portion
of the user manual.

# Terminology

**grid**: This refers to the entire grid.

**grid cell**: This refers to a grid cell within a grid.

## MOM6

**supergrid**: This refers a denser grid where
there are not only the grid verticies of the **grid cells** but additional
verticies through the center points of the **grid cells** in both the i
and j direction.  This grid is twice the nominal resolution of the model.

Grid orientation, with **no rotation**, is from the lower left to the upper
right.  The i direction increases from lower to upper portion of the grid.
The j direction incrases from left to right.

More grid specifics for MOM6 can be found at these locations:
  * [Cheat sheet for using a Moasic grid with MOM6 output](https://gist.github.com/adcroft/c1e207024fe1189b43dddc5f1fe7dd6c)
  * [Discrete Horizontal and Vertical Grids](https://mom6.readthedocs.io/en/dev-gfdl/api/generated/pages/Discrete_Grids.html)

# Parameters

The library acts on user provided grid and plot parameters.

The user must specify projection information for both the grid and plot
parameters if the grid is to be used on a geographic surface.  In most
cases, the grid and plot projections will be the same unless you wish
to see the grid in a different projection.

The library has also been designed to allow the grid center to be
in a different location than the projection center.  The library
makes *limited* assumptions for parameters and it is highly
recommended to provide complete information no matter how
redundant it may seem.

There are certain assumptions made by the `pyproj` library for
certain projection parameters.

# Grid Creation

The library supports one mode of grid creation at present.  The user
must provide:
  * Size of the grid in the i(dy) and j(dx) direction in degrees or meters.
  * Grid center in degrees or meters.
  * Grid resolution in degrees or meters.

The number of grid cells depends on the total size of the grid
and selected grid resolution.  The library may automatically
adjust number of grid points in the i and j direction.  Automatic
adjustment can be disabled.

## Projections

The user may select from three available projections:
  * Lambert Conformal Conic
  * Mercator
  * Stereographic

Since `pyproj` is utilized by this library, the
default ellipsoids for [projections](https://proj.org/operations/projections/index.html)
is GRS80.  If `proj` is installed, use `proj -le` to produce a
list of available ellipoids.

## Projection Support

These grids are believed to be conformal as generated by the library:
  * Lambert Conformal Conic
  * Mercator (no tilt)
  * Stereographic (with grid distance in meters)

Other grids may be generated, but they are not guaranteed to be conformal.

### Lambert Conformal Conic

All grid parameters must be specified in degrees.

### Mercator

All grid parameters must be specified in degrees.

### Stereographic

The central grid point must be specified in degrees.
Grid distance must be specified in meters.

# Defaults

This section shows all available grid and plot parameters.  Parameter
definitions are provided.

All the available parameters are shown for completeness.  Not all
parameters are needed to create a grid or request a plot.  It some
cases, it does not make sense to mix parameters.  Some parameters
are only available for specific grid types.

## Grid

Grid parameters may be changed through the `setGridParameters` function by
passing a python dictionary.  The order of the parameters does not matter.
The parameter names are case sensitive.

```
grd.setGridParameters({
	'centerUnits': 'degrees',
	'centerX': 0.0,
	'centerY': 0.0,
	'dx': 0.0,
	'dy': 0.0,
	'dxUnits': 'degrees',
	'dyUnits': 'degrees',
	'nx': 0,
	'ny': 0,
	'tilt': 0.0,
	'gridResolution': 0.0,
	'gridResolutionX': 0.0,
	'gridResolutionY': 0.0,
	'gridResolutionUnits': 'degrees',
	'gridResolutionXUnits': 'degrees',
	'gridResolutionYUnits': 'degrees',
	'projection': {
		'name': 'Mercator',
		'lat_0': 0.0,
		'lat_1': 0.0,
		'lat_2': 0.0,
		'lat_ts': 0.0,
		'lon_0': 0.0,
		'ellps': 'GRS80',
		'R': 6378137.0,
		'x_0': 0.0,
		'y_0': 0.0,
		'k_0': 1.0
	},
	'gridMode': 2,
	'ensureEvenJ': True
})
```

Parameter definitions:

Parameter | Definition | Type | Valid Values | Default
--------- | ---------- | ---- | ------------ | -------
centerUnits | units for center grid point | string | 'degrees', 'meters' | 'degrees'
centerX | grid center in j direction | float | **(1)** | n/a
centerY | grid center in i direction | float | **(1)** | n/a
dx | grid length in the j direction | float | **(2)** | n/a
dy | grid length in the i direction | float | **(2)** | n/a
dxUnits | grid length units | string | 'degrees', 'meters' | 'degrees'
dyUnits | grid length units | string | 'degrees', 'meters' | 'degrees'
nx | number of grid points in the j direction | integer | **(3)** | n/a
ny | number of grid points in the i direction | integer | **(3)** | n/a
tilt | degree to rotate the grid | float | 0.0 to 360.0 | 0.0 **(4)**
gridResolution | grid cell size in the i and j direction | float | **(5)** | n/a
gridResolutionX | grid cell size in the j direction | float | **(5)** | n/a
gridResolutionY | grid cell size in the i direction | float | **(5)** | n/a
gridResolutionUnits | grid cell size units in the i and j direction | string | 'degrees', 'meters' | 'degrees'
gridResolutionXUnits | grid cell size units in the j direction | string | 'degrees', 'meters' | 'degrees'
gridResolutionYUnits | grid cell size units in the i direction | string | 'degrees', 'meters' | 'degrees'

NOTES:
 * **(1)** If centerUnits is in 'degrees', the limits for centerX are +0.0 to +360.0 and centerY are -90.0 to +90.0.
 * **(2)** This is a reasonable float number representing degrees or meters.
 * **(3)** This feature has not been implemented yet.
 * **(4)** This parameter only applies to the Lambert Conformal Conic projection.
 * **(5)** Specifying gridResolutionX and/or gridResolutionY will override the value specified for gridResolution

MOM6 parameter definitions:

Parameter | Definition | Type | Valid Values | Default
--------- | ---------- | ---- | ------------ | -------
gridMode | grid generation mode | integer | **(1)** | 2
ensureEvenI | ensure even number of grid points in the i direction | boolean | True, False | True
ensureEvenJ | ensure even number of grid points in the j direction | boolean | True, False | True

NOTES:
 * **(1)** Valid values are 1 and 2.  Grid mode one (1) generates only the specified grid with grid cell distances given by the grid resolution.  Grid metrics will NOT be computed.  Grid mode two (2) generates a standard MOM6 grid with supergrid.  Grid metrics will be computed.
 * `ensureEvenJ` flag allows the grid generator clip the grid if the number of points in the j direction is uneven.

Projection definitions:

Parameter | Definition | Type | Valid Values | Default
--------- | ---------- | ---- | ------------ | -------
name | projection name | string | 'LambertConformalConic', 'Mercator', 'Stereographic' | n/a
lat\_0 | latitude of projection center | degrees | -90.0 to +90.0 | 0.0
lat\_1 | first standard parallel latitude | degrees | -90.0 to +90.0 | 0.0
lat\_2 | second standard parallel latitude | degrees | -90.0 to +90.0 | 0.0
lat\_ts | latitude of true scale | degrees | -90.0 to +90.0 | 0.0 **(1)**
lon\_0 | longitude of projection center | degrees | +0.0 to +360.0 | 0.0
ellps | ellipsoid | string | **(2)** | 'GRS80'
R | radius of the earth sphere | float | **(3)** | n/a
x\_0 | false easting | float | always expressed in meters | 0.0
y\_0 | false northing | float | always expressed in meters | 0.0
k\_0 | scale factor for natural origin or the ellipsoid | float | **(2)** | 1.0

NOTES:
 * **(1)** This parameters take precedence over `k_0` if both options are specified.  For stereographic projections, `lat_0` is used if `lat_ts` is not specified.
 * **(2)** This is a proj string that sets the ellipsoid of the earth or sphere.  See `proj -le` to show all available ellipoids.  Even if an ellipsoid is selected, the radius can be changed by also supplying the `R` argument.
 * **(3)** The radius is normally defined by the ellipsoid.  Use this parameter if the radius of the sphere is slightly different.  Depending on the projection selected, the parameter `k_0` may scale the natural origin or the ellipsoid.

## Plot

Plot parameters may be changed through the `setPlotParameters` function by
passing a python dictionary.  The order of the parameters does not matter.
The parameter names are case sensitive.

```
grd.setPlotParameters({
	'figsize': (5.0, 3.75),
	'extent': [-180.0, +180.0, -90.0, +90.0],
	'showGrid': True,
	'showGridCells': False,
	'showSupergrid': False,
	'title': 'Plot title',
	'iColor': 'k',
	'jColor': 'k',
	'iLinewidth': 1.0,
	'jLinewidth': 1.0,
	'projection': {
		'name': 'Mercator',
		'lat_0': 0.0,
		'lat_1': 0.0,
		'lat_2': 0.0,
		'lat_ts': 0.0,
		'lon_0': 0.0,
		'ellps': 'GRS80',
		'R': 6378137.0,
		'x_0': 0.0,
		'y_0': 0.0,
		'k_0': 1.0
	}
})
```

Parameter definitions:

Parameter | Definition | Type | Valid Values | Default
--------- | ---------- | ---- | ------------ | -------
figsize | default figure size for plots in inches | tuple | (float, float) | (5.0, 3.75) **(1)**
extent | plot extent | list | [float, float, float, float] | n/a **(2)**
extentCRS | plot extent projection | cartopy crs object | **(3)** | cartopy.crs.PlateCarree()
showGrid | plots only show the grid edge | boolean | False, True | True **(4)**
showGridCells | plots show grid cells | boolean | False, True | False **(4)**
showSupergrid | plots show the supergrid | boolean | False, True | False **(4)**
title | plot title | string | any string | n/a **(5)**
iColor | i grid line color | string | **(6)** | 'k'
jColor | j grid line color | string | **(6)** | 'k'
iLinewidth | i grid line width | float | **(7)** | 1.0
jLinewidth | j grid line width | float | **(7)** | 1.0

NOTES:
 * **(1)** The tuple arguments are (width, height) in inches.  This
default figure size is optimized for use in the application portion
of the library.  The library is designed to pass back a figure and
axes matlab object for further customization before rendering. 
 * **(2)** By default, this parameter is not set.  When this parameter
is not set, a geographic map plot will default to a global extent. 
The parameter list is [min x0, max x1, min y0, max y1] where x is
typically longitude and y is latitude.  NOTE: The library pyproj
utilizes longitudes +0.0 to +360.0.  The library cartopy utilizes
longitudes -180.0 to +180.0.
 * **(3)** See [cartopy.crs](https://scitools.org.uk/cartopy/docs/latest/crs/projections.html)
for other projections and required units.  Changing the projection will
require loading the cartopy library.  `import cartopy`
 * **(4)** Not all grid model types will support `showSupergrid`.  If
multiple parameters are set to True, the plot will show the denser of
all the selections.
 * **(5)** By default, the parameter is not set. When set, this is
the title that is shown on the plot.
 * **(6)** By default, grid lines are plotted as black ('k').  The
library utilizes colors available in
[matplotlib](https://matplotlib.org/stable/tutorials/colors/colors.html).
 * **(7)** Grid line width is specified in points (1/72 of an inch).  A grid
can sometimes be viewable at a witdh of 0.1 points.  The grid also
becomes somewhat opaque.

The projection definitions for plot parameters are
the same as the grid parameters and will not be 
repeated here.
