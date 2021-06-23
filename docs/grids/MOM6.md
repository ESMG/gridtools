# MOM6 Grids

## FMS Notes

References:
 * [Gridspec: A standard for description of grids used in Earth System models](https://arxiv.org/abs/1911.08638v1)
 * [Mosaic Tool User Guide](https://data1.gfdl.noaa.gov/~arl/pubrel/r/mom4p1/src/mom4p1/doc/mosaic_tool.html)
 * [A Guide to Grid Coupling in FMS](https://www.gfdl.noaa.gov/guide-to-grid-coupling-in-fms/)
 * [FRE-NCtools](https://github.com/NOAA-GFDL/FRE-NCtools)
 * [Python gridtools](https://github.com/ESMG/gridtools/)

The Flexible Modeling System operates from the same directory (`INPUT`).  This is defined in
`MOM_input` variable `INPUTDIR`.  The `MOM_input` file is defined in `input.nml`.

The top level file is the `grid_spec.nc`.  This file links to three types of files:
 * Mosaics
 * Ocean topography
 * Exchange grid files

## Mosaics

A quick setup entails using the same `ocean_mosaic.nc` file for atmosphere, land and ocean mosaics.
 * atm_mosaic_file = `ocean_mosaic.nc`
 * lnd_mosaic_file = `ocean_mosaic.nc`
 * ocn_mosaic_file = `ocean_mosaic.nc`
 * All should reside in the `INPUT` directory and the mosaics should specify the directory as `./`.

## Ocean topography

The ocean topographic file can be named anything, but the default name is `ocean_topog.nc`.
 * ocean_topog_file = `ocean_topog.nc`
 * This file typically resides in the `INPUT` directory which is specified using `./`.

## Exchange grid files

For the quick case, three files are specified for `tile1`.  The general pattern is:
 * atmos X land
 * atmos X ocean
 * land X ocean

The included points are usually correspond to those requested in the 2nd element.  The land points
are exchanged in `atmosXland` and the ocean points are exchanged in `atmosXocean` and `landXocean`.

## ocean_mosaic.nc

This defines the name of the mosaic without the extension: `ocean_mosaic`.  The `gridlocation`
defines the location of this file which should reside in the `INPUT` directory and should be
specified as `./`.

Each mosaic then points to respective `gridfiles` and `gridtiles`.  In the quick case, there is
only one of each.
  * gridfiles = `ocean_hgrid.nc`
  * gridtiles = `tile1`

## MOM6 Notes

Within the netCDF file for MOM6 grids the following descriptions of 
variables and dimensions:

 * Dimensions
   * nx, ny : grid centers
   * nxp, nxp : grid verticies
