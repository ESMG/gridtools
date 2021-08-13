import os, sys, re
import psutil, shlex, subprocess
import logging
from packaging.version import Version, parse
from . import utils

class SysInfo(object):
    '''
    A small helper class to provide basic system information and misc
    operating system utilities.  Useful for debugging module or system
    conflicts.  Simple core calls should be placed into the utils
    module.  More complex functions that depend on results from other
    functions should go into this module.  For example, tracking or
    detecting module versions are in this module.
    '''

    # Functions

    def __init__(self, grd=None):
        # Attach to a logging mechanism
        self.grd = grd

        # Initialize data structures
        self.versionDataLoaded = False
        self.versionData = dict()
        
        # Maintain a table of python module/packages to increase
        # efficiency.
        self.installedPackages = dict()
        self.loadedPackages = dict()
        self.loadedPackageVersions = dict()
        self.packageManager = None
        self.versionMode = None

    def detectPythonEnvironment(self):
        '''This attempts to detect a python virtual environment that is
        running the python script.

        This attempts to guess if the script is running under conda or venv.
        If the answer is neither, then native is assumed.

        Other possible environments are covered in an article:
        https://towardsdatascience.com/comparing-python-virtual-environment-tools-9a6543643a44

            * virtualenv/virtualenvwrapper
            * pew (unmaintained ~ March 2018)
            * venv (recommended since Python 3.5)
            * pipenv
        '''

        envKeys = os.environ.keys()

        # Conda

        # Check for CONDA_DEFAULT_ENV and CONDA_PREFIX
        if 'CONDA_DEFAULT' in envKeys and 'CONDA_PREFIX' in envKeys:
            return 'conda'

        # venv
        if 'VIRTUAL_ENV' in envKeys:
            return 'venv'

        # default: native
        return 'native'

    def dumpVersionData(self):
        '''Return a string for use in netCDF attributes'''
        softwareKeys = list(self.versionData.keys())
        softwareKeys.sort()

        attrList = []
        for swKey in softwareKeys:
            attrList.append("%s %s" % (swKey, self.versionData[swKey]))

        return '; '.join(attrList)

    def get_jupyterlab_modules(self):

        # Capture jupyterlab environment (if available)
        try:
            # Check if we can run jupyter labextension list
            cmd = 'jupyter labextension list'
            (stdout, stderr, rc) = self.runCommand(cmd)
        except:
            pass

    def get_python_loaded_modules(self):

        loadedModules = []
        # Take only the root elements
        for mdl in list(sys.modules.keys()):
            data = mdl.split('.')
            if not(data[0] in loadedModules):
                loadedModules.append(data[0])
        for mdl in loadedModules:
            if not(mdl) in self.loadedPackages:
                try:
                    ver = self.get_python_module_version(mdl)
                    if ver:
                        self.installedPackages[mdl] = ver
                        self.loadedPackages[mdl] = ver
                        self.loadedPackageVersions[mdl] = ver
                except:
                    pass

        return

    def get_python_module_version(self, mdlName):
        '''Try to obtain the python module version.  This returns
        the version numer if the module was found or None if
        nothing was found or an error was encountered.
        '''

        # Obtain python version
        pythonVersion = utils.get_python_version()

        if Version(pythonVersion) >= Version('3.8'):
            try:
                from importlib.metadata import version
                return version(mdlName)
            except:
                return None
        else:
            try:
                import pkg_resources
                return pkg_resources.get_distribution(mdlName).version
            except:
                return None
    
    def isAvailable(self, pkgReq, verReq, orLower=False):
        # Simple package and version checker
        # Defaults to equal or higher, or set orLower to True to test reverse
        # X.Y.Z each of X Y Z might be 10a or 10b
        pass
        
    def is_lab_notebook(self):
        '''Detects if current process is a jupyter-lab process.'''
        return any(re.search('jupyter-lab', x)
                   for x in psutil.Process().parent().cmdline())    
    
    def loadVersionData(self, **kwargs):
        '''This function loads module version data in a variety of ways.  The
        default is for modules currently loaded by the python executable.

        **Keyword arguments**

            * *usePackageManager* (``boolean``) Use a package manager to
              discover module versions. Default: False
            * *packageManager* (``string``) Specify `conda` or `venv` as the
              package manager to use to show versions of installed software.
              Default: auto

        .. note::

            This function by default only obtains version information for
            modules already loaded into the python environment.  Switching
            to a package manager will display all installed software which
            may be more information than desired.
        
            For the `conda` package manager, the conda python module may
            be installed or the `conda` executable is available.

            The conda python module may be installed within the environment:
            `conda install -c conda-forge conda`
        '''

        # Do not allow this to run if it is already populated
        if self.versionDataLoaded:
            return

        usePackageManager = kwargs.pop('usePackageManager', False)
        packageManager = kwargs.pop('packageManager', 'auto')

        if usePackageManager:
            self.versionMode = 'installed'
        else:
            self.versionMode = 'loaded'

        if packageManager == 'auto':
            pythonEnv = self.detectPythonEnvironment()
            self.packageManager = pythonEnv
        else:
            self.packageManager = packageManager

        if usePackageManager and pythonEnv == 'conda':
            # result = conda.cli.python_api.run_command(conda.cli.python_api.Commands.LIST, "--export")
            try:
                import conda.cli.python_api
            except:
                msg = ("Unable to show requested version information.")
                if self.grd: self.grd.printMsg(msg, level=logging.INFO)
                msg = ("Please install the 'conda' python module in this environment.")
                if self.grd: self.grd.printMsg(msg, level=logging.INFO)
                return
        
            # Load conda environment information
            stdin, stdout, errcode =\
                conda.cli.python_api.run_command(conda.cli.python_api.Commands.LIST, "--export")
            itemList = dict()
            for strItem in stdin.split("\n"):
                #print(strItem)
                if len(strItem) > 0:
                    # Look for platform
                    if strItem[0] == "#":
                        if strItem.find('platform') > 0:
                            data = strItem.split(" ")
                            itemList['platform'] = ' '.join(data[2:])
                    else:
                        if strItem.find('=') > 0:
                            data = strItem.split("=")
                            if len(data) == 3:
                                itemList[data[0]] = data[1]

        # Capture pip environment (if available)
        # TODO
        if not(usePackageManager):
            self.get_python_loaded_modules()
            itemList = self.loadedPackages

        # Add auxillary package items
        #   platform: i386, etc
        #   python: not a module, but report the python version

        itemList['python'] = utils.get_python_version()
        if not('platform' in itemList):
            systemName = utils.get_system().lower()
            machineType = utils.get_machine()
            itemList['platform'] = "%s-%s" % (
                    systemName, machineType)
        
        self.versionData = itemList
        self.versionDataLoaded = True
        
    def printInfo(self, k, kd, msg):
        if hasattr(kd, k):
            print("%-40s: %s" % (msg, getattr(kd, k)))
            return
        if k in kd.keys():
            print("%-40s: %s" % (msg, kd[k]))

    def resetVersionData(self):
        '''This resets any loaded module version data.'''

        self.versionDataLoaded = False
        self.versionData = dict()
        self.installedPackages = dict()
        self.loadedPackages = dict()
        self.loadedPackageVersions = dict()
        self.versionMode = None

    def runCommand(self, cmdString):
        '''
        Generic function to run a command string and return the results as
        an array of three items.  Return: (stdout, stderr, returncode)
        '''
        try:
            cmdList = shlex.split(cmdString)
            temp = subprocess.Popen(cmdList, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            stdout, stderr = temp.communicate()
            stdout = stdout.decode('utf-8').split("\n")
            stderr = stderr.decode('utf-8').split("\n")
            rc = temp.returncode
            msg = ("stdout: %s" % (stdout))
            if self.grd: self.grd.debugMsg(msg)
            msg = ("stderr: %s" % (stderr))
            if self.grd: self.grd.debugMsg(msg)
            msg = ("return code: %d" % (rc))
            if self.grd: self.grd.debugMsg(msg)
            return (stdout, stderr, rc)
        except:
            #raise
            # Uncaught error
            msg = ("ERROR: Command failed to run (%s)" % (cmdString))
            if self.grd: self.grd.debugMsg(msg)
            return (None, None, None)
            
    def showAll(self, vList=[]):
        self.showSystem()
        self.showEnvironment()
        self.showPackageVersions(vList)

    def showSystem(self):
        # Show some basic system information
        if hasattr(os, 'uname'):
            kd = os.uname()
            self.printInfo('sysname', kd, 'System name')
            self.printInfo('nodename', kd, 'System name')
            self.printInfo('release', kd, 'Operating system release')
            self.printInfo('version', kd, 'Operating system version')
            self.printInfo('machine', kd, 'Hardware identifier')

    def showEnvironment(self):
        # Show environment information
        if hasattr(os, 'environ'):
            kd = os.environ
            self.printInfo('CONDA_DEFAULT_ENV', kd, 'Active conda environment')

    def showPackageVersions(self, vList=[]):
        # Show versions of various modules
        if not(self.versionDataLoaded):
            self.loadVersionData()
            
        itemList = self.versionData

        # Report
        print("Reported versions of software (%s):" % self.packageManager)
        if len(vList) == 0:
            vList = itemList.keys()
        for k in vList:
            if not(k in itemList):
                itemList[k] = "not %s" % (self.versionMode)
            self.printInfo(k, itemList, k)

    def show(self, showOnly=[], vList=[]):
        self.showAll(vList=vList)


