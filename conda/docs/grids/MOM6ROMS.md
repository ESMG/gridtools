# MOM6 and MOM6 grids

```
# Both ROMS and MOM6 horizontal grids use an Arakawa C-grid, with four
# types of points:
#   rho: the centers of the cells
#   psi: the corners of the cells, located diagonally between the
#        'rho' points
#   u:   the u-velocity points, located between 'rho' points in the
#        east/west direction
#   v:   the v-velocity points, located between 'rho' points in the
#        north/south direction

# The main differences between the two grids are:
#  * the outermost points of the ROMS grid are the 'rho' points, while
#    the outermost points of the MOM6 grid are the 'psi' points (both
#    with interspersed 'u' and 'v' points); and
#  * the MOM6 grid interleaves all four types of points into a single
#    "supergrid", while ROMS stores them as separate grids.

# The ROMS grid looks like this, with an extra layer of 'rho' points
# around the outside:
# (see https://www.myroms.org/wiki/Numerical_Solution_Technique)
#
#       p - p - p - p - p
#    3  | + | + | + | + |     p = rho (center) points
#       p - p - p - p - p     + = psi (corner) points
#    2  | + | + | + | + |     - = u points
#       p - p - p - p - p     | = v points
#    1  | + | + | + | + |
#       p - p - p - p - p
#
#         1   2   3   4

# The MOM6 grid has 'psi' points on the outside, not 'rho':
#
#    3    + | + | + | +       p = rho (center) points
#         - p - p - p -       + = psi (corner) points
#    2    + | + | + | +       - = u points
#         - p - p - p -       | = v points
#    1    + | + | + | +
#
#         1   2   3   4
```

Here is a representation of a (2, 3) MOM6 grid adapted from convert_ROMS_grid_to_MOM6.py
by Mehmet Ilicak and Alistair Adcroft.  NOTE: The MOM6 supergrid is (5, 7) in shape.

```text
  G SG
     5 + | + | + | +
  2  4 - p - p - p -
     3 + | + | + | +
  1  2 - p - p - p -
     1 + | + | + | +
         1   2   3    G
       1 2 3 4 5 6 7  SG

KEY: p = ROMS rho (center) points; also MOM6 h (center) points
     + = ROMS psi (corner) points
     - = ROMS u points
     | = ROMS v points
     G = grid points
    SG = supergrid points
```

A MOM6 grid of (ny, nx) will have (ny\*2+1, nx\*2+1) points on the supergrid.
NOTE: In python, array storage is zero based.  In the above example, supergrid
point (1, 1) is stored in memory location (0, 0).
