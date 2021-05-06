#!/usr/bin/env python

import os, sys, logging
sys.path.append('lib')
from gridutils import GridUtils

grd = GridUtils()

grd.printMsg("This demonstrates how to work with the debugging system of GridUtils().")
grd.printMsg("")

grd.printMsg("This code generates some useful debugging information by gathering version")
grd.printMsg("for specific libraries.  This is helpful to software developers.  The")
grd.printMsg("developers may ask for other information depending on the nature of")
grd.printMsg("the problem.")
grd.printMsg("---")

from sysinfo import SysInfo
info = SysInfo()
info.show(vList=['platform','python','esmf','esmpy','xgcm','xesmf',
                 'netcdf4','numpy','xarray',
                 'cartopy','matplotlib',
                 'jupyter_core','jupyterlab','notebook',
                 'dask'])
grd.printMsg("---")

#grd.printMsg("This demonstrates how to access the internal help messages from the GridUtils()")
#grd.printMsg("library.  You may need to exit the help page by pressing the q key.")
# Help (module)
#print(help(GridUtils))
#grd.printMsg("")

# Without debugging, a failed assigment to a plot parameter subkey will result in
# a message and the program will continue running.  We can easily cause a problem
# by trying to use a non-existing subkey.  The only one that exists at the moment is
# projection.
grd.printMsg("")
grd.printMsg("Using a 'test' subkey to try and assign {'a': 1} into plot parameters.")
testParameters = {
        'a': 1
}

grd.printMsg("""Attempting to run: grd.setPlotParameters(testParameters, subKey='test')""")
grd.setPlotParameters(testParameters, subKey='test')
grd.printMsg("""
Note: nothing should have printed, it was silently ignored as the debug level
by default is zero(0) and the display of messages (verbosity) by default is at 
the INFO level which is one higher than DEBUG.  With both these settings, no 
messages are emitted.

""")

grd.printMsg("Lets change the debug level to 1 (MESSAGES) and the verbosity to DEBUG and try again.")
grd.printMsg("")
grd.setDebugLevel(1)
grd.setVerboseLevel(logging.DEBUG)
# This should also work
grd.setVerboseLevel("DEBUG")

grd.printMsg("""Attempting to run: grd.setPlotParameters(testParameters, subKey='test')""")
grd.setPlotParameters(testParameters, subKey='test')

grd.printMsg("")
grd.printMsg("""
If that message is utilizing the debugMsg() function, changing the debug level to 3
will attempt to start the python debugger pdb so you can poke around at the code and
attempt to reason out why it is failing at that point.

""")

grd.printMsg("Lets change the debug level to 3 (BREAKPOINT) and try again.")
grd.printMsg("NOTE: The program should stop with a (Pdb) prompt.  Use quit() to exit.")
grd.printMsg("      Or you can use c to continue and we can try debug level 2 (RAISE)")
grd.printMsg("      which will stop the program by raising the exception.")
grd.printMsg("")
grd.setDebugLevel(3)

grd.printMsg("""Attempting to run: grd.setPlotParameters(testParameters, subKey='test')""")
grd.setPlotParameters(testParameters, subKey='test')

grd.printMsg("")
grd.printMsg("Change debug level to RAISE (2).")
grd.setDebugLevel(2)

grd.printMsg("""Attempting to run: grd.setPlotParameters(testParameters, subKey='test')""")
grd.setPlotParameters(testParameters, subKey='test')

# No code beyond this point will run as the program will stop
# with an exception.
print("The program should never reach this point and should not be printed.")
