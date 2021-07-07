# Changelog

# 2021-07-06

 - Try to save an artifact to github actions: conda dump
 - All examples are functional on aarch64
 - Clear all outputs in notebooks again
 - Fix title bar on pylab plot
 - conda vs pip: pyqt vs PyQt5
 - ROMS grid writing is confirmed operational
 - Added coastline plotting to pylab grid editor.
 - CI failed with added pyqt requirement.
 - Fix example 9 for projection parameter in use instead of crs.
 - Need to debug/test further on our big node.
 - For the aarch64 platform, the virtualenv (venv) cannot be used due
   to missing pyqt support for pylab.  The conda package manager
   provides sufficient pyqt support.

# 2021-07-05

 - Rename a few of the examples so they sort nicely in UNIX `ls`.
 - Hashes match between github `x86_64` and `aarch64`. Good!
 - Change pytest grid example to match Example 1 for platform
   comparisons (LLC grid tilt 30 degrees).

# 2021-07-04

 - Cause an error if a ROMS gridid.txt file cannot be found.
 - Ocean and land masks did not have a hash created.  Added to meshutils
   functions.
 - FRE-NCtools does not like `GEBCO_2020`.  Will try ETOPO1 and ETOPO2.
 - Change Example3 to Mercator so we can work up an example comparing
   gridtools with FRE-NCtools.
 - Change an information message in the change debug level to avoid confusion.
 - Include platform and python version in software list for saved netCDF files.
 - The warnings for gridResolution parameters do not make sense if
   some are properly defined. Revised.
 - Add to favorite shortcuts to jupyter.
 - Update jupyter MD notes.
 - Fix CI as we changed the source of the requirements file
   in binder which is also used by github Actions.
 - Fix spelling of notebook in bokeh.
 - Update the README.md in examples.
 - RT: Bugs in mkGridIterative notebook.  Refactoring software
   metadata discovery.
 - Packages versions are typically seen only at the root
   element, so optimize on that.

# 2021-07-03

 - Rework sysinfo and utils modules to allow more flexible software
   and detection in different environments.

# 2021-07-02

 - RTD is fixed.
 - Add roms modules to RTD docs.
 - Create release/0.3.0.md to begin a release cycle.
 - Update DEPLOY.md template; includes RTD fix
 - RTD: point environment to `conda/gridTools_export-linux-64-RTD.yml`
 - Remove pip entries and nodejs from `gridTools_export.yml` to
   fix RTD using `gridTools_export-linux-64-RTD.yml`
 - In conda, rename `gridTools_export.yml` to `gridTools_export-linux-64.yml`
 - RTD(dev) is broken; unresolvable nodejs
 - Xarray items have to have consistent dimensions and coordinates work smoothly.
 - In bathyutils, after applying mask to correct ocean points, check the depths
   against the `MINIMUM_DEPTH` for points that need to be capped as well.
 - Update some MOM6 notes about bathymetry and related parameters.

# 2021-07-01

 - Set undefined depth of ocean to -99999.0
 - Refactor codes to use utils.sha256sum()
 - Apply `MASKING_DEPTH` and `MINIMUM_DEPTH` to ocean points in
   bathyutils.applyExistingLandmask() and bathyutils.applyExistingOceanmask().
 - Make sure we write hashes for files created by gridutils.makeSoloMosaic().
 - Create a utility function: utils.sha256sum() for all objects
 - Include variable coord as variables to ignore in gridutils.removeFillValueAttributes()
 - Handle single variables passed to gridutils.removeFillValueAttributes()
 - Change test for data in gridutils.removeFillValueAttributes()
 - Revising mask modification for bathyutils.applyExistingLandmask() and
   bathyutils.applyExistingOceanmask().

# 2021-06-30

 - MOM6 PR#1428 `MASKING_DEPTH` may be unspecified or shallower than `MINIMUM_DEPTH`.
 - Allow modification of a MOM6 grid.
 - Now need to work on save and application of edited grid.

# 2021-06-29

 - Continue configuration of jupyter mask editer.
 - Integration of ROMS grids into openGrid/readGrid infrastructure.
 - Rename variable `PYROMS_GRIDID_FILE` to `ROMS_GRIDID_FILE`.
 - Move to more generic keywarg arguments to openDataset, openGrid and readGrid.

# 2021-06-28

 - Add controls to jupyter mask editor
 - Jupyter mask editor is now wrapped in a class
 - create two more classes in gridtools: maskEditor() and maskEditorPylab()
 - Performing integration of mask editors into gridtools.
 - Before use of pylab class in jupyter, a user must have a cell
   that calls `%pylab` first.
 - fix typo in example for gridutils.plotGrid()

# 2021-06-27

 - map() does not work well with numpy/xarray
 - pyplot will require a rewrite to optimize speed; the full map is rendered and
   underlying data is changed and requested to redraw on update.
 - need to add a control to jupyter editor to enable/disable mask edits but still
   allow moving the subgrid on each click.

# 2021-06-26

 - Working on trying to get jupyter and pyplot displays to be more similar to
   each other.

# 2021-06-25

 - Added an adaptive method to the mask editor.  User can specify size of
   grid subset.  Subset grid is centered over the last mouse click.
 - Mask value is toggled between 1 and 0.
 - With 2D lon, lat grids we have to resort to a great circle calcuation
   of all the points to find our clicked grid point.  This computation is
   fast.  The rendering of many points is slow.
 - Make sure to reset the kernel and wipe out any cells on notebooks to
   keep the repository size down.

# 2021-06-24

 - Experimenting with hvplot quadmesh.  With a large grid, it takes a long time.
   May want to consider partitioning the grid for plotting?  Sliding views?
 - Add note to README
 - Additional package requirements: geoviews, hvplot, nodejs, pooch, owslib
 - May be able to use jupyter for the editor
 - Return references to the created plot object or the event
   hooks go away.
 - The coordinate system is a little different in cartopy.  Found
   a reference that helped fix the issue.

# 2021-06-23

 - Copied needed modules from pyroms and made some modifications
 - Added new modules to `__init__` for grids module
 - Added (object) to all current classes
 - Starting ipython and pasting code from mkGridsExample9 will launch a window
 - editing only works via `ipython --pylab`
 - a plot shows up but the transformations are off
 - investigating replacement for Basemap() for conversion of (lon, lat) to (x, y)
 - branch exp/maskeditorV1 opened
 - consolidate credits and citations
 - fix more main README.md links
 - Updated pyroms install information for the brave
 - bibtex authors are separated by and and not commas
 - Add citation for pyroms

# 2021-06-22

 - PR#8 submitted to main.  Making final checks of CI, RTD and mybinder.

# 2021-06-21

 - Add more environment infomation
 - Show stdout for pytests (-rA)
 - Add dev and main branches for CI testing
 - Add a pytest to show some initial hashes to check in CI output
 - Add reference for numpypi.  Need to add URL to original and latestURL if updates were made.
 - Updated workaround information dropping datashader and updating xesmf information.
 - Add `source/_static` and `source/_templates` to repo as they are needed for sphinx.
 - Pinned git repo version for datashader no longer needed
 - `pdb.set_trace()` can be replaced with `breakpoint()` and the import pdb is no longer needed.
 - BUG: RTD: bullet items not rendered, use "conda install docutils=0.16"
 - Verified python script examples are still operational.
 - Updated some documentation in the sanity module.
 - Add reference to `gridutils.generate_regional_spherical_meters()`

# 2021-06-20

 - Add keyword arguments to GridUtils.plotGrid() for control over plotting
   elements.
 - Add dpi control to GridUtils.newFigure() and add 100.0 dpi to defaults.
 - Bump __version__ to 0.2.0
 - Jupyter notebooks pass initial testing towards release 0.2.0
 - Jupyter notebooks require: %matplotlib inline for showing figures
 - Fix code fetching __version__ tag
 - reformat TODOs to shorter columns
 - sysinfo: needed some self prefixes on a few objects
 - sysinfo: stdout/stderr needed to be decoded() from bytes
 - sysinfo: fix capture of returncode
 - Add a common wrkDir and inputDir for examples to easier set paths to files, etc.
 - Add default tileName of `tile1` to examples.
 - Replace temporary `package_versions.txt` placeholder.
 - Begin running tests to work on Release 0.2.0
 - Fix dpi at a default value (100.0).  It can magically change between Figure() calls.
 - xarray plot wants coordinate variables.  For MOM6, add `x` and `y`
   to coordinates before plotting.
 - xarray tutorial data requires python module pooch
 - Create mkGridsExample7a notebook to experiment with xarray plotting methods.

# 2021-06-19

 - Add generic plotting demonstration to Example 7.  Will add more options
   in later releases.  Not quite working yet.
 - Add sanity module to documentation.
 - New goals and milestones defined.  Older milestones archived.
 - Add `**kwargs` access to `convert_ROMS_to_MOM6` function.
 - ROMS2MOM6: Mask depths to `MASKING_DEPTH` instead of a hard coded zero(0).
   Use xarray instead of numpy.
 - Deployment plan firming up for generic plotting.
 - Add default tileName to example 7.
 - Update documentation about file specifications.
 - Basic testing has increased confidence code that grid generation
   and conversion is somewhat operational.
 - NOTE: **kwargs is not updatable within function calls
 - Update utils routine to use generic command callout function to fix extranious
   warnings to be output when a git repo may not be present.
 - Conversion routine ROMS_to_MOM6 did not update the kwargs topographyGrid which is
   used later when writing out the topography and masking files.
 - Add a sanity check module instead of repeating code.
 - Add `*_DEPTH` specified options to metadata for topography and masking files.
 - Restructure plotGrid to enable plotting of model grid or other variables.

# 2021-06-18

 - conda export environments should not include special pip packages
 - Remove pip definitions from binder/environment.yml
 - Document build failing: adding sphinxcontrib.bibtex
 - Indexing across xarray and numpy is hard; need to move
   more numpy items toward xarray.
 - Add makeSoloMosaic to 20x30 test grid Example7
 - Rename LandMask to Landmask
 - Rename OceanMask to Oceanmask

# 2021-06-17

 - Adopt use of colorama for optional coloring of text output
 - Debug gridtools.grids.mom6
 - Debug gridtools.grids.roms
 - Fixes for at least when git commands fail attempting to grab
   git related information.

# 2021-06-16

 - Initial coding of ROMS to MOM6 converter and writing out a solo
   mosaic for a new grid is complete.  Now to begin testing.
 - Reformat keyword arguments.
 - MOM6 default tileName = tile1
 - Add grid geometry type to tile variable: cartesian or spherical
 - Add proper string encoding to gridutils.removeFillValueAttributes.
 - Continue adding routines to mom6 and roms modules.

# 2021-06-15

 - Replace {} with dict()
 - Porting of ROMS to MOM6 grids will go hand in hand with general
   solo mosaic creation routines.
 - Created ROMS and MOM6 specific classes for dealing with their own grids
 - Add sphinxcontrib-bibtex to requirements.txt file to see if we fix RTD build failure
 - Add reference to FRE-nctools.
 - Add a generic utils module for generic functions.
 - gridutils.readGrid() does not need to do anything but note the grid type
   in gridInfo['type'].
 - urllib.parse: double slash denotes the next argument is a network
   specification.  We can use file:/filename for absolute and relative paths.
   We need to rework documentation so we can specify data sources more explicitly.
   These are equivalent (ds:/GEBCO_2020) = (ds:///GEBCO_2020).  A relative
   path would be ds:GEBCO_2020.  It would be an implementation decision
   if ds:/GEBCO_2020 == ds:GEBCO_2020.
 - Simplify Example 8 a little bit with file spec discovery.

# 2021-06-14

 - Add remaining modules to RTD documentation.
 - RTD docstrings: https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
 - Fix all the current documentation warnings.
 - Fix some latex math.  Use double slash in math expressions.
 - Add sysinfo.runCommand() to consolidate the ability to capture
   output from running commands from the library.
 - sysinfo.sysInfo() class has a grd= argument that allows connecting
   the logging portion of the library.
 - Ongoing expansion of documentation.
 - Add bibtex to sphinx documentation process.
 - bibliography.rst: Sample entry for a paper and a github repo.

# 2021-06-13

 - computeGridMetrics comes in two forms: spherical and cartesian.
 - Begin construction of makeSoloMosaic that does similar work to
   `make_solo_mosaic`.
 - Attempts to build FRE-nctools on chinook have failed so far.

# 2021-06-12

 - Numpy has a method to access the indexes that match grid points
   for any value test.

# 2021-06-11

 - BUG: Relative paths do not work in the new filespec scheme.
 - Remove old Documentation.md file.
 - Do not install the binary TeX environment or the glibc anywhere near the
   conda gridTools environment.  The environment became tainted and began
   to segfault.  Only activate TeX when a PDF is needed.
 - Markdown file processing is problematic.  A module m2r2 needs some work to
   do things the way we want. Leaving it disabled for now.
 - Add configuration file for ReadtheDocs site
 - Fix Example8 to set periodic=False
 - Initial sphinx setup is complete; need to test linkage to ReadTheDocs.
 - Adding Documentation.md to docs/development.
 - Sphinx requires a fully operational software stack to generate documentation.
 - Adding sphinx/doxygen to documentation proceedures.  The documentation
   will utilize a separate enviornmnet to keep things simple.

# 2021-06-10

 - More TODOs.
 - Added Example8 to demonstrate construction of depth/ocean mask grid
   through gridtools library with new topoutils regridding method.
 - Fix masking names for Example7.  ROMS to MOM6 calls the masking fields
   `mask`.  If they are in the same file, we will have to put a prefix
   on the field.
 - Initial construction of topoutils.TopoUtils.regridTopo() is done.  Needs
   testing.
 - Found a way to get the prior function caller to assist debugging.  It
   introduces a performance hit so we need to be careful about turning it
   on.
 - Log an ERROR if we fail to evaluate any fields for a data source.
 - Add a note about using ... in python. Cute!
 - Rework Example7 with a common work directory.
 - Adding contribution from James to topoutils.py.
 - Bug in xesmf requires temporary reference to a git repo.
 - Be sure to rehash the new 'depth' field in bathyutils.applyExistingLandMask()
 - Add a MOM6 message indicating diagnosed maximum ocean depth.
 - gridtools.openDataset() can now open a catalog data source or file or
   OpenDAP end point.  Completely rewrote this routine again.
 - Adopt prefixes for file specs.  See doc/development/Filespec.md  No
   filespec prefix is assumed to be filenames.  Things should work
   if regular filenames are used.  The only thing that will break is
   the data source catalog references.  A / must be prefixed on the
   entries.  We can do a soft ignore in the future to allow plain
   names to work too.
 - Add a fileutils library for generic gridtools operations that are
   not field or grid based.
 - Allow chunks option to be passed for grid and data sources.
 - openGrid now uses openDataset again

# 2021-06-09

 - Implement saving of ocean and land masks using a specified
   `MASKING_DEPTH`.
 - Adding bathyutils.applyExistingLandMask()
 - There is a better way to use complex expressions in
   xarray.where().  Bookmark to gist added to important information.
 - Add various TODOs.
 - Example 7 works.  It should be cleaned up and Example 7a should be
   created to demonstrate using existing files created by Example 7.
 - gridutils.removeFillValueAttributes() add a data= parameter to
   allow use outside of grids.
 - gridutils: Add more comments to allow searching of large sections of code
 - Add meshutils for generic routines that we do not really have a good place
   for at the moment.  The first routines are writing a land and ocean mask
   file based on a supplied field.

# 2021-06-08

 - Integration of bathymetric roughness to allow for internal tide
   parameterization to be used in a model run.
 - Add a data catalogging system in the grid tools library.  The
   catalog system can point to physical files or remote files.
 - Move generic dataset operations into data source operations
 - Keep grid operations separate from data source operations
 - openDataset() for grids is now openGrid() followed by readGrid()
 - We should keep better track of assembled code to reduce hours of
   rediscovery should we to totally rewrite this library.
 - Add a hook to enable passing a chunks argument to `open_dataset()`
   for grids and data sources.
 - Implement applying an existing land mask after getting the roughness
   field instead of being combined with this function.
 - Plotting of created fields will be done separately.
 - Application of the ice9 algorithm will also be done separately.
 - `MASKING_DEPTH` defines the land mask for MOM6.  All depths shallower
   than `MINIMUM_DEPTH` but deeper than `MASKING_DEPTH` are rounded to
   `MINIMUM_DEPTH`.  When the FMS coupler is involved, a separate land
   mask is stored in the exchange grids.
 - TODO: Create several routines for checking/updating masks.
 - Collecting lots of TODOs for bathymetric roughness code.
 - Using chunks with eval works but is not numpy fancy indexable.
 - Delay evaluation of depth until the end to support chunks.
 - variableMap will remap variables; evalMap will perform calculations
   after the fact.  In our example, elevation was remapped to the needed
   depth variable for input, then we invert the sign after processing.
 - Add LICENSE.md similar to MOM6
 - Noted quirk for xesmf

# 2021-06-03

 - Release 0.1.1
   - Installation and tutorial (PR#3)
   - Start use of github action workflows
   - Start implementation of some pytests
   - Add CONTRIBUTING.md stub
   - Update main README.md
   - Gridtools library is now installable via pip
   - Move all mybinder.org materials into a binder directory
   - Add the quiet flag to postBuild pip install
   - Add `gridTools_explicit_linux-aarch64.txt` for use with conda on Raspberry Pi
   - Remove mkGridInteractive.ipynb from root tree
   - Move tutorials into doc folder and update README.md to link to them
   - Update tutorial links so they will work after publication to main branch
 - Update todos

# 2021-05-30

 - Consolidate requirements lists again
 - github CI: use quiet mode for conda and pip to make output less verbose
 - We have a complete python venv build for UAF:chinook cluster
 - numba requires a modern compiler
 - A couple of dependencies require openssl: nodejs particularly
 - libtiff is required by proj
 - Do not use python setup.py: this is a legacy installation method

# 2021-05-28

 - The answer is use python -m pip; do not use python setup.py
 - Revamped requirements for possibly a two stage install for pip?
 - python setup.py develop mostly works; still some workarounds needed
 - Providing install info for specific compute clusters: python3 -m venv on UAF:chinook
 - Fixes for: python -m pip install .
 - Add numba to gridTools conda environment and removed as TBB was old on UAF:chinook due to ancient compiler
 - Add other dependencies: dask, colorcet and datashape
 - Add a hack for supporting differences in package requirements for pip vs. setup.py

# 2021-05-26

 - Fix remote saving to correct directory as shown in the application
 - Improve gridtools metadata output; add hashes to certain variables
 - For pip installs, if jupyterlab<3.0.0 is required, require: jupyter labextension install @pyviz/jupyterlab_pyviz
 - In gridutils, self.app was overwriting the app() function; changed to self.applicationObj
 - Add a couple more try blocks on a machine without conda
 - Add example #7 demonstrating grid generation of bathymetric roughness(h2)
   and other bathymetric or other general field options.
 - Add hashlib to gridutils
 - Add package requirements to setup.py and requirements.txt
 - Begin construction of topoutils.py based on ocean_model_topog_generator
 - Begin construction of datasource.py that will manage data sources

# 2021-05-20

 - Add netCDF4 to gridTools.yml base packages; xarray needs it to read netcdf version 4 files
 - Add a few informational links
 - Update to push exp/bathyV1

# 2021-05-18

 - Add info on running dask in a cluster environment
 - Delete duplicate conda/docs directory; not sure how that got there
 - Create exp/bathyV1 branch
 - Merge https://github.com/ESMG/gridtools/pull/1
 - Finish out documentation updates for PR#1

# 2021-05-17

 - Merge updates (PR#2)
   - Add netcdf metadata: grid\*, conda\_env, package\_versions and software\_version.
 - Redefining gridTools.yml.  Attempting to combine panel, xesmf and xgcm packages.
   - Currently defined gridTools loads xesmf(0.5.3) and xgcm(0.5.1) for x86\_64.
 - Indicate some pitfalls in maintaining exported configurations for conda
 - Resync binder/environment.yml with conda/gridTools\_export.yml

# 2021-05-15

 - Aggregate mybinder.org into its binder directory to further clean up the repository
 - Add numpypi to setup.py for automatic installation
 - Update binder to only install gridtools(+datashader+numpypi)

# 2021-05-14

 - Delete conda/xesmfTest.yml; this used for testing a conda install environment for the reworked repo
 - Start on continuous integration (CI) and testing of repo code to help check for inadvertant bugs
 - Add a contributing stub.
 - Modify initial workflow to do some basic sluthing.
 - Pare down gridTools environment
 - Remove netCDF4 module from app.py since we have xarray
 - Add pytest and some tests; try in CI
 - Update conda README with update instructions with explicit
 - Found key to getting conda environment working
 - Each step needs conda activate
 - Update pytest tests with expected failures
 - Add gridtool module import tests
 - Add a couple more tests (incomplete)

# 2021-05-13

 - Add datashader dependency to setup.py
 - Remove duplicate logging example
 - Update examples to use refactored installable library
 - Update mybinder.org to see if that still works with refactored library
 - Refactored library: from gridutils import GridUtils becomes from gridtools.gridutils import GridUtils, etc
 - Add .swp to .gitignore
 - Move installable library to 0.2 milestones
 - Remove LIBROOT dependency for library
 - setup.py installs the datashader requirement
 - Update documentation for installation and use
 - Fix mybinder.org detection in application
 - Fix mybinder.org installation paths

# 2021-05-11

 - Finish out 0.1 milestones
 - Add more TODOs including reproducibility goals
 - Create a exp/pipInstaller branch for testing
 - Refactor repo (again) to support pip install of library
 - Copied a versioning method from the sphinx project
 - Removed warning handling
 - Removed xgcm from app.py (not sure why it was working either)
 - Had to change how gridutils.py imports packages at its own level to enable from gridtools import * to work
 - Add a pyproject.toml file template; had to delete build-backend for pip install -e . to work
 - Modify setuptools import to model that of the sphinx setup.py
 - Refactoring likely broke a lot of stuff...have to check

# 2021-05-10

 - Establish 0.2 milestones

# 2021-05-06

 - BUG(app): Stereographic grid generation does not work when dx/dy is not
   evenly divisible by grid resolution. TODO
 - IBCAO grid exhausts memory on mybinder.org
   - Try to implement dask features in Example4a (incomplete)
 - Updated grid center text in application
 - Rename an example script to conform to mkGrids
 - Remove mkMapInteractive.ipynb
 - Fix metadata for IBCAO grid in Example 5 and 5a
 - Add jupyter-resource-usage to conda:xesmfTools
 - BUG(app): Add missing self on plotTitle FIXED
 - Add information to examples/README.md
 - BUG(app): x/y color and line controls are swapped FIXED
 - app: adjusted grid resolution to take larger numbers.
 - app: erase debug cell at the bottom of mkGridInteractive.ipynb
 - publish to ESMG:dev branch and test mybinder.org

# 2021-05-05

 - This day in history.  SpaceX launches and lands starship prototype number 15.
 - Add wish list task for delta method import of boundary conditions and forcing fields.
 - Add/update documentation for the application.

# 2021-05-04

 - Merge PR#1 into robTest
   - Provide user with more descriptive plotting failure whether it is due to a non-existent grid or really a plotting error.
   - Add errorNoGridFigure().
   - Move coordinates of existing message on plot.
   - Add self.gridMode flag to GridUtils()
   - Upon use of saveGrid() adjust x in grids from 0,360 to -180,+180

 - Still some rough edges to clean up.
   - One more pass at the application and application documentation
 - Application changes:
   - Adjust projection parameters depending on selected projection in make_plot and make_grid
   - allow projection center to be separate from grid center
   - define more controls for plot and grid to match recent API changes to GridUtils
   - Ellipsoid for grids and plotting set to WGS84
   - Add a grid "Center" tab
   - Expand ranges of dx, dy, gridResolutionX and gridResolutionY to also support meters

# 2021-05-03

 - WARNING: This commit leaves the Application broken (temporarily).
 - API CHANGES
   - Created grid generation function for spherical units given in meters and degrees.
 - Add warning when grid generation fails.
 - Add informational message when grid metrics are not computed.
 - Check for lat_0 of +90 or -90 for spherical projection plots.
 - Example mkGridsExample4.ipynb complete
 - Checked operation of mkGridsExample1.py
 - Checked operation of mkGridsExample5.py and mkGridsExample5a.py
 - Issue a warning for grids that might not be conformal.
 - Update app:make_plot for various projection inputs
 - Remove an unneeded string expansion for Mercator.

# 2021-05-02

 - API CHANGES
   - Performing parameter checks upfront and converting some to float for use later.
   - Update mercator with Niki's routine to allow users to specify tilt.
   - Define _default_availableGridTypes
   - Add ensureEvenI flag for MOM6 grids
 - Whitespace cleanup
 - Begin to leverage args and kwargs in python functions.  This will allow us to
   use developed math functions for use with other grid types that might require
   different options.
 - Adding code guards for MOM6 specific operations.

# 2021-05-01

 - Move generic API demonstrations into mkGridsExample2.py so it
   does not detract from specific grid generation demonstrations
   in mkGridsIterative.ipynb.
 - API CHANGES (incomplete)
   - Enforce grid center parameters: centerX, centerY, centerUnits.
 - mkGridsInterative.ipynb (incomplete)
   - Add Niki's example of a Stereographic grid
   - Add Niki's example of a rotated Mercator grid
 - Added more of Niki's functions for Mercator grid generation
 - NOTE: Grid generation techniques sometimes require projection
   information and sometimes grid generation techniques change
   projection information.  All details should be specifically
   documented.

# 2021-04-30

 - API CHANGES
   - gridResolution is now units based instead of scale based as Niki defined it in his notebook example.
 - gridutils
   - Enforce degrees as units for Mercator and Lambert Conformal Conic.
   - TODO: Niki performs some clipping of points along the j direction.  This should be an expanded feature
     to warn the user about grids with odd number of points in the i and j direction and offer an expansion
     or clipping method.  For supercomputing, it is easier to decompose a grid with even amounts of
     points.
   - Plotting: follow proj convention, when lat_ts is missing, attempt to use lat_0.
   - Plottind defaults: follow proj defaults.
   - drop "+units" from Mercator proj string
   - add lat_ts to Stereographic proj string if available
   - fix proj string bug for Lambert Conformal Conic
   - Allow users to set the verbose Level by name instead of by number
   - makeGrid() refactoring: use a flag to track when a new grid is created and then compute
     grid metrics after attempting to establish a proj string.  Creating a proj string too
     early did not work for the delayed information from the Lambert Conformal Conic grid.  Now
     we compute the proj string at the latest possible moment.  This would break the Spherical
     grid generator for units in meters.  This routine will have to construct the proj string early.
   - Build out of Spherical grid generator begins (not complete)

# 2021-04-29

 - Unify user manual.  The user manual will hold the bulk of the operational details.  Application details
   will be a small subset enough to explain the operational details of the graphical user interface.
 - Merge NorthPolarStero and SouthPolarStereo to Sterographic in which grid generation will
   need to pay attention to lat_0 defined for the projection.
 - Update application to merge North and South polar stereographic to Stereographic.
 - TODO: grab github revision used by each specific mybinder.org instance
 - User can specify ellipsoid (ellps) and earth radius (R) through projection options to grid and plot.
 - Do not forecast milestones past the next logical one; put other major milestones into a generic X milestone.
 - We assume the user is familiar with the python programming language.  We will point the user to helpful
   materials when appropriate.
 - API CHANGES
   - Implementation requires vetting application and examples for proper operation
   - Change user specification of grid center to "centerX" and "centerY" and specify those units in "centerUnits".
 - BUG: Updating grid or plot parameter nested arguments will get clobbered.  Queued to be fixed later.

# 2021-04-28

 - Raphael pointed us code he wrote that allows conversion from XY to LATLON over a 2D field.  It was
   exactly what we needed to get the IBCAO grid working in the polar projection.
 - Unify MOM6/proj defaults for grid generation
   - Default radius is 6.378137e6
   - Default ellipse is GRS80
 - Add warnings to various areas where we create the projection string
 - Add warnings to determiniation of the radius of the earth to use
 - Add three examples on how to create the IBCAO grid.  One example shows how
   things change when a slightly different radius is specified for WGS84.
 - Move some milestones around with polar grids now possibly working
 - Keep milestones under 1.0 for now
 - Add datetime and pyproj to gridutils imports
 - Return a version number for gridutils library
 - Better metadata for xarray/netCDF structures
 - Determine earth radius based on projection string on the fly
 - Move construction of proj string into a function so it will work for grid and
   plot projections as needed
 - TODO: improve documentation for grid and plot parameters and finish implementation work
   for all projections.  For now, keep the grid construction simplified.
 - Added a plotting demo for illustrating unstructured grid interpolation and differences
   between using grid edges and grid center points for plotting.

# 2021-04-26

 - Avoid use of xesmf 0.5.2
   - split xesmfTools environment and move xgcm into its own environment
 - Add xgcmTools environment
 - Remapping an ice field using xesmf regridder
 - Begin rework field flood algorythm that pyroms utilizes
 - Added more bookmarks and sorted them
 - Added xesmf to pangeo environment
 - app.py; gridtools.py updates
   - Add appropriate spacing between items
   - If tilt is zero, remove it from any message or title
   - Split refine into two arguments
   - Update message if regular lat lon grid is being built on the equator or not
 - Move plotBathyArctic6.py into pyroms directory

# 2021-04-22

 - The supergrid plotting would fail if grid type was two(2) and resolution was 0.5.  When
   multiplied together, it results in 1.0 which confused the current system.
 - Add simple mercator grid generation method
 - Add a couple of bathy examples to debug a masking issue.  We can use xarray to display a
   GEBCO 2020 figure and a ROMS figure with bathymetry.
 - Add xmap examples that almost work
 - Fix some spacing in some gridutils functions
 - Update metadata for NEP7 grid in README
 - Disable mercator tilt
 - Separate refine inputs to grid functions that use gridResolution and gridMode
 - Update some messaging

# 2021-04-10

 - Shore up messaging and debugging code in GridUtils().  A lot of missing level= in 2nd arguments
   calls to printMsg and debugMsg.
 - Add a TODO to refactor messaging and debugging into its own package/module.
 - Add an example on how to work with logging levels and debug levels.
 - Add showPlotParameters function.
 - Add more explanation to example1.
 - Testing NSIDC's grid generation software: mapx
   - https://github.com/nsidc/mapx
 - Learn how to read binary and reshape a numpy array after reading a mapx binary grid file
 - FIX: GridUtils: Reformat lon > 180 
 - lcc_grid.gpd almost replicates Niki's example grid; degress vs meters
 - Create a 3rd example that generates a 1x1 grid for testing

# 2021-04-09

 - Fix warning in GridUtils.plotGrid()
 - Change warnings to logging.WARNING messages
 - Moved all print statements to printMsg calls
 - Fix printing to STDOUT when msgBox is not defined
 - Add a function that allows tweaking of noisy python modules that send information to the log.
 - Add Manual documentation
 - Add application Setup tab for other obscure toolset options; add setter and getter methods in GridUtils()
   - Use numpypi: True/False
   - Enable logging: True/False
   - Specify logfile: "filename"
   - Specify logging level
   - Specify verbose level
   - Specify debug level
   - Log erase button
 - Update some important references
 - We can add param.watch to any control to trigger events when certain things happen.
 - We also learned that a lot of python modules leverage the logging module and that some of
   those modules are very verbose.  We setup a function to reduce some of that noise.
 - Once a logger is created, it cannot be deleted.  It can be enabled and disabled.
 - Add a small program example to show all available loggers after a GridUtils object is created.
 - TODO: Creating more small program examples to demonstrate logging and debugging techniques.
 - Use the setter functions in mkGridScripts and examples instead of setting the object variables directly.
   - TODO: consider moving important variables to private/hidden variables.

# 2021-04-08

 - Experimentation with panel.pane.HTML did not work pan out.  No great control over width and height.
   Text updates did not automatically resize the window.  The TextAreaInput automatically adds a
   scrollbar to the box when enough lines are added to the window.
 - Fixed up documentation of Grid Representation in the app manual.
 - Panel markdown honors the usage of options after a link. 
   Ex: [MOM6 User Manual](https://mom6.readthedocs.io/){target="\_blank"}
 - Testing of new printMsg facility is working.
 - Added a clear information button to clear the inforamtion window.

# 2021-04-07

 - Move Spherical.py to spherical.py to match coding standards
 - Use R from GridUtils class in spherical

# 2021-04-03

 - BUG: add ccrs.SouthPolarStereo() to projCarto
 - Remove plotExtentX0,X1 checks for lon>180
 - Moving the boilerplate into its own module works
 - BUG(migration): makeGrid() contained a small bug, parallels were not updating; missing self
 - reworked the way we start the app via show() and display()
 - BUG(migration): Plot button stopped working; missing self 
 - BUG(migration): Saving local files are fixed
 - BUG(migration): Call the showManual method with ()

# 2021-04-02

 - combined xgcmTools with xecmfTools configuration
 - added nbserverproxy to xecmfTools
 - moved documentation around
 - merge code updates from James
   - proj; applied application changes into gridutils so it is available to all
   - applied widget clean up for local file selection
 - add todos: LCC limitations; consider numpypi code
 - initial move to hide application boilerplate; help diff/debugging
 - discovered how to suppress xarray \_FillValue attributes
 - created mkGridScripts.py to demonstrate command line/ipython use
 - more documentation needed
 - document how numpypi and datashader should be installed
 - update extent display to show -180 to +180
 - most spinner widgets updated to numeric values instead of integer
 - establish a global for the defaultGridFilename
 - still need to understand how libraries, modules and packages are handled in python
 - migration of mkMap to mkGrid filename; we started with maps but have moved onto grids

