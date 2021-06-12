# Planned work

## Milestones

 - [X] Version 0.1.1
   - [X] Installation and usage tutorials
   - [X] Make library installable via pip or setup.py
   - [X] Create specific installation instructions
 - [ ] Version 0.2
   - [X] Implement a basic data catalog for data management
   - [X] Improve reproducibility of grids produced by the library
   - [X] Establish sphinx document generator and link to readthedocs
   - [X] Construct initial bathymetry grid for new grids
   - [X] Construct bathymetric roughness
   - [ ] Construct initial grid ocean/land masks for new grids
   - [ ] Creation of more of the needed files to run a MOM6 simulation
 - [ ] Verison 0.x
   - [ ] Sponge data preparation
   - [ ] Subset existing grids and infrastructure
   - [ ] Leverage dask (for users that lack access to large memory nodes)
   - [ ] Explore the extent problem for lon defined as +0,+360 vs -180,+180
   - [ ] Enhanced grid/plot projection options
   - [ ] Allow import of ROMS grid for conversion to MOM6
   - [ ] Allow export of MOM6 grid to ROMS
   - [ ] Boundery condition grid creation and support
   - [ ] Grid filling options (flooding)
   - [ ] Grid mask editor
   - [ ] This library is installable via conda

# BUGS
 - [X] app:Remote Files does not save the grid in the specified directory
 - [ ] A nested dictionary will clobber other nested elements instead
       of updating elements.  Recode `setPlotParameters` and
       `setGridParameters` to recursively update dictionary elements.
 - [ ] Regular filenames should be usable everywhere that takes file or
       data source arguments.
 - [ ] file:// spec does not honor relative paths.  There should be
       generic support for relative and absolute paths for file:// and
       ds:// file specs.

# TASKS

 - [ ] Sponge data preparation
   - [ ] Current scripts generate u,v fields on h-points; this needs to be changed to C-grid u/v-points instead
 - [ ] general documentation
   - [X] enable sphinx as the documentation generator
   - [X] link to readthedocs
   - [ ] include local markdown files
     - [ ] Hack on m2r2 python module for sphinx
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
     - [ ] having tilt may not produce conformal grids
     - [X] Niki's example added; but it may not be correct
     - [ ] Niki might have solved lat lon tilt?
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
     - [ ] add routines for mask checking
     - [ ] add routines for updating the exchange grid masks
     - [ ] Obey `MASKING_DEPTH`, `MINIMUM_DEPTH`, `ALLOW_LANDMASK_CHANGES`,
           `MAXIMUM_DEPTH`, `TOPO_EDITS_FILE` MOM6/src/initialization parameters
 - [ ] integration of data sources
   - [ ] generic regridder for creating boundary files from data sources
   - [ ] xesmf regridder for bathymetry sources
   - [ ] option to create land mask fraction
   - [ ] option to use source grid as a supergrid for coarsening
   - [X] implemented as topoutils.TopoUtils.regridTopo()
   - [ ] refactor function arguments into kwargs
   - [ ] refactor print statements to use gridtools logging facility
 - [ ] integration of bathymetric sources and apply to grids
   - [ ] https://github.com/nikizadehgfdl/ocean\_model\_topog\_generator
   - [ ] fix native zero band columns in partitions
   - [ ] flexible partitioning / rework
   - [ ] Investigate `get_indices1D()` function
   - [ ] Rework detection of grid bounds
   - [ ] Rework calculation of input grid points available vs grid points utilized
   - [ ] Rework for use with periodic grids
   - [ ] Include metadata for each partition: number of refinements, etc
   - [ ] implement useFixByOverlapQHGridShift so a regular grid can be used without a shift
   - [ ] Implement `TOPO_EDITS_FILE` in bathytools.applyExistingLandMask()
 - [X] add nbserverproxy/xgcm to conda software stacks; copied to binder environment.yml
 - [ ] improve reproducibility
   - [ ] include a dump of conda environment in the grid file (nc)
   - [ ] if conda environment does not exist, do some other snooping
   - [X] add sha256 to grid elements
 - [ ] Add option to use numpypi package (Alistair) as a configurable option in gridtools
 - [X] turn numpypi into a loadable package via pip
 - [X] add datashader and numpypi from github sources; see postBuild script
   - [ ] implement and document in application
   - [ ] implement and document for programming use
 - [ ] on load of a grid into gridtool library
   - [ ] calculate R
   - [ ] calculate tilt (may not be possible)
   - [ ] update any tool metadata that is appropriate for that grid
   - [ ] parse and utilize any available proj string; must be a global or variable attribute
 - [ ] Using xesmf regridder and other tools to create bathymetry and other forcing and boundary files
 - [ ] Develop a field "flood" routine similar to pyroms
 - [ ] Perform checks for ensureEvenI and ensureEvenJ everywhere.  This applies only to the grid not
       the supergrid.

# TODO

 - [ ] Plotting
   - [X] Grid
   - [X] Gridboxes
   - [ ] Supergrid
   - [ ] Fields (from data sources or script generated)
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
   - [ ] enable user to change ellipsoid, R, `x_0` and `y_0` grid and plot parameters
   - [ ] plotting: adjust `satellite_height`, for now it is fixed to the default
   - [ ] title is misleading; it should show the projections in use if different
 - [ ] Develop a GridUtils() function
   - [ ] Run `proj -le` and return the names or display the details
   - [ ] Populates the ellps field for the application
 - [ ] `x_0` and `y_0` are hard coded to be zero offsets.  The user can modify these values.
 - [ ] Deploy use of self.gridMade (robTest:PR#1)
   - [ ] After success in makeGrid()
   - [ ] Successful load of grid from a file
   - [ ] Reset appropriately when clearGrid() is called
 - [ ] More contemplation of longitude range with respect 0, +/-180, 360.
   - [ ] How does this library respond for grids draped over 0 degree longitude vs +/-180 degrees longitude
 - [ ] numpypi
   - [ ] a test fails in `test_trunc.py`
 - [ ] Add testing harnesses.
   - [X] pytest: This will allow testing of core code via command line and iterative methods.
   - [ ] pytest: Setup some simple projection tests: IBCAO, ....
   - [ ] pytest: Refactor numpypi into structured tests under pytest
   - [ ] pytest: allow certain tests to fail if a module is not available (issue warnings instead)
   - [ ] selenium: Testing interactive methods may be harder.
 - [X] gridtools.openDataset() should scan the dsName for a file:// or
       http: address maybe using the parser to detect something that
       is not a catalog.  This routine could be improved.

# WISH

 - [ ] Teach grid tools to use "input.nml" to find grid related things for model runs.
 - [ ] Investigate the differences between FRE-NCtools vs gridutils.  Are
       there things that we could use there instead of recreating many wheels.
       There are lot of FRE-NCtool references in the ROMS to MOM6 conversion tool.
 - [ ] Migrate to use of file:// or http://, https:// for file specifications.
 - [ ] Allow gridtools to continue to operate with some disabled routines that use xesmf.
 - [ ] app:Save remote files; additional sanity checks
 - [ ] app:Add an activity spinner to indicate the notebook is busy
 - [ ] Compute `angle_dy` for testing of grid conformality.  Theoretically,
       we can do this check for all grid and supergrid cells.
 - [ ] tripolar grids: use FRE-NCtools via cython?
 - [ ] Bring in code that converts ROMS grids to MOM6 grids
   - [ ] Allow conversion of MOM6 grids to ROMS grids
 - [ ] grid reading and plot parameter defaults should be dynamic with
       grid type declaration and potentially split out into separate
       library modules? lib/gridTools/grids/{MOM6,ROMS,WRF}
 - [ ] Place additional metadata into MOM6 grid files
   - [X] Grid parameters
   - [X] Software stack, git information
   - [ ] Alternate version/software capture if conda and/or git is not available
   - [X] Added proj string to netCDF file
   - [ ] Tri polar grid description
   - [ ] Update conda capture code so a temporary file is not necessary
 - [ ] Work with generic non-mapping reference systems for use with some of the sample MOM6 problems
 - [ ] Refactor any grid math into a gridmath library.  Any grid computation that can stand on its own
       should be moved into a separate gridmath library.
 - [ ] gridtools.makeGrid() will need a refactor to work with other grid types
 - [ ] write out all MOM6 ancillary files when writing a grid
 - [ ] refactor expansion/clipping of grid points when fitting grid
 - [ ] Add a notebook or two that demonstrates some of the esoteric API
       features of the library: help, debugging, etc.
 - [ ] Dask optimizations
   - [ ] creating the native IBCAO grid is too big for mybinder.org
 - [ ] Subset any grid for running with MOM6
   - [ ] https://github.com/ESMG/regionalMOM6_notebooks/tree/master/creating_obc_input_files
   - [ ] May be especially useful for debugging situations; Arctic6
 - [ ] Allow gridtools to be used without xesmf and xgcm; enable module detection for available capabilities
 - [ ] Update setup.py and other files with package dependencies
   - Create a configuration script that would perform autosetup of gridtools library
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
 - [ ] triton node issue: python netCDF4 large file reading seems to hang nodes
 - [ ] Add an Example 7a to demonstrate using existing files from Example 7.
