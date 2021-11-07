# netCDF

The netCDF kitchen sink tools append to the global history element by
separating the inserted strings by a linefeed (`\n`).

For example:
```
:history = "Sat Nov  6 15:45:29 2021: ncrename -v xx,x land_mask_Example3.nc\nSat Nov  6 15:45:11 2021: ncrename -v x,xx land_mask_Example3.nc" ;
```
