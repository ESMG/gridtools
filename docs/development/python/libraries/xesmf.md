# xesmf

The regridder algorithm requires coordinate names in lon and lat.  The grid
tools python library will standardize on these common variable names.

## Quirks

It was determined that the lon grid points need to run from -180.0 to
+180.0 instead from 0.0 to 360.0.   A fix is in the work for this in a
future xesmf version.
