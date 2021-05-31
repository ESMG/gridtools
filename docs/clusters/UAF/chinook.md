# UAF COMPUTE CLUSTER: CHINOOK

## ENVIRONMENT #1 (venv)

export LOCAL_SW_PATH=/import/AKWATERS/jrcermakiii/local
#export PKG_CONFIG_PATH=${PKG_CONFIG_PATH}:${LOCAL_SW_PATH}/lib/pkgconfig
export PKG_CONFIG_PATH=${LOCAL_SW_PATH}/lib/pkgconfig
export PATH=${LOCAL_SW_PATH}/bin:${PATH}
export LD_LIBRARY_PATH=${LOCAL_SW_PATH}/lib64:${LOCAL_SW_PATH}/lib:${LD_LIBRARY_PATH}

## binutils 2.34

Required for nodejs.  Unpack tarball inside gcc-9.3.0.

## gcc 9.3.0

wget https://bigsearcher.com/mirrors/gcc/releases/gcc-9.3.0/gcc-9.3.0.tar.gz
tar xzf gcc-9.3.0.tar.gz
cd gcc-9.3.0
mv ../binutils-2.34 .
contrib/download_prerequisites
cd ..
mkdir objdir
cd objdir
../gcc-9.3.0/configure --prefix=/import/AKWATERS/jrcermakiii/local --enable-languages=c,c++,fortran,go --disable-multilib --enable-shared
make -j 16 >& make.log
make install
LIBDIR=/import/AKWATERS/jrcermakiii/local/libexec/gcc/x86_64-pc-linux-gnu/9.3.0

## tiff 4.3.0

## sqlite 3.31.1

wget https://github.com/sqlite/sqlite/archive/refs/tags/version-3.31.1.tar.gz
cd sqlite-version-3.31.1
./configure --prefix=/import/AKWATERS/jrcermakiii/local --disable-tcl
make
make install

## proj 7.3.1

## geos 3.9.1

## openssl 1.1.1f
./config --prefix=/import/AKWATERS/jrcermakiii/local

## libffi

wget https://github.com/libffi/libffi/releases/download/v3.3/libffi-3.3.tar.gz
Provides _ctypes

## python 3.8.10

wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tgz
tar xzf Python-3.8.10.tgz
cd Python-3.8.10
#./configure --prefix=/import/AKWATERS/jrcermakiii/local --enable-optimizations
./configure --prefix=/import/AKWATERS/jrcermakiii/local LDFLAGS='-L/import/AKWATERS/jrcermakiii/local/lib64'
make -j 16 >& make.log
make install

Just enough to get venv

## nodejs 14.17.0
Apply fix to node.gypi:
  https://github.com/nodejs/node/issues/30077 (add -lrt)

make CC="gcc -msse4.1"
make install CC="gcc -msse4.1"

```
# RESET:
deactivate
rm -rf workdir/local/venv/base

# INIT-ONCE: python3 -m venv workdir/local/venv/base
source workdir/local/venv/base/bin/activate

# INIT-ONCE: Open source install in order
# tiff(4.3.0): http://download.osgeo.org/libtiff/
# proj(7.2.1): https://github.com/OSGeo/PROJ.git
# geos(3.9.1): https://github.com/libgeos/geos.git
# nodejs(14.17.0): https://nodejs.org/en/download/
# X:proj(8.0.1): https://github.com/OSGeo/PROJ.git
# ./configure --prefix=/import/AKWATERS/jrcermakiii/local

# INIT-ONCE:
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools
python -m pip install certifi cython numpy
cd src/gridtools
python -m pip install -e .
```

## ENVIRONMENT #2

conda

```
conda update -n base -c defaults conda
conda env create -q -f conda/gridTools.yml
conda activate gridTools
cd src/gridtools
python -m pip install .
```
