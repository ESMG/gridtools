# UAF COMPUTE CLUSTER: CHINOOK

## ENVIRONMENT #1 (venv)

python3.7 using venv

```
# RESET:
deactivate
rm -rf workdir/local/venv/base

module load lang/Python/3.7.0-pic-intel-2019b
# INIT-ONCE: python3 -m venv workdir/local/venv/base
source workdir/local/venv/base/bin/activate

export LOCAL_SW_PATH=/import/AKWATERS/jrcermakiii/local
export PKG_CONFIG_PATH=${PKG_CONFIG_PATH}:${LOCAL_SW_PATH}/lib/pkgconfig
export PATH=${LOCAL_SW_PATH}/bin:${PATH}
export LD_LIBRARY_PATH=${LOCAL_SW_PATH}/lib:${LD_LIBRARY_PATH}

# INIT-ONCE: Open source install in order
# tiff(4.3.0): http://download.osgeo.org/libtiff/
# proj(7.2.1): https://github.com/OSGeo/PROJ.git
# geos(3.9.1): https://github.com/libgeos/geos.git
# nodejs(14.17.0): https://nodejs.org/en/download/
#  * https://github.com/nodejs/node/issues/30077 (add -lrt)
# X:proj(8.0.1): https://github.com/OSGeo/PROJ.git
# ./configure --prefix=/import/AKWATERS/jrcermakiii/local

# INIT-ONCE: pip install --upgrade pip
# INIT-ONCE:
pip install cython numpy setuptools
pip uninstall certifi
pip install certifi
pip uninstall importlib-metadata
pip install "importlib-metadata<4"
pip uninstall setuptools
pip check

python setup.py develop
# INIT-ONCE:
jupyter lab build
pip uninstall pyviz-comms
pip install pyviz-comms
```

## ENVIRONMENT #2

conda
conda create -n gridTools python
conda activate gridTools
