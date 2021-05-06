# Library design

These are the overarching design elements.  To follow along
with actual milestones, task, todo and extras list, please
consult the [TODO](TODO.md) page.

## Requirements

These are MUST HAVE elements.

The ocean grids are conformal.  This means the angles between the horizontal
and vertical intersections are 90 degrees.

Long term view is to be able to create subsets of grids from an existing global
grid.

Must work with these conformal projections:
 * Mercator
 * Lambert Conformal Conic
 * Polar Stereographic (N and S)
 * Tri Polar

Grid operation:
 * Set, increase, decrease number of grid points (x, y)
 * Set, increase, decrease cell size (dx, dy)
 * Set or unset the requirement that dx = dy
 * Zoom in/out
 * Draw, adjust or delete the drawn grid

### Features

This is a list of elements that would be nice to have.

Grid operation:
 * Adjust the drawn box with a fixed boundary or point
 * Grid rotation

Field import:
 * Regrid bathymetry to new grid
 * Build boundary and forcing files
 * Adaptation of other routines from pyroms

Ability to work in mapping and non-mapping frames of reference.  The
ability to work in raw coordinate systems as needed by example problems.

### Operational modes

Desired operational modes
 * Command line
 * Command line widget mode
 * jupyter notebook
 * jupyter lab
 * cloud: mybinder.org
