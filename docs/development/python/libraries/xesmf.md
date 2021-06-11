# xesmf

The Regridder algorithm requires:
 * Center coordinate names as lon and lat
 * Corner coordiante names as lon_b and lat_b

The gridtools library will standardize on these to common variable names.

## Quirks

It was determined that the lon grid points need to run from -180.0 to
+180.0 instead from 0.0 to 360.0.

Regridding for grids that require periodic=True has a problem over the
dateline.  A fix is in the work for this in a future xesmf version.
The gridtools installation points to a fixed version temporarily.
