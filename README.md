# gridtools

A generic set of grid manipulation tools for computer models.  These tools are
adapted from the ROMS ocean model and for specific use in the MOM6 ocean model.
One could hope it can be kept generic enough to support any model.  The focus
is on supporting the MOM6 ocean model.

For in depth details about the MOM6 ocean model, please visit provided
[wiki](https://github.com/NOAA-GFDL/MOM6-examples/wiki) pages.  Technical
details about this repository can be found below.  For usage of
the GridUtils library, please visit the [user manual](docs/manual/GridUtils.md).

Various examples are available to demonstrate manipulation of new and existing
grids in an iterative or interactive (application) form.

Python notebooks:
 * [mkGridIterative.ipynb](examples/mkGridIterative.ipynb)
 * [mkGridInteractive.ipynb](examples/mkGridInteractive.ipynb)
   * The [gridtools application tutorial](docs/manual/gridtoolAppTutorial.ipynb)

Python scripts:
 * [examples](examples)

# Operational Modes

## Command Line

Using the command line or writing your own python scripts is also
possible utilizing this library.  Please see the python scripts
in the [examples](examples) folder.

## Command Line Widget Mode

 * ipython --pylab

The interpreter, ipython, can run python scripts and notebook scripts.
To run a notebook script, you can use
`ipython -c "%run your_script.ipynb"`.  Or start ipython, and then
`%run your_script.ipynb`.

The [example](examples) python scripts can also be run with ipython.

## Jupyter notebook

 * jupyter notebook
 
These prefer notebook files (ipynb).  Please see the
mkGridIterative.ipynb notebook for a hands on way to access the grid
generation library.

A simple graphical user interface (GUI) was built and is available using the
mkGridInteractive.ipynb notebook.

## Jupyter lab

 * jupyter lab

These prefer notebook files (ipynb).  Please see the
mkGridIterative.ipynb notebook for a hands on way to access the grid
generation library.  Jupyter lab also provides a command console
for running python scripts.

## Application

The grid generation application, mkGridInteractive.ipynb, can be run
using jupyter on a cloud hosting system.

### mybinder.org

 * Main: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ESMG/gridtools/main)
 * Dev: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ESMG/gridtools/dev)

NOTE: This is provided as a point of demonstration.  These cloud
system instances do not persist for a long period of time and should
not be used in production.  Any information created on these systems
should be backed up as soon as possible.

The form at mybinder.org can be manually filled out instead of useing the links
above:
 * GitHub=https://github.com/ESMG/gridtools
 * Git ref=main
 * Launch
 * Once the server loads, navigate to gridTools/mkMapInteractive.ipynb
 * Re-run all the cells
 * Have fun with the grid editor.

# Installation

If you plan to use the grid generation software on your system, you
need to peform the following steps or follow the
[local installation tutorial](docs/manual/local_installation_tutorial.ipynb).

## Step 1

Install conda or manually install the python libraries and software
dependencies that would allow you to run the python scripts or notebooks.

We have pulled together some pre-defined environments.  You may also
install an environment yourself.   Please review the
[conda](docs/conda/README.md) page for more information about conda.

We currently recommend the *gridTools* environment for use with this
library.

NOTE: If **conda** cannot be used,
a list of [required software](docs/development/Requirements.md) is
provided.  Once software and libraries are installed, the remaining
software should be installable via pip and/or python's virtual
environment (venv).

**WARNING**: If a new enviroment is to be prepared with `conda/gridTools.yml`,
be prepared to wait a VERY LONG TIME for conda to resolve the
environment.  It is highly recommened to load a new environment with
`conda/gridTools_export.yml` or `conda/gridTools_explicit-linux-64.txt`.

## Step 2

[Download](https://github.com/ESMG/gridtools/archive/refs/heads/main.zip)
or [clone](https://github.com/ESMG/gridtools.git) the
[ESMG/gridtools](https://github.com/ESMG/gridtools) repository.

The `python setup.py install` method is now considered a legacy installation
method.  Please use the `python -m pip install .` method.

### pip

```
$ cd gridtools
$ python -m pip install .
```

If using **conda**, only minimal changes will be noted.

# Workarounds

These are the current workarounds that are required for the grid
toolset package.  You may need to perform these steps once if you
plan to install a copy of the grid generation software.

NOTE: These workarounds should be automatically installed with
an installation of gridtools in step 2 using pip.

## nodejs

OPTIONAL: This package is optional.  If not using **conda**, this package
is needed to avoid a warning when starting up jupyter.

```
Could not determine jupyterlab build status without nodejs.
```

## numpypi

Portable intrinsics for numpy ([REPO](https://github.com/adcroft/numpypi)).
For bitwise-the-same reproducable results, a numpy subset of computational functions are
provided.  These routines are slower than the numpy native routines.
A repackaged installable [REPO](https://github.com/jr3cermak/numpypi/tree/dev) of the library.

## xesmf

A slight modification to xesmf is required to fix a periodic boundary
problem when regridding.  Note that conda loads an older version of
xesmf and then pip replaces it with a fixed copy.

Users using **venv**, a working compiled copy of ESMF and ESMPy need to
be installed prior to installing gridutils via pip.

# More

Until we can activate Sphinx to create our body of documentation we will have to resort
to upkeep of a manual index.

Documentation:
  * [conda](docs/conda/README.md)
  * [development](docs/development)
    * [CHANGELOG](docs/development/CHANGELOG.md): Development log of changes
    * [CREDITS](docs/development/CREDITS.md) and citations
    * [Documentation](docs/development/Documentation.md)
    * [DEPLOY](docs/development/DEPLOY.md)
    * [Design](docs/development/Design.md): Design elements for the grid generation library
    * [Important References](docs/development/ImportantReferences.md): Things that helped this project work
    * [Jupyter](docs/development/Jupyter.md): Notes on embeddeding applications within a notebook
    * [python](docs/development/python)
      * [leaflet](docs/development/python/libraries/leaflet.md)
      * [panel](docs/development/python/libraries/panel.md)
      * [pyroms](docs/development/python/libraries/pyroms.md)
      * [xesmf](docs/development/python/libraries/xesmf.md)
    * [TODO](docs/development/TODO.md): Milestones, tasks, todos and wish list items
      * [archive](docs/archive) -- Archive of completed TODOs
      * [releases](docs/releases) -- Release information
  * [grids](docs/grids)
    * [Examples](docs/grids/Examples.md): Descriptions of grids used in examples
    * [Grids](docs/grids/Grids.md)
    * [MOM6](docs/grids/MOM6.md): MOM6 grids
    * [MOM6ROMS](docs/grids/MOM6ROMS.md): Important things between MOM6 and ROMS grids
    * [ROMS](docs/grids/ROMS.md): ROMS grids
  * [manual](docs/manual/GridUtils.md): User manual for the GridUtils library
    * [Installation tutorial](docs/manual/local_installation_tutorial.ipynb)
    * [Gridtools application tutorial](docs/manual/gridtoolAppTutorial.ipynb)
    * API : Gridtools library
      * [stable](https://mom6gridtools.readthedocs.io/en/stable/) -- latest release version
      * [dev](https://mom6gridtools.readthedocs.io/en/dev/) -- follows `dev` branch
      * [latest](https://mom6gridtools.readthedocs.io/en/latest/) -- usually follows an experimental branch
  * [resources](docs/resources)
    * [Bathymetry](docs/resources/Bathymetry.md)

# Development

This project is soliciting help in development.  Please contribute
ideas or bug requests using the issues tab.  Code contributions can
be sent via github's pull request process.  Code adoption will follow
the [contribution](CONTRIBUTING.md) process.  Development can be
discussed in the [MOM6 forum](https://bb.cgd.ucar.edu/cesm/forums/mom6.148/).
