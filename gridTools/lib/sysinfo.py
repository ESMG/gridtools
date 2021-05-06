# Small helper class to show basic system information
# Useful for debugging module/system conflicts
# Revised:
#   https://www.python.org/dev/peps/pep-0008/#package-and-module-names

import os, sys, re
import psutil
import shlex, subprocess

class SysInfo:

    # Functions

    def __init__(self):
        # Initialize
        self.resetVersionData()
        
        # Load conda version information upon creation of object
        self.loadVersionData()
    
    def isAvailable(self, pkgReq, verReq, orLower=False):
        # Simple package and version checker
        # Defaults to equal or higher, or set orLower to True to test reverse
        # X.Y.Z each of X Y Z might be 10a or 10b
        pass
        
    def is_lab_notebook(self):
        return any(re.search('jupyter-lab', x)
                   for x in psutil.Process().parent().cmdline())    
    
    def loadVersionData(self):
        # Load conda version information for other functions
        # Requires "conda" to be installed within the environment
        # conda install -c conda-forage conda
        # result = conda.cli.python_api.run_command(conda.cli.python_api.Commands.LIST, "--export")
        try:
            import conda.cli.python_api
        except:
            print("Unable to show requested version information.  Please install 'conda' in this environment.")
            return
        
        # Load conda environment information
        stdin, stdout, errcode =\
            conda.cli.python_api.run_command(conda.cli.python_api.Commands.LIST, "--export")
        itemList = {}
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
        
        # Load jupyterlab environment (if available)
        try:
            # Check if we can run jupyter labextension list
            cmd = 'jupyter labextension list'
            cmdList = shlex.split(cmd)
            temp = subprocess.Popen(cmdList, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            stdout, stderr = temp.communicate()
            stdout = stdout.split("\n")
            stderr = stderr.split("\n")
            print("stdout:",stdout)
            print("stderr:",stderr)
        except:
            pass
    
        self.versionData = itemList
        self.versionDataLoaded = True
        
    def printInfo(self, k, kd, msg):
        if hasattr(kd, k):
            print("%-40s: %s" % (msg, getattr(kd, k)))
            return
        if k in kd.keys():
            print("%-40s: %s" % (msg, kd[k]))

    def resetVersionData(self):
        self.versionDataLoaded = False
        self.versionData = {}
            
    def showAll(self, vList=[]):
        self.showSystem()
        self.showEnvironment()
        self.showCondaVersions(vList)

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
            self.printInfo('CONDA_DEFAULT_ENV', kd,'Active conda environment')

    def showCondaVersions(self, vList=[]):
        # Show versions of various conda modules
        if not(self.versionDataLoaded):
            self.loadVersionData()
            
        itemList = self.versionData

        # Report
        print("Conda reported versions of software:")
        if len(vList) == 0:
            vList = itemList.keys()
        for k in vList:
            if not(k in itemList):
                itemList[k] = "not installed"
            self.printInfo(k, itemList, k)

    def show(self, showOnly=[], vList=[]):
        self.showAll(vList=vList)


