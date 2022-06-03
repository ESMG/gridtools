Build a new grid
================

This section describes how to set the grid parameters
for building a new grid.

Please see :py:func:`gridtools.gridutils.GridUtils.setGridParameters`
for explanation of all available parameters.

By default, a grid center is defined.  A total distance
in the :math:`x` and :math:`y` direction of the grid
is defined.  The number of grid points is determined by
the defined resolution of the grid cells in the :math:`x`
and :math:`y` direction.

This example creates the IBCAO grid as described by the
`Technical Reference and User's Guide <https://www.ngdc.noaa.gov/mgg/bathymetry/arctic/IBCAO_TechnicalReference.PDF>`_.
:cite:`IBCAO_TechnicalReference` :cite:`GEBCO_Centenary_Conference`

The user manual states that the IBCAO grid is a
Cartesian grid which has coordinates in meters in
the :math:`x` and :math:`y` direction.   The grid
center or **Origin** is the North Pole.  The
Cartesian grid system starts at an :math:`(x,y)`
of :math:`(0,0)`
at the North Pole.

The grid size is 580.5 km in both directions giving
a size of 2902500 meters on all sides of the North
Pole.

To create an IBCAO grid suitable for MOM6, grid
parameters need to be set to appropriate values.

The user manual states the IBCAO grid is in
the **Polarsterographic** projection.  For `gridtools`,
this is specified as ``Stereographic``.  In that
projection, the true scale is preserved at 75 degrees
North.  For `gridtools`, this is specified by setting
``lat_ts`` to ``75.0``.  Although the grid in
Cartesian space is :math:`(0,0)`, in `gridtools`, the
grid center needs to be specified in map coordinates
for the projection center and the grid center.

To specify that the grid should be centered
at the North Pole, in `gridtools` set the grid
projection parameters ``lon_0`` to ``0.0`` and ``lat_0``
to ``90.0``.  The grid parameters ``CenterX`` is also ``0.0``
and ``CenterY`` is ``90.0``.  The ``CenterUnits`` should
be set to ``degrees``.

The user manual specifies a standard radius of the Earth
by stating that the "horizontal datum is World Geodetic
System (WGS 84)".  This is specified in `gridtools` using
the projection parameter of ``WGS84`` for the ``ellps``
(ellipsoid) parameter.

The user manual states the grid distance is 2.5 km.  The
grid resolution is 2500 meters.  In `gridtools`, ``dx``
and ``dy`` are set to the total distance of the grid
or ``5805000.0`` meters.  The ``gridResolution`` is
set to ``2500.0`` meters.  The units should be set
to ``meters`` for ``dxUnits``, ``dyUnits``, and
``gridResolutionUnits``.

The grid parameters ``tilt`` is optional.  The
default value of ``0.0`` is shown in the example.

For now, MOM6 grids should all be created using
a ``gridMode`` of ``2`` to specify creation of
a supergrid.  For MOM6 grids, the ``gridType``
should be ``MOM6``.

The parameters ``ensureEvenI`` and ``ensureEvenJ``
ensure the supergrid is properly sized.  Use the
default value of ``True`` for now.

Here is the command pulling all the above parameters
together ready to create the IBCAO grid::

    # Create a gridtools object
    from gridtools.gridutils import GridUtils
    grd = GridUtils()

    # Define IBCAO grid for gridtools library
    grd.setGridParameters({
        'projection': {
            'name': "Stereographic",
            'ellps': 'WGS84',
            'lon_0': 0.0,
            'lat_0': 90.0,
            'lat_ts': 75.0,
        },
        'centerX': 0.0,
        'centerY': 90.0,
        'cneterUnits': 'degrees',
        'dx': 5805000.0,
        'dy': 5805000.0,
        'dxUnits': 'meters',
        'dyUnits': 'meters',
        'gridResolution': 2500.0,
        'gridResolutionUnits': 'meters',
        'tilt': 0.0,
        'gridMode': 2,
        'gridType': 'MOM6',
        'ensureEvenI': True,
        'ensureEvenJ': True
    })

After setting the grid parameters, the
next command will instruct `gridtools` to
make the grid::

    grd.makeGrid()

For systems with smaller amounts of memory,
`example #6 <https://github.com/ESMG/gridtools/blob/exp/rel031/examples/mkGridsExample06.py>`_
constructs a mini IBCAO grid with fewer grid points.

Grid metrics
------------

This section describes the generation of grid metrics.  Grid metrics includes
information such as `angle_dx`....


