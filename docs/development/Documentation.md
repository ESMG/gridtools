# Documentation

This project uses the same documentation process as the MOM6 manual.
A separate `sphinx` environment is created for creating the gridtools
documentation.

# Important Information

For python documentation to work, it requires a fully operational
software stack for the library.  These instructions are additional
to the basic requirements for installation of the gridtools
library.

Installation of TeX is a little more cumbersome.

## Bookmarks

 * https://devguide.python.org/documenting/
 * https://docs.python-guide.org/writing/documentation/
 * https://eikonomega.medium.com/getting-started-with-sphinx-autodoc-part-1-2cebbbca5365
 * https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
 * https://stackoverflow.com/questions/50564999/lib64-libc-so-6-version-glibc-2-14-not-found-why-am-i-getting-this-error
 * https://thomas-cokelaer.info/tutorials/sphinx/docstring_python.html
 * https://tug.org/texlive/quickinstall.html

# TeX

These are specific instructions for installation of TeX on the chinook@UAF cluster.
Use only after activating the gridTools environment for conda.  This installs over
7 GB of data.

SPECIAL NOTE: Do not mix this software directly with the gridTool installation.
Only activate it when you need to build the PDF.

```
$ cd src/TeX
$ wget https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
$ tar xzf install-tl-unx.tar.gz
$ cd install-tl-20210611
$ ./install-tl
$ export TEXDIR=/import/AKWATERS/jrcermakiii/local/texlive/2021
$ export TEXMFHOME=${TEXDIR}/texmf
```

The install may fail with some warnings:
```
kpsewhich: /lib64/libc.so.6: version 'GLIBC_2.14' not found
```
This means a local installation of the libc.so is required for TeX to run.  See one
time installation steps below.

These commands needed to be rerun after installation at chinook@UAF once the
environment variables are set and glibc is installed.

```
$ updmap-sys --nohash
$ mtxrun --generate
$ fmtutil-sys --no-error-if-no-engine=luajithbtex,luajittex,mfluajit --no-strict --all
```

Created a `latex.sh` to run after `conda activate gridTools`.  This allows installation
of TeX within the conda environment.

```
export TEXDIR=/import/AKWATERS/jrcermakiii/local/texlive/2021
export TEXMFHOME=${TEXDIR}/texmf
# This updates the users PATH so TeX executables can be found
export TEXPATH=${TEXDIR}/bin/x86_64-linux
export PATH=${TEXPATH}:${PATH}
export MANPATH=${TEXDIR}/texmf-dist/doc/man:${MANPATH}
export INFOPATH=${TEXDIR}/texmf-dist/doc/info:${INFOPATH}
# If glibc is needed
export LD_LIBRARY_PATH=${TEXDIR}/lib:${LD_LIBRARY_PATH}
```

Activation sequence:
```
$ conda activate gridTools
$ source latex.sh
```

# Updates to the gridTools environment

The only thing needed is Doxygen.  The rest of the
requirements are installed via pip.

To test with the MOM6 Manual documentation:
```
# Need to have a functional pdflatex installed to make PDF.
$ conda activate gridTools
# PERFORM ONE TIME INSTALL ITEMS
$ git clone git@github.com:ESMG/MOM6.git
$ cd MOM6/docs
$ git checkout dev/esmg
$ python -m pip install -r requirements.txt
$ make html
# Start a very basic webserver
$ python -m http.server 8888
# Navigate to: http://localhost:8888/_build/html/
```

## One time installation

```
$ conda install doxygen
$ wget http://ftp.gnu.org/gnu/glibc/glibc-2.14.tar.gz
# A local install of glibc may not be needed.  It is here if you need it.
$ tar xzf glibc-2.14.tar.gz
$ cd glibc-2.14
$ mkdir build
$ cd build
$ ../configure --prefix=${TEXDIR}
$ make
$ make install
```

## MOM6 Manual

Make the HTML pages:
```
$ make html
```

Make the PDF:
```
$ make latexpdf
```

# Gridtools manual

## Initialization

This was the initialization process.  This does not need to be
repeated.

```
$ sphinx-quickstart
Welcome to the Sphinx 3.3.0+ quickstart utility.

Please enter values for the following settings (just press Enter to
accept a default value, if one is given in brackets).

Selected root path: .

You have two options for placing the build directory for Sphinx output.
Either, you use a directory "_build" within the root path, or you separate
"source" and "build" directories within the root path.
> Separate source and build directories (y/n) [n]: y

The project name will occur in several places in the built documentation.
> Project name: Gridtools library
> Author name(s): MOM6 Community
> Project release []: 0.2.0

If the documents are to be written in a language other than English,
you can select a language here by its language code. Sphinx will then
translate text that it generates into that language.

For a list of supported codes, see
https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-language.
> Project language [en]:

Creating file src/gridtools/source/conf.py.
Creating file src/gridtools/source/index.rst.
Creating file src/gridtools/Makefile.
Creating file src/gridtools/make.bat.

Finished: An initial directory structure has been created.

You should now populate your master file src/gridtools/source/index.rst
and create other documentation
source files. Use the Makefile to build the docs, like so:
   make builder
where "builder" is one of the supported builders, e.g. html, latex or linkcheck.
```
