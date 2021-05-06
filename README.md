# gridtools

A generic set of grid manipulation tools for computer models.  These tools are
adapted from the ROMS ocean model and for specific use in the MOM6 ocean model.
One could hope it can be kept generic enough to support any model.  The focus
is on supporting the MOM6 ocean model.

For in depth details about the MOM6 ocean model, please visit provided
[wiki](https://github.com/NOAA-GFDL/MOM6-examples/wiki) pages.  Technical
details about this repository can be found below.  For usage of
the GridUtils library, please visit the [user manual](docs/manual/GridUtils.md).

Required items:
 * spherical.py
 * gridutils.py
 * app.py

Optional items:
 * sysinfo.py

Various tools are available to manipulation of new and existing grids in
an iterative or interactive form.

Python notebooks:
 * mkGridIterative.ipynb
 * mkGridInteractive.ipynb

With this software, you should be able to operate in any mode you prefer.

# Operational Modes

## Command Line

Using the command line or writing your own python scripts possible utilizing this library.
To look at a few examples, please look at the mkGridsExample1.py, mkGridsExample2.py and
mkGridsExample3.py programs.

## Command Line Widget Mode

 * ipython --pylab

The interpreter, ipython, can run python scripts and notebook scripts.  To run a notebook
script, you can use `ipython -c "%run your_script.ipynb"`.  Or start ipython, and then
`%run your_script.ipynb`.

Again, the mkGridsExample.py programs can be run with ipython.

## Jupyter notebook

 * jupyter notebook
 
These prefer notebook files (ipynb).  Please see the mkGridIterative.ipynb program for a hands
on way to access the grid generation library.  

A simple graphical user interface (GUI) was built and is available when you run the
mkGridInteractive.ipynb notebook.

## Jupyter lab

 * jupyter lab

These prefer notebook files (ipynb).  Please see the mkGridIterative.ipynb program for a hands
on way to access the grid generation library.  

A simple graphical user interface (GUI) was built and is available when you run the
mkGridInteractive.ipynb notebook.

## mybinder

 * Main: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ESMG/gridtools/main)
 * Dev: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ESMG/gridtools/dev)

Instead of loading software on your computer, the library and application is hosted on a cloud system.  You do not
have to install anything on your system to use the cloud system's copy of the grid generation library.

# Application

The grid generation application, mkGridInteractive.ipynb, can be run on a cloud hosting system.  The application has been adapted to work on mybinder.org.
NOTICE: The mybinder application can take upwards to 30 minutes to build.

Use the following options:
 * GitHub=https://github.com/ESMG/gridtools
 * Git ref=main
 * Launch
 * Once the server loads, navigate to gridTools/mkMapInteractive.ipynb
 * Re-run all the cells
 * Have fun with the grid editor.

# Code contributions

## Lambert Conformal Conic Grid Generation
Author: Niki Zadeh [REPO](https://github.com/nikizadehgfdl/grid_generation)
 * [regional_grid_spheical.ipynb](https://github.com/nikizadehgfdl/grid_generation/blob/dev/jupynotebooks/regional_grid_spherical.ipynb)

## Numpy bitwise-the-same floating-point values
Author: Alistair Adcroft [REPO](https://github.com/adcroft/numpypi)
 * To obtain bitwise-the-same floating-point values in certain non-time-critical calculations.

## ROMS to MOM6 Grid Converter
Authors: Mehmet Ilicak; Alistair Adcroft [REPO](https://github.com/ESMG/pyroms)
 * [convert_ROMS_grid_to_MOM6.py](https://raw.githubusercontent.com/ESMG/pyroms/python3/examples/grid_MOM6/convert_ROMS_grid_to_MOM6.py)

# Installation

If you plan to use the grid generation software on your system, you need to peform the following steps.

## Step 1

[Download](https://github.com/ESMG/gridtools/archive/refs/heads/main.zip) or [clone](https://github.com/ESMG/gridtools.git) the 
[ESMG/gridtools](https://github.com/ESMG/gridtools) repository.

Discover the full directory path to gridtools/gridTools/lib.   Place the full path in the environment variable `LIBROOT` if you are planning to run
the python notebooks.  If you are going to use the library in your scripts, simply append the full path to `PYTHONPATH`.  In the future, we will enable
installation using ptyhon pip.

## Step 2

Install conda or manually install the python libraries and software dependencies that would allow you to run the python scripts or notebooks.

We have pulled together some pre-defined environments.  You may also install an environment yourself.   Please look at the [conda](docs/conda/README.md)
page for more information about conda.

We currently recommend the *xesmfTools* environment for use with this libaray.

## Step 3

Follow any steps in the "Workarounds" section.

# Workarounds

These are the current workarounds that are required for the grid toolset
package.  You will need to perform these steps once if you plan to install a
copy of the grid generation software.

## datashader

The lastest version from github is required for proper operation of bokeh, holoviews and panel which
are used by the interactive portions of the grid generation library.

[REPO](https://github.com/holoviz/datashader)

Installation:
  * Download or clone this repository.
  * Change directory to the datashader directory.
  * Make sure your conda enviroment is active.
  * `pip install -e .`

## numpypi

NOTE: This has not been fully implemented yet.  Do not worry about this just yet.

For bitwise-the-same reproducable results, a numpy subset of computational functions are
provided.  These routines are slower than the numpy native routines.  
[REPO](https://github.com/adcroft/numpypi)

# More

Until we can activate Sphinx to create our body of documentation we will have to resort
to upkeep of a manual index.

[Documentation](docs/Documentation.md)
  * [conda](docs/conda/README.md)
  * [development](docs/development)
    * [CHANGELOG](docs/development/CHANGELOG.md): Development log of changes
    * [CREDITS](docs/development/CREDITS.md)
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
  * [resources](docs/resources)
    * [Bathymetry](docs/resources/Bathymetry)

# Development

This project is soliciting help in development.  Please contribute ideas or bug requests using the issues tab.
Code contributions can be sent via github's pull request process.
