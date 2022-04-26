# Generic utility functions
'''
Generic utility functions
'''

import copy, datetime, hashlib, platform, subprocess, sys
import numpy as np
from decimal import *
from . import sysinfo
import gridtools

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

    # On error provide the gridtools.__version__ variable as the version number
    if rc != 0:
        out = gridtools.__version__

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

def jday2date(jday):
    """
    Copied from pyroms_toolbox.py
    (https://github.com/ESMG/pyroms/commit/b83f79614acbf245e2bc35f0c65b5a27c862992f)

    return the date from the number od days since 1900/01/01.
    date = jday2date(jday) where jday is an integer or a float
                             and date is a datetime object
    """

    if type(jday).__name__ == 'ndarray':
        nt = np.size(jday)
    else:
        nt = 1
        jday = np.array([jday])

    date = []

    jd0 = 2415021 #days since 1900/01/01

    for t in range(nt):
        j = int(np.floor(jday[t])) + 32044 + jd0
        g = j // 146097
        dg = j % 146097
        c = (dg // 36524 + 1) * 3 // 4
        dc = dg - c * 36524
        b = dc // 1461
        db = dc % 1461
        a = (db // 365 + 1) * 3 // 4
        da = db - a * 365
        y = g * 400 + c * 100 + b * 4 + a
        m = (da * 5 + 308) // 153 - 2
        d = da - (m + 4) * 153 // 5 + 122
        Y = y - 4800 + (m + 2) // 12
        M = (m + 2) % 12 + 1
        D = d + 1

        hr = Decimal(str(jday[t])) - Decimal(str(np.floor(jday[t])))
        hr = hr * 24
        h = int(hr)
        m = int((hr-h)*60)
        s = int(hr*3600 - h*3600 - m*60)

        date.append(datetime.datetime(Y,M,D,h,m,s))

    if np.size(date) == 1:
        date = date[0]
    else:
        date = np.array(date)

    return date
