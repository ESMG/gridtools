*******
Spacing
*******

This section describes the "`Spacing`" controls
for generation of the model grid.

This controls the construction of the model grid
about the center point.

Grid Extent
===========

The `dx` and `dy` represent the **DISTANCE** of the
entire model grid in the x and y directions.  The
**UNITS** need to be in degrees or meters.

Grid Resolution
===============

The grid resolution in the X and Y direction
in degress or meters. These represent the
individual cell distances in the X and Y
direction.

Number of grid points
=====================

The following equations are used to determine
the number of grid points in the x and y
directions.

.. math::

    nx = dx / X

    ny = dy / Y

The supergrid will be of the size:

.. math::

    (ny * 2) + 1, (nx * 2) + 1

If the grid cell distance is *INCREASED*
the number of grid cells will *DECREASE*.

.. note::

    This is for the construction of the
    regular grid cells for a MOM6 model
    grid.  A supergrid is automatically
    created for the regular MOM6 model
    grid.
