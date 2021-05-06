# Planned work

## Milestones

 - [ ] Version 0.1
   - [X] Simple polar grid generation
   - [X] Clean up documentation
   - [X] Generify current examples
   - [X] Test examples for LCC grid generation
   - [X] Test examples for regular Mercator grid generation
   - [X] Test examples for stereographic grid generation
   - [X] Test application for LCC grid generation
   - [X] Test application for regular Mercator grid generation
   - [X] Test application for stereographic grid generation
   - [X] Tackle critical TODO items
   - [X] Publish initial commit to ESMG
   - [ ] Ensure mybinder.org works with the published github commit
 - [ ] Version 0.2
   - [ ] Estabish sphinx document generator and link to readthedocs
   - [ ] Allow import of ROMS grid for conversion to MOM6
   - [ ] Enhanced grid/plot projection options
   - [ ] Explore the extent problem for lon defined as +0,+360 vs -180,+180
   - [ ] Leverage dask (expecially for binder.org)
 - [ ] Verison 0.x
   - [ ] Bathymetry and boundery condition support
   - [ ] Grid filling options (flooding)
   - [ ] Grid mask editor
   - [ ] This library is installable via pip
   - [ ] This library is installable via conda

# BUGS
 - [ ] A nested dictionary will clobber other nested elements instead
       of updating elements.  Recode `setPlotParameters` and
       `setGridParameters` to recursively update dictionary elements.

# TASKS

 - [ ] general documentation
   - [X] grid parameters
   - [X] plot parameters
   - [ ] enable sphinx as the documentation generator
   - [ ] link to readthedocs
 - [ ] grid creation/editor
   - [ ] grid metrics
     - [X] Spherical solution is complete via Niki's ROMS to MOM6 converter
     - [X] Mercator (angle_dx might be 0 as it is lined up along latitude lines; except for tilt?)
     - [X] Polar
   - [ ] make Lambert Conformal Conic Grids; needs testing
     - [ ] LCC cannot take custom lat_1 and lat_2; it generates 
           lat_1 and lat_2 based on grid inputs.
     - [X] Update new lat_1 and lat_2 for application after makeGrid() is run
     - [ ] changing plot parameters lat_1 and lat_2 do not seem to impact the view
   - [ ] make Mercator grids; needs testing
     - [ ] issue a warning if tilt is non-zero - disabled
     - [ ] Niki might have solved lat lon tilt?
     - [ ] having tilt may not produce conformal grids
     - [X] Niki's example added; but it may not be correct
   - [X] make Stereographic grids; needs testing
     - [X] using meters; no tilt; based on code from Raphael
     - [X] using degrees; with tilt; based on code from Niki; may not be correct
   - [ ] grid generation in other projections (tri-polar, etc)
   - [X] on saveGrid() convert lon [+0,+360] to [-180,+180]
     - [ ] Unify code that adjusts lon (robTest:PR#1)
   - [X] Unify ellipse radius (R) constants throughout code
     - [X] Gridutils initializes with proj GRS80
     - [X] Allow user control
 - [ ] grid mask editor (land, etc)
 - [ ] integration of bathymetric sources and apply to grids
   - [ ] https://github.com/nikizadehgfdl/ocean_model_topog_generator
   - [ ] xesmf regridder
 - [X] add nbserverproxy/xgcm to conda software stacks; copied to binder environment.yml
 - [ ] Add option to use Alistair's numpypi package as a configurable option in toolsets
 - [ ] turn numpypi into a loadable package via pip
 - [X] add datashader and numpypi from github sources; see postBuild script
   - [ ] implement and document in application
   - [ ] implement and document for programming use
 - [X] xarray \_FillValue needs to be turned off somehow
 - [X] place display(dashboard) as a separate notebook cell
 - [ ] on load of a grid
   - [ ] calculate R
   - [ ] calculate tilt (may not be possible)
   - [ ] update any tool metadata that is appropriate for that grid
   - [ ] parse and utilize any available proj string; must be a global or variable attribute
 - [X] Create an application method within the GridUtils() class; GridTools().app()
 - [ ] Using xesmf regridder and other tools to create bathymetry and other forcing and boundary files
 - [ ] Develop a field "flood" routine similar to pyroms
 - [ ] create a setup.py to allow this library to be installable via pip
 - [ ] Perform checks for ensureEvenI and ensureEvenJ everywhere.  This applies only to the grid not
       the supergrid.

# TODO

 - [X] Further consolidate matplotlib plotting code
   - [X] Refactor plotting code.  It is mostly the same except for setting the projection.
 - [ ] Plotting
   - [X] Grid
   - [X] Gridboxes
   - [ ] Supergrid
 - [ ] Add "Refresh Plot" buttons to other Plot tabs or figure out how to squeeze a single plot button into the layout
 - [ ] Do we have to declare everything in __init__ first or can be push all that to respective reset/clear functions?
 - [ ] refactor messaging/logging out of GridUtils into its own package so we can import printMsg/debugMsg as standalone calls
 - [X] refactor refineS and refineR options as Niki had them defined
 - [X] makeGrid assumes working in degrees
 - [X] Allow library to work in degree or meters
 - [X] Pass back an error graphic instead of None for figures that do not render
 - [ ] Add a formal logging/message mechanism.
   - [X] Allow display of important messages and warnings in panel application: widget=TextAreaInput
   - [X] Create options in application and other tools for user configuration of logging and output.
   - [X] Create a message buffer/system for information.
   - [ ] Create a separate app to watch a log file? https://discourse.holoviz.org/t/scrollable-log-text-viewer/317
   - [ ] log github revision used by mybinder.org instances
 - [ ] For now, the gridParameters are always in reference to a center point in a grid
   in the future, one may fix a side or point of the grid and grow out from that point
   instead of the center.
 - [ ] application
   - [ ] enable user configurable plot and widget sizes (hardcoded in __init__)
   - [ ] enable user to change ellipsoid, R, x_0 and y_0 grid and plot parameters
   - [ ] plotting: adjust satellite_height, for now it is fixed to the default
   - [ ] title is misleading; it should show the projections in use if different
 - [ ] Develop a GridUtils() function
   - [ ] Run `proj -le` and return the names or display the details
   - [ ] Populates the ellps field for the application
 - [ ] x_0 and y_0 are hard coded to be zero offsets.  The user can modify these values.
 - [ ] Deploy use of self.gridMade (robTest:PR#1)
   - [ ] After success in makeGrid()
   - [ ] Successful load of grid from a file
   - [ ] Reset appropriately when clearGrid() is called
 - [ ] More contemplation of longitude range with respect 0, +/-180, 360.
   - [ ] How does this library respond for grids draped over 0 degree longitude vs +/-180 degrees longitude
 - [ ] Add testing harnesses.
   - [ ] pytest: This will allow testing of core code via command line and iterative methods.
   - [ ] selenium: Testing interactive methods may be harder.

# WISH

 - [ ] Add an activity spinner to indicate the notebook is busy
 - [ ] Compute angle_dy for testing of grid conformality.  Theoretically, we can do this check for all grid
       and supergrid cells.
 - [ ] tripolar grids: use FRE-NCtools via cython?
 - [ ] Bring in code that converts ROMS grids to MOM6 grids
   - [ ] Allow conversion of MOM6 grids to ROMS grids
 - [ ] grid reading and plot parameter defaults should be dynamic with grid type declaration and potentially
       split out into separate library modules? lib/gridTools/grids/{MOM6,ROMS,WRF}
 - [ ] Place additional projection metadata into MOM6 grid files
   - [X] Added proj string to netCDF file
   - [ ] Tri polar grid description
 - [ ] Work with generic non-mapping reference systems for use with some of the sample MOM6 problems
 - [ ] Refactor any grid math into a gridmath library.  Any grid computation that can stand on its own
       should be moved into a separate gridmath library.
 - [ ] gridtools::makeGrid() will need a refactor to work with other grid types
 - [ ] write out all MOM6 ancillary files when writing a grid
 - [ ] refactor expansion/clipping of grid points when fitting grid
 - [ ] Add a notebook or two that demonstrates some of the esoteric API
       features of the library: help, debugging, etc.
 - [ ] Dask optimizations
   - [ ] IBCAO grid is too big for mybinder.org
 - [ ] Pull in BC and forcing fields from various sources
   - [ ] Delta method: "We extract 20-30 years of a future projection from several models, build an average of each forcing variable which we superpose on modern day climate.  It’s the so-called delta method.  It debiases climate projections relative to modern day (reanalysis constrained) dynamics, but adds the climate change signal on top of it (as a secular change/delta)."
   - [ ] CMIP/ESM
     - [ ] Browser catalog: https://esgf-node.llnl.gov/search/cmip6/
     - [ ] Programmatic access: https://github.com/intake/intake-esm
     - [ ] http://gallery.pangeo.io/repos/pangeo-gallery/cmip6/
     - [ ] https://github.com/aradhakrishnanGFDL/gfdl-aws-analysis/tree/master/examples
     - [ ] https://github.com/aradhakrishnanGFDL/gfdl-aws-analysis/tree/master/esm-collection-spec-examples
     - [ ] https://github.com/MackenzieBlanusa/OHC_CMIP6
     - [ ] https://github.com/xarray-contrib/cf-xarray
     - [ ] https://github.com/jbusecke/cmip6_preprocessing
