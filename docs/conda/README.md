# conda

This explains some things about how to utilize conda to
manage python environments.  To learn much more details about
conda, we suggest visiting the
[conda documentation](https://docs.conda.io/projects/conda/en/latest/index.html)
website.

A YAML specification file is to configure a python environment.  We
have prepared a few specification files, please see the conda directory.
The YAML specification file is also platform dependent.  In most cases,
the linux-64 will work.  For older systems, we have provided a YAML
file for an older 64-bit glibc.

These instructions assume you have conda/miniconda installed.  If
conda is not installed, please consult this
[webpage](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

If **conda cannot be used**, please consult the
[required software](../development/Requirements.md) for packages to install.

Several basic YAML files are provided to install an appropriate python
environment.  To expidite the conda environment solver,
a `YAML_export` or `YAML_explicit` file is
also provided for quicker recovery of python environment.

Initialization:
```
$ cat conda/gridTools.yml
$ conda env create -f=conda/gridTools_export-linux-64.yml
$ conda env export > conda/gridTools_export-linux-64.yml
$ conda list --explicit > conda/gridTools_explicit-linux-64.txt
```

NOTE: If you are recreating the package lists (txt) or the
export (yml) file.  Do that before running the pip install
for gridtools.

NOTE: The exported yml file will specify a directory path for
installation.  It is recommended to delete the last line in the
yml file before publication.

NOTE: The explicit package listings will contain a specific OS
platform target (e.g. linux-64) and may not be compatible with
the intended target platform for installation of the library.

For a quicker recovery of a conda environment, use the exported
YAML file:
```
$ conda env remove --name gridTools
$ conda env create -f=conda/gridTools_export-linux-64.yaml
```

NOTE: In some cases, the above may fail.  You then have two options.
(1) Use the generic `gridTools.yml` file which may take several hours
to resolve. (2) Create a gridTools enviornment with python and
then install conda packages sequentially using the `slow_bootstrap.sh`
script.

Alternate Install(1):
```
$ conda env create -f conda/gridTools.yml
$ conda activate gridTools
```

Alternate Install(2):
```
$ conda create -n gridTools python==3.7.10
$ conda activate gridTools
$ ./slow_bootstrap.sh
```

You can also restore a conda environment using the explicit listing
of packages.
```
$ conda create --name gridTools --file conda/gridTools_explicit-linux-64.txt
```

## Performance

Sometimes the conda resolution can take a very long time to run.
Setting an automatic timeout is recommended if building a custom
conda enviroment.  This can be done using the `timeout` feature
of UNIX `time` command.

In this example, the timeout is set to 5 minutes to allow resolution
of the environment.
```
$ time timeout 5m conda env create -f conda/gridTools.yml
```

# Environments

Current operational environment for the grid toolset: ***gridTools***

## gridTools

This is the main enviroment for utilizing the grid generation libraries.

NOTE: Avoid version 0.5.2 of xesmf.  If you need to use the xgcm library,
      install it as a separate environment.

## legacyTools

NOTE: This is a very limited environment with netcdf4 and matplotlib's basemap
to review former functionality of older libraries and software.

This environment supported investigation into the following libraries:
  * [leaflet](../development/python/libraries/leaflet.md)
  * [pyroms](../development/python/libraries/pyroms.md)

# Post install

A successful install of conda packages will make the `pip install .`
quite easy.  All the dependent packages are again referenced in
the `requirements.txt` file for pip.  At the conclusion of the
install, only a minimal amount of package should be
actually installed.

You should see a similar message:
```
Successfully built numpypi xesmf
Installing collected packages: xesmf, numpypi, gridtools
  Running setup.py develop for gridtools
  Successfully installed gridtools-0.2.0+aaf0877 numpypi-1.0.0+40b7b0d xesmf-0.5.4.dev8+g7a2830c
```

If you are just doing an install and do not plan to edit any code,
please use: `pip install .`

If you are planning to edit code within gridtools, please use:
`pip install -e .`.  This will allow you to edit the gridtools
library.  Changes will immediately be seen when you restart
the jupyter kernel and rerun all the cells or rerun the
python script.
