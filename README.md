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

## Step 2

[Download](https://github.com/ESMG/gridtools/archive/refs/heads/main.zip)
or [clone](https://github.com/ESMG/gridtools.git) the
[ESMG/gridtools](https://github.com/ESMG/gridtools) repository.

The `python setup.py install` method is now considered a legacy installation
method.  Please use the `python -m pip install` method.

### pip

```
$ cd gridtools
$ python -m pip install .
```

# Workarounds

These are the current workarounds that are required for the grid
toolset package.  You may need to perform these steps once if you
plan to install a copy of the grid generation software.

NOTE: These workarounds should be automatically installed with
an installation of gridtools.

## datashader

The lastest version from github is required for proper operation of
bokeh, holoviews and panel which are used by the interactive portions
of the grid generation library.

[REPO](https://github.com/holoviz/datashader)

Installation:
  * Download or clone this repository.
  * Change directory to the datashader directory.
  * Make sure your conda enviroment is active.
  * `pip install -e .`

NOTE: The datashader library should be automatically installed as a
dependency of gridtools.

## numpypi

Portable intrinsics for numpy ([REPO](https://github.com/adcroft/numpypi)).
For bitwise-the-same reproducable results, a numpy subset of computational functions are
provided.  These routines are slower than the numpy native routines.
A repackaged installable [REPO](https://github.com/jr3cermak/numpypi/tree/dev) of the library.

# Code contributions

## Lambert Conformal Conic Grid Generation
Author: Niki Zadeh [REPO](https://github.com/nikizadehgfdl/grid_generation)
 * [regional_grid_spheical.ipynb](https://github.com/nikizadehgfdl/grid_generation/blob/dev/jupynotebooks/regional_grid_spherical.ipynb)

## Portable intrinsics for numpy
Author: Alistair Adcroft [REPO](https://github.com/adcroft/numpypi)
 * To obtain bitwise-the-same floating-point values in certain non-time-critical calculations.

## ROMS to MOM6 Grid Converter
Authors: Mehmet Ilicak; Alistair Adcroft [REPO](https://github.com/ESMG/pyroms)
 * [convert_ROMS_grid_to_MOM6.py](https://raw.githubusercontent.com/ESMG/pyroms/python3/examples/grid_MOM6/convert_ROMS_grid_to_MOM6.py)

# More

Until we can activate Sphinx to create our body of documentation we will have to resort
to upkeep of a manual index.

[Documentation](docs/Documentation.md)
  * [conda](docs/conda/README.md)
  * [development](docs/development)
    * [CHANGELOG](docs/development/CHANGELOG.md): Development log of changes
    * [CREDITS](docs/development/CREDITS.md)
    * [DEPLOY](docs/development/DEPLOY.md)
    * [Design](docs/development/Design.md): Design elements for the grid generation library
    * [Important References](docs/development/ImportantReferences.md): Things that helped this project work
    * [Jupyter](docs/development/Jupyter.md): Notes on embeddeding applications within a notebook
    * [python](docs/development/python)
      * [leaflet](docs/development/python/leaflet.md)
      * [panel](docs/development/python/panel.md)
      * [pyroms](docs/development/python/pyroms.md)
    * [TODO](docs/development/TODO.md): Milestones, tasks, todos and wishes
  * [grids](docs/grids)
    * [Examples](docs/grids/Examples.md): Descriptions of grids used in examples
    * [Grids](docs/grids/Grids.md)
    * [MOM6](docs/grids/MOM6.md): MOM6 grids
    * [MOM6ROMS](docs/grids/MOM6ROMS.md): Important things between MOM6 and ROMS grids
    * [ROMS](docs/grids/ROMS.md): ROMS grids
  * [manual](docs/manual/GridUtils.md): User manual for the GridUtils library
    * [Installation tutorial](docs/manual/local_installation_tutorial.ipynb)
    * [Gridtools application tutorial](docs/manual/gridtoolAppTutorial.ipynb)
  * [resources](docs/resources)
    * [Bathymetry](docs/resources/Bathymetry)

# Development

This project is soliciting help in development.  Please contribute
ideas or bug requests using the issues tab.  Code contributions can
be sent via github's pull request process.  Code adoption will follow
the [contribution](CONTRIBUTING.md) process.
