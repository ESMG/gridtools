# Ubuntu VM

This document describes local installations of gridtools software
on a virtual machine.  The host is a MacOSX running Oracle
VirtualBox.  MacOS Big Sur 11.4, 2.7Ghz dual core Intel i5 
CPU with 16 GB of RAM.

# python venv

```
python3 -m venv venv/base
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools
python -m pip install -q certifi cython numpy
cd src/gridtools
python -m pip install -q -e .
```
