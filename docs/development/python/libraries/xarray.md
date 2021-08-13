# xarray

## sel

When using the selection method for xarray, the dimensions want
array location.  If slice() is used, be sure to use the shape
value to select the entire array.

Reverse slices do odd things: slice(9, 0, -1)

