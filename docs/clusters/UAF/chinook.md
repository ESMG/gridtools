# UAF COMPUTE CLUSTER: CHINOOK

## ENVIRONMENT #1 (venv)

export LOCAL_SW_PATH=/import/AKWATERS/jrcermakiii/local
#export PKG_CONFIG_PATH=${PKG_CONFIG_PATH}:${LOCAL_SW_PATH}/lib/pkgconfig
export PKG_CONFIG_PATH=${LOCAL_SW_PATH}/lib/pkgconfig
export PATH=${LOCAL_SW_PATH}/bin:${PATH}
export LD_LIBRARY_PATH=${LOCAL_SW_PATH}/lib64:${LOCAL_SW_PATH}/lib:${LD_LIBRARY_PATH}

## gcc 9.3.0

Newer compiler required for python numba module.

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

## binutils 2.34

Newer assembler required for nodejs.  Unpack tarball inside gcc-9.3.0.

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

# sphinx

For some reason sphinx cannot build documentation using `latexpdf` after
a `clean`.  Please run `make html` first and then `make latexpdf` will
succeed.

# FRE-Tools installation

## netcdf

Requirements
 * http://prdownloads.sourceforge.net/libpng/zlib-1.2.11.tar.gz?download
 * https://support.hdfgroup.org/ftp/lib-external/szip/2.1.1/src/szip-2.1.1.tar.gz
 * https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.10/hdf5-1.10.7/src/hdf5-1.10.7.tar.gz

Building
```
# See HDF5 dependency below
$ export H5DIR=/home/jrcermakiii/workdir/local
$ CPPFLAGS='-I${H5DIR}/include' LDFLAGS='-L${H5DIR}/lib' ./configure --prefix=${H5DIR} --enable-nczarr --enable-mmap --enable-byterange 
```

### zlib

```
$ ./configure --prefix=/home/jrcermakiii/workdir/local --enable-shared
```
 
### szip

Normal build process.

```
$ ./configure --prefix=/home/jrcermakiii/workdir/local --enable-shared
```

### hdf5

```
$ export H5DIR=/home/jrcermakiii/workdir/local
$ CPPFLAGS='-I${H5DIR}/include' LDFLAGS='-L${H5DIR}/lib' ./configure --with-zlib=${H5DIR} --with-szlib=${H5DIR} --prefix=${H5DIR} --enable-hl
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

# jupyter

It is a couple step process to launch a jupyter session from
the UAF:chinook cluster.

## Start an interactive node via srun

Connect to any head node.

```
srun -p t1small --nodes=1 --exclusive --pty /bin/bash
```

Ensure the enviroment is set to run gridtools and start jupyter lab.

Use the IP address to start jupyter lab.

```
jupyter lab --ip=10.50.50.4 --no-browser
```

Copy the http://127.0.0.1:8888/... link for use below.

Find the IP address of the interactive node and put into
`COMPUTE_NODE` on your local machine from
a separate shell.

```
export COMPUTE_NODE=10.50.50.4
```

## Forward port 8888

From any head node to your local machine.

```
ssh -A -X -Y -L 8888:${COMPUTE_NODE}:8888 jrcermakiii@chinook04.rcs.alaska.edu
```

Once connected, paste the link that was copied above into a browser on
your local machine.

If also using dask, forward port 8787 also.

```
ssh -A -X -Y -L 8888:${COMPUTE_NODE}:8888 8787:${COMPUTE_NODE}:8787 jrcermakiii@chinook04.rcs.alaska.edu
```


