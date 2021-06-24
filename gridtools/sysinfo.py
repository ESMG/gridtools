import os, sys, re
import psutil, shlex, subprocess
import logging

class SysInfo(object):
    '''
    A small helper class to provide basic system information and misc
    operating system utilities.  Useful for debugging module or system
    conflicts.
    '''

    # Functions

    def __init__(self, grd=None):
        # Attach to a logging mechanism
        self.grd = grd

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
        
        # Load jupyterlab environment (if available)
        try:
            # Check if we can run jupyter labextension list
            cmd = 'jupyter labextension list'
            (stdout, stderr, rc) = self.runCommand(cmd)
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
        self.versionData = dict()

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


