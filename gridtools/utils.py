# Generic utility functions
'''
Generic utility functions
'''

import copy, datetime, hashlib, platform, subprocess, sys
import numpy as np
from . import sysinfo

def checkArgument(vDict, vKey, vVal):
    '''
    This checks to see if there is a key in the passed dictionary.  If the
    key does not exist, create the key with the specified value.  No logging
    of any kind is performed.  Any errors are silently ignored.

    :param vDict: python dictionary; typically kwargs
    :type vDict: dict
    :param vKey: dictionary key to check
    :type vKey: string
    :param vVal: value to use for dictionary key if it does not exist
    :type vVal: value
    :return: none
    :rtype: none
    '''

    try:
        if not(vKey in vDict.keys()):
            vDict[vKey] = vVal
    except:
        pass

def get_git_repo_version_info(grd=None):
    """Describe the current version of this script as known by Git.

    This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
    """
    # Refactor to use: git config --get remote.origin.url
    repo_name = 'ESMG/gridtools'
    #git_command = ['git', 'describe', '--all', '--long', '--dirty', '--abbrev=10']
    git_command = 'git describe --all --long --dirty --abbrev=10'
    #try:
    #    description =  subprocess.check_output(git_command, universal_newlines=True).rstrip()
    #    return repo_name + ': ' + description
    #except:
    #    return repo_name + ': running git returned an error'
    sysObj = sysinfo.SysInfo(grd=grd)
    (out, err, rc) = sysObj.runCommand(git_command)
    return repo_name + ": %s" % (out)

def get_history_entry(argv):
    """Construct an entry for the global 'history' attribute of a NetCDF file,
    which is a date and the command used.

    This function is copied from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
    """
    today = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    command = ' '.join(argv)
    return today + ': ' + command

def get_architecture():
    '''Returns the executable architecture.'''
    return platform.architecture()

def get_machine():
    '''Returns the machine type: i386, x86_64, etc.'''
    return platform.machine()

def get_processor():
    '''Returns the real processor name.'''
    return platform.processor()

def get_python_version():
    '''Returns the python version.'''
    return platform.python_version()

def get_system():
    '''Returns the system/OS name: Linux, Darwin, etc.'''
    return platform.system()

def get_release():
    '''Returns the system' release version.'''
    return platform.release()

def runningHow():
    """Utility function to determine how a python script is being run.

    +--------------------------+----------------+
    | Detected Value           | Returned Value |
    +--------------------------+----------------+
    | ZMQInteractiveShell      | jupyter        |
    +--------------------------+----------------+
    | TerminalInteractiveShell | ipython        |
    +--------------------------+----------------+
    | <other>                  | <other>        |
    +--------------------------+----------------+
    | on error/exception       | python         |
    +--------------------------+----------------+
    """
    try:
        shell = get_ipython().__class__.__name__

        if shell == 'ZMQInteractiveShell':
            shell = 'jupyter'

        if shell == 'TerminalInteractiveShell':
            shell = 'ipython'

        return shell
    except:
        return "python"

def sha256sum(xrData):
    """Utility function that returns a hash of the data provided.
    """

    return hashlib.sha256( np.array( xrData ) ).hexdigest()
