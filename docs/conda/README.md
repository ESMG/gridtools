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

# Troubleshooting

There are at least two known failure modes for conda that are documented below.
  * Upgrade of the `base` environment causes the conda package manager to malfunction.
  * Reinstalling an environment will break on older systems due to an aged GLIBC.

## Conda Package Manager Malfunction

Upgrading conda is usually accomplished by following the warning message
usually provided by conda:

```
==> WARNING: A newer version of conda exists. <==
  current version: 4.9.2
  latest version: 4.12.0

Please update conda by running

    $ conda update -n base -c defaults conda
```

In certain situations, after upgrading conda, the package manager is not longer
functional.  The typical problem encountered is the inability to contact any
repository.  Here is a typical error when running
certain commands:

```
$ conda create -n gridtest python==3.7.10
Collecting package metadata (current_repodata.json): failed

CondaHTTPError: HTTP 000 CONNECTION FAILED for url <https://conda.anaconda.org/pyviz/linux-64/current_repodata.json>
Elapsed: -

An HTTP error occurred when trying to retrieve this URL.
HTTP errors are often intermittent, and a simple retry will get you on your way.
'https://conda.anaconda.org/pyviz/linux-64'
```

### Revert back to prior version

If conda is broken beyond repair, there may be a way to salvage your environments.  If you
were fortunate to have kept the miniconda shell installer archive
(`Miniconda3-py39_4.9.2-Linux-x86_64.sh`), then you may be in luck.

Process:
  * Deactivate any exiting environments
  * Rename the existing miniconda root to a backup
  * Remove any .bashrc references
  * Re-login to clear any lingering shell enviroment references
  * Re-install miniconda to create a new miniconda root
  * Re-login to initialize the new shell environment
  * Change directory into the backup root `envs` directory
  * Copy (cp -a) environments you wish to salvage into the newly created miniconda root `envs` directory
  * Attempt to activate the copied environment
  * If all checks out, erase the backup miniconda root

## GLIBC errors

If you reload the gridtools environment on an old machine, you may encounter
GLIBC errors as shown below.

```
(gridtest) jrcermakiii@chinook03:~/src/gridtools/examples$ python mkGridsExample01.py
Traceback (most recent call last):
  File "mkGridsExample01.py", line 12, in <module>
    from gridtools.gridutils import GridUtils
  File "/import/AKWATERS/jrcermakiii/src/gridtools/gridtools/gridutils.py", line 5, in <module>
    import xarray as xr
  File "/import/AKWATERS/jrcermakiii/local/miniconda3/envs/gridtest/lib/python3.7/site-packages/xarray/__init__.py", line 1, in <module>
    from . import testing, tutorial, ufuncs
  File "/import/AKWATERS/jrcermakiii/local/miniconda3/envs/gridtest/lib/python3.7/site-packages/xarray/testing.py", line 8, in <module>
    from xarray.core import duck_array_ops, formatting, utils
  File "/import/AKWATERS/jrcermakiii/local/miniconda3/envs/gridtest/lib/python3.7/site-packages/xarray/core/duck_array_ops.py", line 13, in <module>
    import pandas as pd
  File "/import/AKWATERS/jrcermakiii/local/miniconda3/envs/gridtest/lib/python3.7/site-packages/pandas/__init__.py", line 22, in <module>
    from pandas.compat import (
  File "/import/AKWATERS/jrcermakiii/local/miniconda3/envs/gridtest/lib/python3.7/site-packages/pandas/compat/__init__.py", line 15, in <module>
    from pandas.compat.numpy import (
  File "/import/AKWATERS/jrcermakiii/local/miniconda3/envs/gridtest/lib/python3.7/site-packages/pandas/compat/numpy/__init__.py", line 7, in <module>
    from pandas.util.version import Version
  File "/import/AKWATERS/jrcermakiii/local/miniconda3/envs/gridtest/lib/python3.7/site-packages/pandas/util/__init__.py", line 1, in <module>
    from pandas.util._decorators import (  # noqa
  File "/import/AKWATERS/jrcermakiii/local/miniconda3/envs/gridtest/lib/python3.7/site-packages/pandas/util/_decorators.py", line 14, in <module>
    from pandas._libs.properties import cache_readonly  # noqa
  File "/import/AKWATERS/jrcermakiii/local/miniconda3/envs/gridtest/lib/python3.7/site-packages/pandas/_libs/__init__.py", line 13, in <module>
    from pandas._libs.interval import Interval
ImportError: /lib64/libc.so.6: version `GLIBC_2.14' not found (required by /import/AKWATERS/jrcermakiii/local/miniconda3/envs/gridtest/lib/python3.7/site-packages/pandas/_libs/interval.cpython-37m-x86_64-linux-gnu.so)
```

This is an indication that the underlying system (or cluster) you are using is
falling out of date. The supported python versions of modules managed by conda
are under constant integration (CI) are are rebuilt using newer systems and
hence are linked to more recent versions of GLIBC. On my particular system, the
underlying GLIBC is version 2.12. One or more of the loaded python modules now
requires GLIBC 2.14. Unless you have a backup of the conda environment, there is
no way to recover the original operating environment. You will likely have to
resort to conventional manual installation of modules to restore the environment.

To see what your conda installation is using for GLIBC, use conda info. The
version of glibc should be noted in the virtual packages.

```
$ conda info

     active environment : gridtest
    active env location : /import/AKWATERS/jrcermakiii/local/miniconda3/envs/gridtest
            shell level : 1
       user config file : /home/jrcermakiii/.condarc
 populated config files : /home/jrcermakiii/.condarc
          conda version : 4.9.2
    conda-build version : not installed
         python version : 3.9.1.final.0
       virtual packages : __glibc=2.12=0
                          __unix=0=0
                          __archspec=1=x86_64
       base environment : /import/AKWATERS/jrcermakiii/local/miniconda3  (writable)
           channel URLs : https://conda.anaconda.org/pyviz/linux-64
                          https://conda.anaconda.org/pyviz/noarch
                          https://conda.anaconda.org/conda-forge/linux-64
                          https://conda.anaconda.org/conda-forge/noarch
                          https://repo.anaconda.com/pkgs/main/linux-64
                          https://repo.anaconda.com/pkgs/main/noarch
                          https://repo.anaconda.com/pkgs/r/linux-64
                          https://repo.anaconda.com/pkgs/r/noarch
          package cache : /import/AKWATERS/jrcermakiii/local/miniconda3/pkgs
                          /home/jrcermakiii/.conda/pkgs
       envs directories : /import/AKWATERS/jrcermakiii/local/miniconda3/envs
                          /home/jrcermakiii/.conda/envs
               platform : linux-64
             user-agent : conda/4.9.2 requests/2.25.0 CPython/3.9.1 Linux/2.6.32-754.35.1.el6.61015g0000.x86_64 centos/6.10 glibc/2.12
                UID:GID : 3739:2161
             netrc file : None
           offline mode : False
```

## Discoveries and Workarounds

### pandas

At the moment, the GLIBC trouble seems to be limited to the `pandas`
package.  A workaround is to follow the installation proceedure for
gridtools and then reinstall the `pandas` package manually via pip.
