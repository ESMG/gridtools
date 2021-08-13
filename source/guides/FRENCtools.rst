.. fre_nctools_comparison:

***********
FRE-NCtools
***********

Comparison of grid generation methods between gridtools and FRE-NCtools
#######################################################################

This guide demonstrates two things:

    * the creation of two similary constructed MOM6 model grids using
      gridtools and FRE-NCtools

    * the creation of `ocean_topog.nc` using available functions
      in the gridtools library

.. note::
    The FRE-NCtools software can be downloaded from the
    `FRE-NCtools <https://github.com/NOAA-GFDL/FRE-NCtools>`_ github
    website.

Grid Generation
***************

In this section, a MOM6 model grid is created using the gridtools
library and then the FRE-NCtools software.

In both examples, the
MOM6 model grid is in the Mercator projection.  The regular grid
is 1.0 degree x 1.0 degree.  The representation of this grid in
the `ocean_hgrid.nc` file is typically a *supergrid*.  The
resolution of this grid is half the distance which is
0.5 degrees x 0.5 degrees.

The MOM6 model grid extent is from 220 East (or -140 West) to
240 East (or -120 West) and 25 to 55 North.  The number of
*supergrid* cells is 40 in the longitude or *j*-direction
and 60 in the latitude or *i*-direction.

gridtools
=========

A python script was written to demonstrate the creation of the
MOM6 model grid using the gridtools python library.
This example is currently named:
`mkGridsExample03.py <https://github.com/ESMG/gridtools/blob/main/examples/mkGridsExample03.py>`_

A MOM6 model grid is created by specifing grid parameters
with respect to the regular grid.  The grid center is
specified and the number of grid cells evenly distributed
along the *i* and *j*-direction.  It is possible for a
regular grid cell to become centered over the grid center
in either the *i* and *j*-direction.  The *supergrid* will
always have an odd number of vertices which represents
the number of regular grid points times two plus one.

A detailed description of the representation of discrete
horizontal and vertical grids can be found
in the
`MOM6 User Manual <https://mom6.readthedocs.io/en/dev-gfdl/api/generated/pages/Discrete_Grids.html>`_.

Grid parameters::
    * **gridResolution**: 1.0 degree; the distance of the regular grid
      cell in both *i* and *j*-direction.
    * **dx**: 20; the number of grid cells to use along the longitude
      or *j*-direction.
    * **dy**: 30; the number of grid cells to use along the latitude
      or *i*-direction.

Specification of the grid center for longitude is specified in the
total number of degrees East from the Prime Meridian.

Grid parameters::
    * **centerX**: 230.0; 230.0 degrees East of the Prime Meridian
    * **centerY**: 40.0; 40.0 degrees North

Once the grid paramters are set, a call to
:py:func:`~gridtools.gridutils.GridUtils.makeGrid`
will result in construction of a regular grid that is 20x30 and
a *supergrid* of 41x61 points that form vertices and pass through the
center of the grid points.

FRE-NCtools
===========

A python script was written to demonstrate the creation of the
MOM6 model grid using the FRE-NCtools software package.
This example is currently named:
`mkGridsExample03FRE.py <https://github.com/ESMG/gridtools/blob/main/examples/mkGridsExample03.py>`_

A MOM6 model grid is created by specifying grid parameters
with respect to the *supergrid*.

The executable, `make_hgrid`, is used to create the MOM6 model grid.
The program will create an output filename called `horizontal_grid.nc`.

The Mercator grid projection is specified by the program arguent `--grid_type`
using `regular_lonlat_grid`.

The next two arguments specifies the number of x (or *j*) and y (or *i*) boundaries
in the MOM6 model grid.  Since this is a rectangle, there are two boundaries in
each direction.  The extents of the rectangle are specified in the next two arguments.

Grid parameter arguments::
    * **--nxbnds** 2
    * **--nybnds** 2
    * **--xbnds** -140,-120
    * **--ybnds** 25,55

Since longitude has a length of 20 degrees and the desired distance for
the *supergrid* is 0.5 degrees, the number of points along the longitude
is 40.  Since latitude has a length of 30 degrees, the number of points
needed to create 0.5 degree spacing is 60 points.

Grid parameters arguments::
    * **--nlon** 40
    * **--nlat** 60

This creates a regular grid that 20x30 grid points.  The *supergrid* will
have 41x61 points that make up the grid vertices that form the edges of
the regular grid and pass through the grid centers.

The full command pulling all the above arguments togther is:
::

    make_hgrid --grid_type regular_lonlat_grid --nxbnds 2 --nybnds 2\
        --xbnds -140,-120 --ybnds 25,55 --nlon 40 --nlat 60
