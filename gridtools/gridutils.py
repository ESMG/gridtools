# General imports and definitions
import os, re, sys, datetime, logging, importlib, copy, math
import cartopy, warnings, hashlib
import numpy as np
import xarray as xr
from pyproj import CRS, Transformer
import pandas as pd
import requests, urllib.parse
import matplotlib as mpl
import gridtools

# Needed for panel.pane                
from matplotlib.figure import Figure
# not needed for mpl >= 3.1
# Does not cause any problems to continue to use it
from matplotlib.backends.backend_agg import FigureCanvas  

# Required for:
#  * ROMS to MOM6 grid conversion
#  * Computation of MOM6 grid metrics
from . import spherical

# Other utilities
from . import fileutils
from . import utils
from . import sanity
from . import sysinfo

class GridUtils(object):

    def __init__(self, app=dict()):
        # Constants
        self.PI_180 = np.pi/180.
        # Adopt GRS80 ellipse from proj
        self._default_Re = 6.378137e6
        self._default_ellps = 'GRS80'
        self._default_availableGridTypes = ['MOM6']
        
        # Application object
        self.applicationObj = None
        # File pointers
        self.xrOpen = False
        self.xrDS = xr.Dataset()
        self.grid = self.xrDS
        # Native grid variable (ROMS, etc)
        self.nativeGrid = None
        # Allow setting of chunk parameter for grids
        self.xrChunks = None
        # Internal parameters
        self.usePaneMatplotlib = False
        self.msgBox = None
        # Private variables begin with a _
        # Grid parameters
        # Locals
        self.gridMade = False
        self.gridInfo = dict()
        self.gridInfo['dimensions'] = dict()
        self.gridInfo['gridParameters'] = dict()
        self.gridInfo['gridParameterKeys'] = self.gridInfo['gridParameters'].keys()
        # Defaults
        self.plotParameterDefaults = {
            'figsize': (8, 6),
            'dpi': 100.0,
            'extent': [],
            'extentCRS': cartopy.crs.PlateCarree(),
            'projection': {
            },
            'showGrid': True,
            'showGridCells': False,
            'showSupergrid': False
        }
        # Plot parameters
        self.gridInfo['plotParameters'] = self.plotParameterDefaults
        self.gridInfo['plotParameterKeys'] = self.gridInfo['plotParameters'].keys()

        # Messages
        # Logging and Verbosity Levels
        # CRITICAL:50; ERROR:40; WARNING:30; INFO:20, DEBUG:10, NOTSET:0
        self.debugLevel = 0
        self.verboseLevel = logging.INFO
        # Logging options
        self.msgBuffer = []
        self.msgLogger = False
        self.msgLogFile = None
        self.msgLogLevel = logging.WARNING
        self.stdLogValues = {
                0: 'NOTSET',
                10: 'DEBUG',
                20: 'INFO',
                30: 'WARNING',
                40: 'ERROR',
                50: 'CRITICAL'
        }

    # utility operations utility functions
    # Utility Operations Utility Functions

    def addMessage(self, msg):
        '''Append new message to message buffer.'''
        self.msgBuffer.append(msg)
        return

    def app(self):
        '''By calling this function, the user is requesting the application functionality of GridUtils().
           return the dashboard, but GridUtils() also has an internal pointer to the application.'''
        # Delay loading app module until we actually call app()
        # GridUtils() application
        from . import app
        appObj = app.App(grd=self)
        self.applicationObj = appObj
        return appObj.dashboard

    def application(self, app=dict()):
        '''Convienence function to attach application items to GridUtils() so it can update certain portions
        of the application::

            app = {
                'messages': panel.widget.TextBox     # Generally a pointer to a panel widget for display of text
                'defaultFigureSize': (8,6)           # Default figure size to return from matplotlib
                'usePaneMatplotlib': True/False      # Instructs GridUtils to use panel.pane.Matplotlib for plot objects 
            }

        '''
        # Setup links to panel, etc
        appKeys = app.keys()
        if 'messages' in appKeys:
            self.msgBox = app['messages']
            msg = "GridUtils application initialized."
            self.printMsg(msg, level=logging.INFO)
        if 'defaultFigureSize' in appKeys:
            self.plotParameterDefaults['figsize'] = app['defaultFigureSize']
        if 'usePaneMatplotlib' in appKeys:
            self.usePaneMatplotlib = app['usePaneMatplotlib']
        else:
            self.usePaneMatplotlib = False

    def adjustExternalLoggers(self):
        '''This adjusts some noisy loggers from other python modules.'''

        # Readjust logger levels to specific noisy modules
        noisyModules = {
                'PIL.PngImagePlugin': logging.ERROR,
                'fiona._env': logging.ERROR,
                'fiona.collection': logging.ERROR,
                'fiona.env': logging.ERROR,
                'fiona.ogrext': logging.ERROR,
                'matplotlib.backends.backend_pdf': logging.ERROR,
                'matplotlib.font_manager': logging.ERROR,
        }

        for moduleName in noisyModules.keys():
            lh = logging.getLogger(moduleName)
            lh.setLevel(noisyModules[moduleName])

        return

    def isAvailable(self, utilName):
        '''Check the availablilty of a runnable executable in the
        system PATH.  Returns True if an executable appears to be
        available in the system PATH.  Otherwise, return False.
        '''
        sysObj = sysinfo.SysInfo(grd=self)
        cmd = 'which %s' % (utilName)
        (stdout, stderr, rc) = sysObj.runCommand(cmd)

        if rc == 0:
            return True

        return False


    def clearMessage(self):
        '''This clears the message buffer of messages.'''
        self.msgBuffer = []
        return

    def debugMsg(self, msg, level = -1):
        '''This function has a specific purpose to aid in debugging and
        activating pdb breakpoints.  NOTE: pdb breakpoints tend not to
        work very well when running under the gridtools application.  It
        tends to terminate the bokeh/tornado server.

        The debug level can be zero(0) and you can forcibly add a break
        point in the code by using `debugMsg(msg, level=3)` anywhere in
        the code.

        .. note::

            Currently defined debug levels:
                0=off 
                1=log debugging messages
                2=raise an exception
                3=stop with a pdb breakpoint after logging message
        '''

        # If level is not set (-1), set to self.debugLevel
        if level == -1:
            level = self.debugLevel

        if level < 1:
            return

        if level >= 1 and msg != "":
            # Send the message at the DEBUG level if 
            # the message is not empty
            self.printMsg(msg, level=logging.DEBUG)

        if level == 2:
            raise

        if level == 3:
            breakpoint()

        return

    def deleteLogfile(self, logFilename):
        '''Delete a log file.  Logging must be off.'''
        if self.msgLogger:
            self.printMsg("Logging active: Unable to delete log file.", level=logging.ERROR)
            return

        if not(os.path.isfile(logFilename)):
            self.printMsg("Logfile (%s) does not exist." % (logFilename), level=logging.ERROR)
            return

        os.unlink(logFilename)
        self.printMsg("Logfile (%s) removed." % (logFilename), level=logging.INFO)

    def detachLoggingFromApplication(self):
        '''Detach logging from application so messages are shown in
        the script and/or jupyter.'''
        self.msgBox = None
        msg = "GridUtils detached logging from application information window."
        self.printMsg(msg, level=logging.INFO)

    def disableLogging(self):
        '''Disable logging of messages to a file'''
        self.logHandle.disable = True
        self.logHandle = None
        self.msgLogger = False
        self.printMsg("Logging disabled", level=logging.INFO)

    def enableLogging(self, logFilename):
        '''Enable logging of messages to a file'''

        # Do not permit re-enabling a logging event if logging is already been activated
        if self.msgLogger:
            self.printMsg("Logging already active.  Ignoring request.", level=logging.ERROR)
            return

        # Test to see if we can write to the log file
        success = False
        try:
            fn = open(logFilename, 'a')
            success = True
        except:
            self.printMsg("Failed to open logfile (%s)" % (logFilename), level=logging.CRITICAL)
            return

        if success:
            fn.close()

        logging.basicConfig(filename=logFilename, level=self.msgLogLevel)
        self.adjustExternalLoggers()
        self.logHandle = logging.getLogger(__name__)
        self.logHandle.disabled = False
        self.msgLogger = True
        self.printMsg("Logging enabled", level=logging.INFO)

    def filterLogMessages(self, record):
        '''This may not be needed after all.'''
        print(">>",record.name,__name__)
        if record.name == __name__:
            return True
        return False

    def getDebugLevel(self):
        '''Get the current debug level for GridUtils().  See setDebugLevel() for available
        levels.'''
        return self.debugLevel

    def getLogLevel(self):
        '''Get the current debug level for GridUtils().  See setLogLevel() for available
        levels.'''
        return self.msgLogLevel

    def getRadius(self, param):
        '''Return a radius based on projection string.  If parsing the projection string
        fails, the radius from GRS80/WGS84 is used.'''

        # GRS80/WGS84
        radiusVal = self._default_Re

        if 'projection' in param:
            if 'proj' in param['projection']:
                try:
                    crs = CRS.from_proj4(param['projection']['proj'])
                    radiusVal = crs.ellipsoid.semi_major_metre
                except:
                    msg = "WARNING: Using default ellipsoid.  Projection string was not used."
                    self.printMsg(msg, level=logging.WARNING)
                    self.debugMsg(msg)
                    pass

        return radiusVal

    def getVerboseLevel(self):
        '''Get the current verbose level for GridUtils()'''
        return self.verboseLevel

    def getVersion(self):
        '''Return the version number of this library'''

        softwareRevision = gridtools.__version__

        return softwareRevision

    def printMsg(self, msg, level = logging.INFO):
        '''
        The verboseLevel and msgLogLevel can be set separately to any level.
        If this is attached to a panel application with a message
        box, the output is sent to that object.  Messages omitting the level argument
        will default to INFO.
        '''

        # Debugging messaging system: may be removed later
        #if self.debugLevel >= 1:
        #    print(">>(%s)(%d)(%d)" % (msg, level, self.verboseLevel))

        # If logging is enabled, send it to the logger
        if self.msgLogger:
            self.logHandle.log(level, msg)

        if level >= self.verboseLevel:
            self.addMessage(msg)

            # Always update the application message box
            # If we don't have a msgBox, then print to STDOUT.
            if hasattr(self, 'msgBox'):
                if self.msgBox:
                    self.msgBox.value = self.showMessages()
                else:
                    print(msg)
            else:
                print(msg)

        return

    def showLoggers(self):
        '''Display an alphabetical list of loggers.  Messages sent at the
        INFO level.'''

        # List of all known loggers: logging.Logger.manager.loggerDict
        loggerNames = list(logging.Logger.manager.loggerDict)
        loggerNames.sort()
        for loggerName in loggerNames:
            logger = logging.getLogger(loggerName)
            msg = "%-40s : %s" % (logger.name, logging.getLevelName(logger.getEffectiveLevel()))
            self.printMsg(msg, level=logging.INFO)

    def showMessages(self):
        '''This converts the message buffer to text with linefeeds.'''
        return '\n'.join(self.msgBuffer) 

    def setDebugLevel(self, newLevel):
        '''Set a new debug level.

        :param newLevel: debug level to set or update
        :type newLevel: integer
        :return: none
        :rtype: none

        .. note::
            Areas of code that typically cause errors have try/except blocks.  Some of these
            have python debugging breakpoints that are active when the debug level is set
            to a positive number.        

            Currently defined debug levels:
                0=off 
                1=extra messages
                2=raise an exception
                3=stop at breakpoints
        '''
        self.printMsg("Debug level now (%d)" % (newLevel))
        self.debugLevel = newLevel

    def setLogLevel(self, newLevel):
        '''Set a new logging level.

        :param newLevel: logging level to set or update
        :type newLevel: integer or string
        :return: none
        :rtype: none

        .. note::
            Setting this to a positive number will increase the feedback from this
            module.

            The available levels are:
                +----------+---------------+
                | Level    | Numeric value |
                +----------+---------------+
                | CRITICAL | 50            |
                +----------+---------------+
                | ERROR    | 40            |
                +----------+---------------+
                | WARNING  | 30            |
                +----------+---------------+
                | INFO     | 20            |
                +----------+---------------+
                | DEBUG    | 10            |
                +----------+---------------+
        '''
        if type(newLevel) == str:
            try:
                newLevel = logging.getLevelName(newLevel)
            except:
                newLevel = logging.INFO

        self.msgLogLevel = newLevel

        # Also update the logger, if active
        if self.msgLogger:
            self.logHandle.setLevel(newLevel)

    def setVerboseLevel(self, newLevel):
        '''Set a new verbose level.

        :param newLevel: verbose level to set or update
        :type newLevel: integer or string
        :return: none
        :rtype: none
        
        .. note::
            Setting this to a positive number will increase the feedback from this
            module.

            The available levels are:
                +----------+---------------+
                | Level    | Numeric value |
                +----------+---------------+
                | CRITICAL | 50            |
                +----------+---------------+
                | ERROR    | 40            |
                +----------+---------------+
                | WARNING  | 30            |
                +----------+---------------+
                | INFO     | 20            |
                +----------+---------------+
                | DEBUG    | 10            |
                +----------+---------------+
        '''
        if type(newLevel) == str:
            try:
                newLevel = logging.getLevelName(newLevel)
            except:
                newLevel = logging.INFO
                
        self.verboseLevel = newLevel

    # grid operations grid functions
    # Grid Operations Grid Functions

    def clearGrid(self):
        '''Call this when you want to erase the current grid.  This also
        clobbers any current grid and plot parameters.
        Do not call this method between plots of the same grid in different
        projections.'''

        # If there are file resources open, close them first.
        if self.xrOpen:
            self.closeGrid()

        self.xrFilename = None
        self.xrDS = xr.Dataset()
        self.grid = self.xrDS
        self.nativeGrid = None
        self.xrChunks = None
        self.gridInfo = dict()
        self.gridInfo['dimensions'] = dict()
        self.clearGridParameters()
        self.resetPlotParameters()

    def computeGridMetricsCartesian(self):
        '''Compute MOM6 grid metrics: angle_dx, dx, dy and area for a
        grid in cartesian coordinates.
        '''
        pass

    def computeGridMetricsSpherical(self):
        '''Compute MOM6 grid metrics: angle_dx, dx, dy and area for a
        grid in spherical coordinates.
        '''

        self.grid.attrs['grid_version'] = "0.2"
        self.grid.attrs['code_version'] = "GridTools: %s" % (self.getVersion())
        self.grid.attrs['history'] = "%s: created grid with GridTools library" %\
            (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        try:
            self.grid.attrs['projection'] = self.gridInfo['gridParameters']['projection']['name']
        except:
            pass

        # Add additional metadata if available
        addMetadata = ['centerX', 'centerY', 'centerUnits', 'dx', 'dxUnits', 'dy', 'dyUnits', 'tilt']
        for metaTag in addMetadata:
            if metaTag in self.gridInfo['gridParameters'].keys():
                self.grid.attrs['grid_%s' % (metaTag)] = self.gridInfo['gridParameters'][metaTag]
        #self.grid.attrs['grid_centerX'] = self.gridInfo['gridParameters']['centerX']
        #self.grid.attrs['grid_centerY'] = self.gridInfo['gridParameters']['centerY']
        #self.grid.attrs['grid_centerUnits'] = self.gridInfo['gridParameters']['centerUnits']
        #self.grid.attrs['grid_dx'] = self.gridInfo['gridParameters']['dx']
        #self.grid.attrs['grid_dxUnits'] = self.gridInfo['gridParameters']['dxUnits']
        #self.grid.attrs['grid_dy'] = self.gridInfo['gridParameters']['dy']
        #self.grid.attrs['grid_dyUnits'] = self.gridInfo['gridParameters']['dyUnits']
        #self.grid.attrs['grid_tilt'] = self.gridInfo['gridParameters']['tilt']

        #try:
        #    self.grid.attrs['conda_env'] = os.environ['CONDA_PREFIX']
        #except:
        #    self.grid.attrs['conda_env'] = "Conda environment not found."

        #try:
        #    #os.system("conda list --explicit > package_versions.txt")
        #    #self.grid.attrs['package_versions'] = str(pd.read_csv("package_versions.txt"))
        #    sysObj = sysinfo.SysInfo(grd=self)
        #    cmd = "conda list --explicit"
        #    (out, err, rc) = sysObj.runCommand(cmd)
        #    self.grid.attrs['package_versions'] = out
        #    #self.grid.attrs['package_versions'] = "/n".join(out)
        #except:
        #    #raise
        #    try:
        #        self.grid.attrs['conda_env'] = os.environ['CONDA_PREFIX']
        #    except:
        #        self.grid.attrs['conda_env'] = "Conda environment not found."
        #
        #    self.grid.attrs['package_versions'] = os.environ['CONDA_PREFIX']

        #try:
        #    response = requests.get("https://api.github.com/ESMG/gridtools/releases/latest")
        #    self.grid.attrs['software_version'] =  print(response.json()["name"])
        #except:
        #    self.grid.attrs['software_version'] = ""

        # Collect system metadata
        sysObj = sysinfo.SysInfo(grd=self)
        sysObj.loadVersionData()
        self.grid.attrs['software_version'] = sysObj.dumpVersionData()

        # If the global attribute 'proj' is not set, try to set it using
        # provided gridParameters.  Use the global 'proj' attribute if
        # already set.

        try:
            if not('proj' in self.grid.attrs.keys()):
                self.grid.attrs['proj'] = self.gridInfo['gridParameters']['projection']['proj']
        except:
            projString = self.formProjString(self.gridInfo['gridParameters'])
            if projString:
                self.grid.attrs['proj'] = projString
                self.gridInfo['gridParameters']['projection']['proj'] = projString
            else:
                msg = "WARNING: Projection string could not be determined from grid parameters."
                self.printMsg(msg, level=logging.WARNING)
                self.debugMsg('')

        # Determine radius from provided metadata
        # R = 6370.e3          # Radius of sphere (from original pyroms ROMS to MOM6 grid conversion script)
        # R = self._default_Re # (GRS80 is the default for the proj python package)
        R = self.getRadius(self.gridInfo['gridParameters'])

        # Make a copy of the lon grid as values are changed for computation
        # xarray=0.19.0 requires unpacking of Dataset variables by using .data
        lon = self.grid.x.copy().data
        lat = self.grid.y.copy().data

        # Approximate edge lengths as great arcs
        self.grid['dx'] = (('nyp', 'nx'),  R * spherical.angle_through_center( (lat[ :,1:],lon[ :,1:]), (lat[:  ,:-1],lon[:  ,:-1]) ))
        self.grid['dx'].attrs['standard_name'] = 'grid_edge_x_distance'
        self.grid['dx'].attrs['units'] = 'meters'
        self.grid['dx'].attrs['sha256'] = hashlib.sha256( np.array( self.grid['dx'] ) ).hexdigest()
        self.grid['dy'] = (('ny' , 'nxp'), R * spherical.angle_through_center( (lat[1:, :],lon[1:, :]), (lat[:-1,:  ],lon[:-1,:  ]) ))
        self.grid['dy'].attrs['standard_name'] = 'grid_edge_y_distance'
        self.grid['dy'].attrs['units'] = 'meters'
        self.grid['dy'].attrs['sha256'] = hashlib.sha256( np.array( self.grid['dy'] ) ).hexdigest()

        # Scaling by latitude?
        cos_lat = np.cos(np.radians(lat))

        # Presize the angle_dx array
        angle_dx = np.zeros(lat.shape)
        angle2_dx = np.zeros(lat.shape)

        # This was commented out in the original conversion code?
        #angle_dx[:,1:-1] = np.arctan2( (lat[:,2:] - lat[:,:-2]) , ((lon[:,2:] - lon[:,:-2]) * cos_lat[:,1:-1]) )
        #angle_dx[:, 0  ] = np.arctan2( (lat[:, 1] - lat[:, 0 ]) , ((lon[:, 1] - lon[:, 0 ]) * cos_lat[:, 0  ]) )
        #angle_dx[:,-1  ] = np.arctan2( (lat[:,-1] - lat[:,-2 ]) , ((lon[:,-1] - lon[:,-2 ]) * cos_lat[:,-1  ]) )

        # Fix lon so they are 0 to 360 for computation of angle_dx
        lon = np.where(lon < 0., lon+360, lon)
        angle2_dx[:,1:-1] = np.arctan2( (lat[:,2:] - lat[:,:-2]) , ((lon[:,2:] - lon[:,:-2]) * cos_lat[:,1:-1]) )
        angle2_dx[:, 0  ] = np.arctan2( (lat[:, 1] - lat[:, 0 ]) , ((lon[:, 1] - lon[:, 0 ]) * cos_lat[:, 0  ]) )
        angle2_dx[:,-1  ] = np.arctan2( (lat[:,-1] - lat[:,-2 ]) , ((lon[:,-1] - lon[:,-2 ]) * cos_lat[:,-1  ]) )
        self.grid['angle_dx'] = (('nyp', 'nxp'), np.maximum(angle_dx, angle2_dx))
        #self.grid.angle_dx.attrs['standard_name'] = 'grid_vertex_x_angle_WRT_geographic_east'
        #self.grid.angle_dx.attrs['units'] = 'degrees_east'
        self.grid['angle_dx'].attrs['units'] = 'radians'
        self.grid['angle_dx'].attrs['sha256'] = hashlib.sha256( np.array( angle_dx ) ).hexdigest()

        self.grid['area'] = (('ny','nx'), R * R * spherical.quad_area(lat, lon))
        self.grid['area'].attrs['standard_name'] = 'grid_cell_area'
        self.grid['area'].attrs['units'] = 'm2'
        self.grid['area'].attrs['sha256'] = hashlib.sha256( np.array( self.grid['area'] ) ).hexdigest()
        #breakpoint()

        return

    def formProjString(self, param):
        '''Create a projection string from parameter attributes.'''

        projString = None

        if 'projection' in param:
            if 'name' in param['projection']:
                if param['projection']['name'] == 'Mercator':
                    projString = "+proj=merc +lon_0=%s +x_0=0.0 +y_0=0.0 +no_defs" %\
                        (param['projection']['lon_0'])

                if param['projection']['name'] in ['NorthPolarStereo', 'SouthPolarStereo', 'Stereographic']:
                    true_scale_latitude = self.getGridParameter('lat_ts', subKey='projection', default=None)
                    if true_scale_latitude:
                        projString = "+proj=stere +lat_0=%s +lon_0=%s +lat_ts=%s +x_0=0.0 +y_0=0.0 +no_defs" %\
                            (param['projection']['lat_0'],
                            param['projection']['lon_0'],
                            param['projection']['lat_ts'])
                    else:
                        projString = "+proj=stere +lat_0=%s +lon_0=%s +x_0=0.0 +y_0=0.0 +no_defs" %\
                            (param['projection']['lat_0'],
                            param['projection']['lon_0'])

                if param['projection']['name'] == 'LambertConformalConic':
                    projString = "+proj=lcc +lon_0=%s +lat_0=%s +x_0=0.0 +y_0=0.0 +lat_1=%s +lat_2=%s +no_defs" %\
                        (param['projection']['lon_0'],
                        param['projection']['lat_0'],
                        param['projection']['lat_1'],
                        param['projection']['lat_2'])

                if projString:
                    if 'ellps' in param['projection']:
                        projString = "+ellps=%s %s" % (param['projection']['ellps'], projString)
                    else:
                        projString = "+ellps=%s %s" % (self._default_ellps, projString)
                        msg = "WARNING: Using default ellipse (%s)." % (self._default_ellps)
                        self.printMsg(msg, level=logging.WARNING)
                    if 'R' in param['projection']:
                        projString = "+R=%s %s" % (param['projection']['R'], projString)

        if projString == None:
            msg = "Unable to set projection string."
            self.printMsg(msg, level=logging.WARNING)
            self.debugMsg(msg)

        return projString

    def getXYDist(self, x1, y1, x2, y2):
        '''Compute distance between two points in x/y space.'''
    
        dst = math.sqrt(((x1-x2)*(x1-x2))+((y1-y2)*(y1-y2)))

        return dst

    def makeGrid(self, setFilename=None):
        '''Using supplied grid parameters, populate a grid in memory.'''

        # New grid created flag
        newGridCreated = False

        # PRESCREEN PARAMETERS

        # Review grid type
        gridType = self.getGridParameter('gridType', default='MOM6')
        if not(gridType in self._default_availableGridTypes):
            msg = 'ERROR: Grid type (%s) not supported.' % (gridType)
            self.printMsg(msg, level=logging.ERROR)
            return

        # MOM6 specific arguments
        gridMode = None
        ensureEvenI = None
        ensureEvenJ = None
        if gridType == 'MOM6':
            gridMode = self.getGridParameter('gridMode', default='2')
            gridMode = int(gridMode)

            ensureEvenI = self.getGridParameter('ensureEvenI', default=True)
            ensureEvenJ = self.getGridParameter('ensureEvenJ', default=True)

        # All grids must have centerX, centerY and centerUnits defined.
        centerX = self.getGridParameter('centerX', default='Error')
        centerY = self.getGridParameter('centerY', default='Error')
        centerUnits = self.getGridParameter('centerUnits', default='degrees')

        if centerX == 'Error' or centerY == 'Error':
            msg = 'ERROR: Grid parameter centerX or centerY missing.  These must be specified.'
            self.printMsg(msg, level=logging.ERROR)
            return

        centerX = float(centerX)
        centerY = float(centerY)

        if centerUnits == 'degrees':
            if centerX < 0.0 or centerX > 360.0:
                msg = 'ERROR: Grid parameter centerX must be +0.0 to +360.0.'
                self.printMsg(msg, level=logging.ERROR)
                return
            if centerY < -90.0 or centerY > 90.0:
                msg = 'ERROR: Grid parameter centerY must be -90.0 to +90.0.'
                self.printMsg(msg, level=logging.ERROR)
                return

        # The centerUnits will determine the geometry type for the grid
        if centerUnits == 'degrees':
            geometryType = 'spherical'
        else:
            geometryType = 'cartesian'

        # For MOM6, we set a default tile name
        tileName = self.getGridParameter('tileName', default='tile1')

        # Review dx and dy: these must be set
        dx = self.getGridParameter('dx', default='Error')
        dy = self.getGridParameter('dy', default='Error')
        if dx == 'Error' or dy == 'Error':
            msg = 'ERROR: Size of grid dx and dy must be defined.'
            self.printMsg(msg, level=logging.ERROR)
            return
        dx = float(dx)
        dy = float(dy)

        # Review the dxUnits and dyUnits parameters
        dxUnits = self.getGridParameter('dxUnits', default='degrees')
        dyUnits = self.getGridParameter('dyUnits', default='degrees')

        # Review gridResolution, gridResolutionX and gridResolutionY,
        #    gridResolutionUnits, gridResolutionXUnits and gridResolutionY
        # parameters

        # We suppress warning messages here and check these parameters later
        gridResolution = self.getGridParameter('gridResolution', default='Error', inform=False)
        gridResolutionX = self.getGridParameter('gridResolutionX', default='Error', inform=False)
        gridResolutionY = self.getGridParameter('gridResolutionY', default='Error', inform=False)

        # Emit warnings only if a parameter above is set.
        gridResolutionUnits = self.getGridParameter('gridResolutionUnits', default='degrees',
                inform=(gridResolution!='Error'))
        gridResolutionXUnits = self.getGridParameter('gridResolutionXUnits', default='degrees',
                inform=(gridResolutionX!='Error'))
        gridResolutionYUnits = self.getGridParameter('gridResolutionYUnits', default='degrees',
                inform=(gridResolutionY!='Error'))

        # Review tilt parameter
        tilt = float(self.getGridParameter('tilt', default="0.0"))

        # If gridResolution is not set, gridResolutionX and gridResolutionY must be set.  At
        # the end, gridResolutionX and gridResolutionY must have values either set from
        # their values or gridResolution.
        if gridResolution == 'Error':
            if gridResolutionX == 'Error' or gridResolutionY == 'Error':
                msg = 'ERROR: Grid parameter gridResolution or (gridResolutionX and gridResolutionY) must be set.'
                self.printMsg(msg, level=logging.ERROR)
                return
        else:
            if gridResolutionX == 'Error':
                gridResolutionX = float(gridResolution)
                gridResolutionXUnits = gridResolutionUnits
            else:
                gridResolutionX = float(gridResolutionX)
            if gridResolutionY == 'Error':
                gridResolutionY = float(gridResolution)
                gridResolutionYUnits = gridResolutionUnits
            else:
                gridResolutionY = float(gridResolutionY)

        # GRID GENERATION ROUTINES

        # Make a grid in the Mercator projection
        if self.gridInfo['gridParameters']['projection']['name'] == "Mercator":

            if gridType == 'MOM6':
                # This projection only supports degrees
                unsupported = False
                if dxUnits == 'meters':
                    unsupported = True
                if dyUnits == 'meters':
                    unsupported = True
                if unsupported:
                    msg = 'ERROR: Mercator grid parameters must be specified in degrees.'
                    self.printMsg(msg, level=logging.ERROR)
                    return

                # Tilt may not produce conformal Mercator
                if tilt > 0.0 or tilt < 0.0:
                    msg = "WARNING: Tilt of a mercator grid may not be conformal."
                    self.printMsg(msg, level=logging.WARNING)

                lonGrid, latGrid = self.generate_regional_mercator(
                    centerUnits, centerX, centerY,
                    dx, dxUnits,
                    dy, dyUnits,
                    tilt,
                    gridResolutionX, gridResolutionXUnits,
                    gridResolutionY, gridResolutionYUnits,
                    self.gridInfo['gridParameters']['projection'],
                    gridType=gridType,
                    gridMode=gridMode,
                    ensureEvenI=ensureEvenI,
                    ensureEvenJ=ensureEvenJ
                )

                if hasattr(lonGrid, 'shape'):
                    # Adjust lonGrid to -180 to +180
                    lonGrid = np.where(lonGrid > 180.0, lonGrid - 360.0, lonGrid)

                    (nxp, nyp) = lonGrid.shape

                    self.grid['x'] = (('nyp','nxp'), lonGrid)
                    self.grid['x'].attrs['standard_name'] = 'geographic_longitude'
                    self.grid['x'].attrs['units'] = 'degrees_east'
                    self.grid['x'].attrs['sha256'] = hashlib.sha256( np.array( lonGrid ) ).hexdigest()
                    self.grid['y'] = (('nyp','nxp'), latGrid)
                    self.grid['y'].attrs['standard_name'] = 'geographic_latitude'
                    self.grid['y'].attrs['units'] = 'degrees_north'
                    self.grid['y'].attrs['sha256'] = hashlib.sha256( np.array( latGrid ) ).hexdigest()

                    newGridCreated = True

        # Make a grid in the Stereographic projection (this should support north and south pole)
        if self.gridInfo['gridParameters']['projection']['name'] == "Stereographic":

            if dxUnits == "Error" or dyUnits == "Error":
                msg = 'ERROR: Stereographic grid parameters, dx and/or dy, must be specified in degrees or meters.'
                self.printMsg(msg, level=logging.ERROR)
                return

            if dxUnits != dyUnits:
                msg = 'ERROR: Stereographic grid parameters, dx and dy, units must match.'
                self.printMsg(msg, level=logging.ERROR)
                return

            if gridType == 'MOM6':
                # Units = meters
                if dxUnits == 'meters':
                    lonGrid, latGrid = self.generate_regional_spherical_meters(
                        centerUnits, centerX, centerY,
                        dx, dxUnits,
                        dy, dyUnits,
                        tilt,
                        gridResolutionX, gridResolutionXUnits,
                        gridResolutionY, gridResolutionYUnits,
                        self.gridInfo['gridParameters']['projection'],
                        gridType=gridType,
                        gridMode=gridMode,
                        ensureEvenI=ensureEvenI,
                        ensureEvenJ=ensureEvenJ
                    )

                    if hasattr(lonGrid, 'shape'):
                        # Adjust lonGrid to -180 to +180
                        lonGrid = np.where(lonGrid > 180.0, lonGrid - 360.0, lonGrid)

                        (nxp, nyp) = lonGrid.shape

                        self.grid['x'] = (('nyp','nxp'), lonGrid)
                        self.grid.x.attrs['standard_name'] = 'geographic_longitude'
                        self.grid.x.attrs['units'] = 'degrees_east'
                        self.grid.x.attrs['sha256'] = hashlib.sha256( np.array( lonGrid ) ).hexdigest()
                        self.grid['y'] = (('nyp','nxp'), latGrid)
                        self.grid.y.attrs['standard_name'] = 'geographic_latitude'
                        self.grid.y.attrs['units'] = 'degrees_north'
                        self.grid.y.attrs['sha256'] = hashlib.sha256( np.array( latGrid ) ).hexdigest()

                        newGridCreated = True
                    
                # Units = degrees
                if dxUnits == 'degrees':
                    msg = "WARNING: Spherical grids specified in degrees may not be conformal."
                    self.printMsg(msg, level=logging.WARNING)
                    
                    lonGrid, latGrid = self.generate_regional_spherical_degrees(
                        centerUnits, centerX, centerY,
                        dx, dxUnits,
                        dy, dyUnits,
                        tilt,
                        gridResolutionX, gridResolutionXUnits,
                        gridResolutionY, gridResolutionYUnits,
                        self.gridInfo['gridParameters']['projection'],
                        gridType=gridType,
                        gridMode=gridMode,
                        ensureEvenI=ensureEvenI,
                        ensureEvenJ=ensureEvenJ
                    )

                    if hasattr(lonGrid, 'shape'):
                        # Adjust lonGrid to -180 to +180
                        lonGrid = np.where(lonGrid > 180.0, lonGrid - 360.0, lonGrid)

                        (nxp, nyp) = lonGrid.shape

                        self.grid['x'] = (('nyp','nxp'), lonGrid)
                        self.grid.x.attrs['standard_name'] = 'geographic_longitude'
                        self.grid.x.attrs['units'] = 'degrees_east'
                        self.grid.x.attrs['sha256'] = hashlib.sha256( np.array( lonGrid ) ).hexdigest()
                        self.grid['y'] = (('nyp','nxp'), latGrid)
                        self.grid.y.attrs['standard_name'] = 'geographic_latitude'
                        self.grid.y.attrs['units'] = 'degrees_north'
                        self.grid.y.attrs['sha256'] = hashlib.sha256( np.array( latGrid ) ).hexdigest()

                        newGridCreated = True
                    
        # Make a grid in the North Polar Stereo projection
        if self.gridInfo['gridParameters']['projection']['name'] == "NorthPolarStereo":

            lonGrid, latGrid = self.generate_regional_spherical(
                self.gridInfo['gridParameters']['projection']['lon_0'], self.gridInfo['gridParameters']['dx'],
                self.gridInfo['gridParameters']['projection']['lat_0'], self.gridInfo['gridParameters']['dy'],
                tilt,
                self.gridInfo['gridParameters']['gridResolution'], self.gridInfo['gridParameters']['gridMode']
            )
            # Adjust lonGrid to -180 to +180
            lonGrid = np.where(lonGrid > 180.0, lonGrid - 360.0, lonGrid)

            (nxp, nyp) = lonGrid.shape

            self.grid['x'] = (('nyp','nxp'), lonGrid)
            self.grid.x.attrs['standard_name'] = 'geographic_longitude'
            self.grid.x.attrs['units'] = 'degrees_east'
            self.grid.x.attrs['sha256'] = hashlib.sha256( np.array( lonGrid ) ).hexdigest()
            self.grid['y'] = (('nyp','nxp'), latGrid)
            self.grid.y.attrs['standard_name'] = 'geographic_latitude'
            self.grid.y.attrs['units'] = 'degrees_north'
            self.grid.y.attrs['sha256'] = hashlib.sha256( np.array( latGrid ) ).hexdigest()

            newGridCreated = True


        # Make a grid in the South Polar Stereo projection
        if self.gridInfo['gridParameters']['projection']['name'] == "SouthPolarStereo":
            if 'tilt' in self.gridInfo['gridParameters'].keys():
                tilt = self.gridInfo['gridParameters']['tilt']
            else:
                tilt = 0.0

            lonGrid, latGrid = self.generate_regional_spherical(
                self.gridInfo['gridParameters']['projection']['lon_0'], self.gridInfo['gridParameters']['dx'],
                self.gridInfo['gridParameters']['projection']['lat_0'], self.gridInfo['gridParameters']['dy'],
                tilt,
                self.gridInfo['gridParameters']['gridResolution'], self.gridInfo['gridParameters']['gridMode']
            )
            # Adjust lonGrid to -180 to +180
            lonGrid = np.where(lonGrid > 180.0, lonGrid - 360.0, lonGrid)

            (nxp, nyp) = lonGrid.shape

            self.grid['x'] = (('nyp','nxp'), lonGrid)
            self.grid.x.attrs['standard_name'] = 'geographic_longitude'
            self.grid.x.attrs['units'] = 'degrees_east'
            self.grid.x.attrs['sha256'] = hashlib.sha256( np.array( lonGrid ) ).hexdigest()
            self.grid['y'] = (('nyp','nxp'), latGrid)
            self.grid.y.attrs['standard_name'] = 'geographic_latitude'
            self.grid.y.attrs['units'] = 'degrees_north'
            self.grid.y.attrs['sha256'] = hashlib.sha256( np.array( latGrid ) ).hexdigest()

            newGridCreated = True

        # Make a grid in the Lambert Conformal Conic projection
        if self.gridInfo['gridParameters']['projection']['name'] == 'LambertConformalConic':
            
            # This projection only supports degrees at the moment
            try:
                unsupported = False
                if dxUnits == 'meters':
                    unsupported = True
                if dyUnits == 'meters':
                    unsupported = True
                if unsupported:
                    msg = 'ERROR: Lambert Conformal Conic grid parameters must be specified in degrees.'
                    self.printMsg(msg, level=logging.ERROR)
                    return
            except:
                # Default units are degrees
                pass
            
            # Sometimes tilt may not be specified, so use a default of 0.0
            if 'tilt' in self.gridInfo['gridParameters'].keys():
                tilt = self.gridInfo['gridParameters']['tilt']
            else:
                tilt = 0.0

            #lonGrid, latGrid = self.generate_regional_spherical(
            #    self.gridInfo['gridParameters']['projection']['lon_0'], self.gridInfo['gridParameters']['dx'],
            #    self.gridInfo['gridParameters']['projection']['lat_0'], self.gridInfo['gridParameters']['dy'],
            #    tilt,
            #    self.gridInfo['gridParameters']['gridResolution'], self.gridInfo['gridParameters']['gridMode']
            #)
            
            lonGrid, latGrid = self.generate_regional_spherical_degrees(
                        centerUnits, centerX, centerY,
                        dx, dxUnits,
                        dy, dyUnits,
                        tilt,
                        gridResolutionX, gridResolutionXUnits,
                        gridResolutionY, gridResolutionYUnits,
                        self.gridInfo['gridParameters']['projection'],
                        gridType=gridType,
                        gridMode=gridMode,
                        ensureEvenI=ensureEvenI,
                        ensureEvenJ=ensureEvenJ
                    )
            
            # Adjust lonGrid to -180 to +180
            lonGrid = np.where(lonGrid > 180.0, lonGrid - 360.0, lonGrid)

            (nxp, nyp) = lonGrid.shape

            self.grid['x'] = (('nyp','nxp'), lonGrid)
            self.grid.x.attrs['standard_name'] = 'geographic_longitude'
            self.grid.x.attrs['units'] = 'degrees_east'
            self.grid.x.attrs['sha256'] = hashlib.sha256( np.array( lonGrid ) ).hexdigest()
            self.grid['y'] = (('nyp','nxp'), latGrid)
            self.grid.y.attrs['standard_name'] = 'geographic_latitude'
            self.grid.y.attrs['units'] = 'degrees_north'
            self.grid.y.attrs['sha256'] = hashlib.sha256( np.array( latGrid ) ).hexdigest()

            # This technique seems to return a Lambert Conformal Projection with the following properties
            # This only works if the grid does not overlap a polar point
            # (lat_0 - (dy/2), lat_0 + (dy/2))
            self.gridInfo['gridParameters']['projection']['lat_1'] =\
                self.gridInfo['gridParameters']['projection']['lat_0'] - (self.gridInfo['gridParameters']['dy'] / 2.0)
            self.gridInfo['gridParameters']['projection']['lat_2'] =\
                self.gridInfo['gridParameters']['projection']['lat_0'] + (self.gridInfo['gridParameters']['dy'] / 2.0)
            
            newGridCreated = True

        if newGridCreated:
            # Fill in a tile name and geometry
            self.grid['tile'] = tileName
            self.grid.tile['geometry'] = geometryType

            # Generate a proj string
            try:
                projString = self.formProjString(self.gridInfo['gridParameters'])
                if projString:
                    self.gridInfo['gridParameters']['projection']['proj'] = projString
                else:
                    msg = "WARNING: Projection string could not be determined from grid parameters."
                    self.printMsg(msg, level=logging.WARNING)
            except:
                msg = "WARNING: Projection string could not be determined from grid parameters."
                self.printMsg(msg, level=logging.WARNING)
                self.debugMsg('')            

            # Declare the xarray dataset open even though it is really only in memory at this point
            self.xrOpen = True

            # Compute grid metrics
            if gridType == 'MOM6':
                if gridMode == 2:
                    self.computeGridMetricsSpherical()
                else:
                    msg = "NOTE: Grid metrics were not computed."
                    self.printMsg(msg, level=logging.INFO)
        else:
            msg = "WARNING: Grid generation failed."
            self.printMsg(msg, level=logging.WARNING)

        # If the grid was just created, the user can provide using setFilename
        if setFilename:
            self.xrFilename = setFilename
                                
    # Original grid generation functions from Niki Zadeh
    # Replace above comment with attribution in each function to mark lineage

    # Mercator
    def rotate_u(self, x , y, z, ux, uy, uz, theta):
        """Rotate by angle :math:`\\theta` around a general axis (ux,uy,uz)."""
        c=np.cos(theta)
        s=np.sin(theta)

        #Normalize, u must be a unit vector for this to work
        unorm=np.sqrt(ux*ux+uy*uy+uz*uz)
        ux=ux/unorm
        uy=uy/unorm
        uz=uz/unorm

        r11=c+(1-c)*ux*ux
        r22=c+(1-c)*uy*uy
        r33=c+(1-c)*uz*uz

        r12=(1-c)*ux*uy-s*uz
        r21=(1-c)*ux*uy+s*uz

        r13=(1-c)*ux*uz+s*uy
        r31=(1-c)*ux*uz-s*uy

        r23=(1-c)*uy*uz-s*ux
        r32=(1-c)*uy*uz+s*ux

        xp= r11*x+r12*y+r13*z
        yp= r21*x+r22*y+r23*z
        zp= r31*x+r32*y+r33*z
        return xp,yp,zp

    def rotate_u_mesh(self, lam, phi, ux, uy, uz, theta):
        #Bring the angle to be in [-pi,pi] so that atan2 would work
        lam = np.where(lam>180,lam-360,lam)
        #Change to Cartesian coord
        x,y,z = self.pol2cart(lam,phi)
        #Rotate
        xp,yp,zp = self.rotate_u(x,y,z,ux,uy,uz,theta)
        #Change back to polar coords using atan2, in [-pi,pi]
        lamp,phip = self.cart2pol(xp,yp,zp)
        #Bring the angle back to be in [0,2*pi]
        lamp = np.where(lamp<0,lamp+360,lamp)
        return lamp,phip

    def generate_rotated_grid(self, lon0, lon_span, lat0, lat_span, tilt, refine):
        Ni = int(lon_span*refine)
        Nj = int(lat_span*refine)

        #Generate a mesh at equator centered at (lon0, lat0)
        lam_,phi_ = self.generate_latlon_mesh_centered(Ni,Nj,lon0,lon_span,lat0,lat_span)
        ux,uy,uz  = self.pol2cart(lon0,lat0)
        lam_,phi_ = self.rotate_u_mesh(lam_,phi_, ux,uy,uz, tilt*self.PI_180)  #rotate mesh around u by theta
        return lam_,phi_

    # Lambert Conformal Conic and Stereographic grids
    # Grid creation and rotation in spherical coordinates
    def mesh_plot(self, lon, lat, lon0=0., lat0=90.):
        """Plot a given mesh with a perspective centered at (lon0,lat0)"""
        f = plt.figure(figsize=(8,8))
        ax = plt.subplot(111, projection=cartopy.crs.NearsidePerspective(central_longitude=lon0, central_latitude=lat0))
        ax.set_global()
        ax.stock_img()
        ax.coastlines()
        ax.gridlines()
        (nj,ni) = lon.shape 
        # plotting vertices
        for i in range(0,ni+1,2):
            ax.plot(lon[:,i], lat[:,i], 'k', transform=cartopy.crs.Geodetic())
        for j in range(0,nj+1,2):
            ax.plot(lon[j,:], lat[j,:], 'k', transform=cartopy.crs.Geodetic())

        return f, ax

    def rotate_x(self, x, y, z, theta):
        """Rotate vector (x,y,z) by angle theta around x axis."""
        """Returns the rotated components."""
        cost = np.cos(theta)
        sint = np.sin(theta)
        yp   = y*cost - z*sint
        zp   = y*sint + z*cost
        return x,yp,zp

    def rotate_y(self, x, y, z, theta):
        """Rotate vector (x,y,z) by angle theta around y axis."""
        """Returns the rotated components."""
        cost = np.cos(theta)
        sint = np.sin(theta)
        zp   = z*cost - x*sint
        xp   = z*sint + x*cost
        return xp,y,zp

    def rotate_z(self, x, y, z, theta):
        """Rotate vector (x,y,z) by angle theta around z axis."""
        """Returns the rotated components."""
        cost = np.cos(theta)
        sint = np.sin(theta)
        xp   = x*cost - y*sint
        yp   = x*sint + y*cost
        return xp,yp,z

    def cart2pol(self, x, y, z):
        """Transform a point on globe from Cartesian (x,y,z) to polar coordinates."""
        """Returns the polar coordinates"""
        lam=np.arctan2(y,x)/self.PI_180
        phi=np.arctan(z/np.sqrt(x**2+y**2))/self.PI_180
        return lam,phi

    def pol2cart(self, lam, phi):
        """Transform a point on globe from Polar (lam,phi) to Cartesian coordinates."""
        """Returns the Cartesian coordinates"""
        lam = lam * self.PI_180
        phi = phi * self.PI_180
        x   = np.cos(phi) * np.cos(lam)
        y   = np.cos(phi) * np.sin(lam)
        z   = np.sin(phi)
        return x,y,z

    def rotate_z_mesh(self, lam, phi, theta):
        """Rotate the whole mesh on globe by angle theta around z axis (globe polar axis)."""
        """Returns the rotated mesh."""
        #Bring the angle to be in [-pi,pi] so that atan2 would work
        lam       = np.where(lam>180, lam-360, lam)
        #Change to Cartesian coord
        x,y,z     = self.pol2cart(lam, phi)
        #Rotate
        xp,yp,zp  = self.rotate_z(x, y, z, theta)
        #Change back to polar coords using atan2, in [-pi,pi]
        lamp,phip = self.cart2pol(xp, yp, zp)
        #Bring the angle back to be in [0,2*pi]
        lamp      = np.where(lamp<0, lamp+360, lamp)
        return lamp,phip

    def rotate_x_mesh(self, lam, phi, theta):
        """Rotate the whole mesh on globe by angle theta around x axis (passing through equator and prime meridian.)."""
        """Returns the rotated mesh."""
        #Bring the angle to be in [-pi,pi] so that atan2 would work
        lam       = np.where(lam>180, lam-360, lam)
        #Change to Cartesian coord
        x,y,z     = self.pol2cart(lam, phi)
        #Rotate
        xp,yp,zp  = self.rotate_x(x, y, z, theta)
        #Change back to polar coords using atan2, in [-pi,pi]
        lamp,phip = self.cart2pol(xp, yp, zp)
        #Bring the angle back to be in [0,2*pi]
        lamp      = np.where(lamp<0, lamp+360, lamp)
        return lamp,phip

    def rotate_y_mesh(self, lam, phi, theta):
        """Rotate the whole mesh on globe by angle theta around y axis (passing through equator and prime meridian+90.)."""
        """Returns the rotated mesh."""
        #Bring the angle to be in [-pi,pi] so that atan2 would work
        lam       = np.where(lam>180, lam-360, lam)
        #Change to Cartesian coord
        x,y,z     = self.pol2cart(lam, phi)
        #Rotate
        xp,yp,zp  = self.rotate_y(x, y, z, theta)
        #Change back to polar coords using atan2, in [-pi,pi]
        lamp,phip = self.cart2pol(xp, yp, zp)
        #Bring the angle back to be in [0,2*pi]
        lamp      = np.where(lamp<0, lamp+360, lamp)
        return lamp,phip

    #def generate_latlon_mesh_centered(self, lni, lnj, llon0, llen_lon, llat0, llen_lat, ensure_nj_even=True):
    def generate_latlon_mesh_centered(self, lni, lnj, llon0, llen_lon, llat0, llen_lat, **kwargs):
        """Generate a regular lat-lon grid"""
        ensure_ni_even = True
        ensure_nj_even = True
        if 'ensureEvenI' in kwargs.keys():
            ensure_ni_even = kwargs['ensureEvenI']
        if 'ensureEvenJ' in kwargs.keys():
            ensure_nj_even = kwargs['ensureEvenJ']
        
        if llat0 == 0.0:
            msg = 'Generating regular lat-lon grid centered at (%.2f, %.2f) on equator.' % (llon0, llat0)
        else:
            msg = 'Generating regular lat-lon grid centered at (%.2f %.2f).' % (llon0, llat0)
        self.printMsg(msg, level=logging.INFO)
        llonSP = llon0 - llen_lon/2 + np.arange(lni+1) * llen_lon/float(lni)
        llatSP = llat0 - llen_lat/2 + np.arange(lnj+1) * llen_lat/float(lnj)
        # TODO: add ensure_ni_even to clip columns
        if(llatSP.shape[0]%2 == 0 and ensure_nj_even):
            msg = "   The number of j's is not even. Fixing this by cutting one row at south."
            self.printMsg(msg, level=logging.INFO)
            llatSP = np.delete(llatSP, 0, 0)
        llamSP = np.tile(llonSP,(llatSP.shape[0], 1))
        lphiSP = np.tile(llatSP.reshape((llatSP.shape[0], 1)), (1, llonSP.shape[0]))
        msg = '   Generated regular lat-lon grid between latitudes %.2f %.2f' % (lphiSP[0,0], lphiSP[-1,0])
        self.printMsg(msg, level=logging.INFO)
        msg = '   Number of js=%d' % (lphiSP.shape[0])
        self.printMsg(msg, level=logging.INFO)
        #h_i_inv=llen_lon*self.PI_180*np.cos(lphiSP*self.PI_180)/lni
        #h_j_inv=llen_lat*self.PI_180*np.ones(lphiSP.shape)/lnj
        #delsin_j = np.roll(np.sin(lphiSP*self.PI_180),shift=-1,axis=0) - np.sin(lphiSP*self.PI_180)
        #dx_h=h_i_inv[:,:-1]*self._default_Re
        #dy_h=h_j_inv[:-1,:]*self._default_Re
        #area=delsin_j[:-1,:-1]*self._default_Re*self._default_Re*llen_lon*self.self.PI_180/lni
        return llamSP,lphiSP

    def generate_regional_spherical(self, lon0, lon_span, lat0, lat_span, tilt, gRes, gMode):
        """Generate a regional grid centered at (lon0,lat0) with spans of (lon_span,lat_span) and tilted by angle tilt"""
        
        Ni = int(lon_span / gRes)
        Nj = int(lat_span / gRes)
        if gMode == 2:
            # Supergrid requested
            Ni = Ni * 2
            Nj = Nj * 2

        # Generate a mesh at equator centered at (lon0, 0)
        lam_,phi_ = self.generate_latlon_mesh_centered(Ni, Nj, lon0, lon_span, 0.0, lat_span)
        lam_,phi_ = self.rotate_z_mesh(lam_,phi_, (90.-lon0)*self.PI_180)   #rotate around z to bring it centered at y axis
        lam_,phi_ = self.rotate_y_mesh(lam_,phi_, tilt*self.PI_180)         #rotate around y axis to tilt it as desired
        lam_,phi_ = self.rotate_x_mesh(lam_,phi_, lat0*self.PI_180)         #rotate around x to bring it centered at (lon0,lat0)
        lam_,phi_ = self.rotate_z_mesh(lam_,phi_, -(90.-lon0)*self.PI_180)  #rotate around z to bring it back

        return lam_,phi_

    # Similar to Niki's generate_rotated_grid function
    #def generate_regional_mercator(self, lon0, lon_span, lat0, lat_span, tilt, gRes, gMode):
    def generate_regional_mercator(self, cUnits, cX, cY, dx, dxU, dy, dyU, tilt, grX, grXU, grY, grYU, pD, **kwargs):
        """Generate a regional mercator grid centered at (cX, cY) with spans of (dx, dy) with resolution (grX, grY) and tilted by angle tilt"""
        
        gType = None
        if 'gridType' in kwargs.keys():
            gType = kwargs['gridType']

        lam_ = None
        phi_ = None
            
        if gType == "MOM6":
            ensureEvenI = True
            ensureEvenJ = True
            if 'ensureEvenI' in kwargs.keys():
                ensureEvenI = kwargs['ensureEvenI']
            if 'ensureEvenJ' in kwargs.keys():
                ensureEvenJ = kwargs['ensureEvenJ']

            Ni = int(dx / grX)
            Nj = int(dy / grY)

            gMode = 1
            if 'gridMode' in kwargs.keys():
                gMode = kwargs['gridMode']
            if gMode == 2:
                # Supergrid requested
                Ni = Ni * 2
                Nj = Nj * 2

            # Generate a mesh centered at (lon0, lat0) -> (cX, cY)
            #lam_,phi_ = self.generate_latlon_mesh_centered(Ni, Nj, lon0, lon_span, lat0, lat_span)
            lam_,phi_  = self.generate_latlon_mesh_centered(Ni, Nj, cX, dx, cY, dy, ensureEvenI=ensureEvenI, ensureEvenJ=ensureEvenJ)
            ux, uy, uz = self.pol2cart(cX, cY)
            # Rotate mesh around u by theta
            lam_,phi_  = self.rotate_u_mesh(lam_, phi_, ux, uy, uz, tilt*self.PI_180)

        if not(hasattr(lam_, 'shape')):
            msg = 'ERROR: Failed to create mercator grid!'
            self.printMsg(msg, level=logging.ERROR)
            
        return lam_,phi_

    # Rebuilt grid generation routines
    
    def generate_regional_spherical_meters(self, cUnits, cX, cY, dx, dxU, dy, dyU, tilt, grX, grXU, grY, grYU, pD, **kwargs):
        '''Create a grid in the spherical projection using grid distances in meters.

        This function uses code that performs projection transformation of 2D grids. :cite:p:`Dussin_2020_regrid_weights_bedmachine_gebco`
        '''

        gType = None
        if 'gridType' in kwargs.keys():
            gType = kwargs['gridType']

        lam_ = None
        phi_ = None
        
        if gType == "MOM6":
            ensureEvenI = True
            ensureEvenJ = True
            if 'ensureEvenI' in kwargs.keys():
                ensureEvenI = kwargs['ensureEvenI']
            if 'ensureEvenJ' in kwargs.keys():
                ensureEvenJ = kwargs['ensureEvenJ']
            
            PROJSTRING = "+proj=stere"
            if 'lat_0' in pD.keys():
                PROJSTRING = "%s +lat_0=%f" % (PROJSTRING, pD['lat_0'])
            if 'lat_ts' in pD.keys():
                PROJSTRING = "%s +lat_ts=%f" % (PROJSTRING, pD['lat_ts'])
            if 'ellps' in pD.keys():
                PROJSTRING = "%s +ellps=%s" % (PROJSTRING, pD['ellps'])
            if 'R' in pD.keys():
                PROJSTRING = "%s +R=%f" % (PROJSTRING, pD['R'])

            msg = 'Transformation proj string(%s)' % (PROJSTRING)
            self.printMsg(msg, level=logging.INFO)                

            # create the coordinate reference system
            crs = CRS.from_proj4(PROJSTRING)
            # create the projection from lon/lat to x/y
            proj = Transformer.from_crs(crs.geodetic_crs, crs)

            # compute (x, y) from (lon, lat)
            gX, gY = proj.transform(cX, cY)
            msg = 'Computing center point in meters: (%f, %f) to (%f, %f)' % (cY, cX, gX, gY)
            self.printMsg(msg, level=logging.INFO)                

            gMode = 1
            if 'gridMode' in kwargs.keys():
                gMode = kwargs['gridMode']
            if gMode == 2:
                # Supergrid requested
                grX = grX / 2.0
                grY = grY / 2.0

            # Grid is centered on gX, gY
            # gX - halfDX to gX + halfDX increments of grX
            # gY - halfDY to gY + halfDY increments of grY
            # Due to the way ranges work in python, we have to add another increment
            # to the end to ensure we have the point that includes what we need.
            halfDX = dx / 2.0
            halfDY = dy / 2.0

            x = np.arange(gX - halfDX, (gX + halfDX) + grX, grX, dtype=np.float32)
            y = np.arange(gY - halfDY, (gY + halfDY) + grY, grY, dtype=np.float32)

            yy, xx = np.meshgrid(y, x)

            # compute (lon, lat) from (x, y)
            # Works for northern hemisphere
            if pD['lat_0'] == 90.0:
                lon, lat = proj.transform(yy, xx, direction='INVERSE')
            # Works for southern hemisphere
            if pD['lat_0'] == -90.0:
                lon, lat = proj.transform(xx, yy, direction='INVERSE')

            lam_ = lon
            phi_ = lat
        
        return lam_,phi_

    def generate_regional_spherical_degrees(self, cUnits, cX, cY, dx, dxU, dy, dyU, tilt, grX, grXU, grY, grYU, pD, **kwargs):
        '''Create a grid in the spherical projection using grid distances in degrees.'''
        
        gType = None
        if 'gridType' in kwargs.keys():
            gType = kwargs['gridType']

        lam_ = None
        phi_ = None
        
        if gType == "MOM6":
            ensureEvenI = True
            ensureEvenJ = True
            if 'ensureEvenI' in kwargs.keys():
                ensureEvenI = kwargs['ensureEvenI']
            if 'ensureEvenJ' in kwargs.keys():
                ensureEvenJ = kwargs['ensureEvenJ']

            Ni = int(dx / grX)
            Nj = int(dy / grY)

            gMode = 1
            if 'gridMode' in kwargs.keys():
                gMode = kwargs['gridMode']
            if gMode == 2:
                # Supergrid requested
                Ni = Ni * 2
                Nj = Nj * 2
                
            # Generate a mesh at equator centered at (lon0, 0)
            lam_,phi_ = self.generate_latlon_mesh_centered(Ni, Nj, cX, dx, 0.0, dy)
            lam_,phi_ = self.rotate_z_mesh(lam_, phi_, (90.-cX)*self.PI_180)   #rotate around z to bring it centered at y axis
            lam_,phi_ = self.rotate_y_mesh(lam_, phi_, tilt*self.PI_180)       #rotate around y axis to tilt it as desired
            lam_,phi_ = self.rotate_x_mesh(lam_, phi_, cY*self.PI_180)         #rotate around x to bring it centered at (lon0,lat0)
            lam_,phi_ = self.rotate_z_mesh(lam_, phi_, -(90.-cX)*self.PI_180)  #rotate around z to bring it back
        
        return lam_,phi_

    # xarray grid operations grid functions
    # Xarray Grid Operations Grid Functions
    
    def closeGrid(self):
        '''Closes and open dataset file pointer.'''
        if self.xrOpen:
            self.xrDS.close()
            self.xrOpen = False

    def convertGrid(self, target, **kwargs):
        '''Convert current grid to another grid type.

        :param target: name of new grid format
        :type target: string
        :return: none
        :rtype: none

        Supported grid conversions:
            +--------+--------+---------------------------------------------------+
            | SOURCE | TARGET | CODE CITATIONS                                    |
            +--------+--------+---------------------------------------------------+
            | ROMS   | MOM6   | :cite:p:`Ilicak_2020_ROMS_to_MOM6`                |
            +--------+--------+---------------------------------------------------+

        **Keyword arguments**:

            * *writeTopography* (``boolean``) -- set True to write topographic grid to a file. Default: False
            * *topographyFilename* (``string``) -- filename used to write topographic grid. Default: "ocean_topog.nc"
            * *writeMosaic* (``boolean``) -- set True to write the mosaic file. Default: False
            * *mosaicFilename* (``string``) -- filename for mosaic file. Default: "ocean_mosaic.nc"
            * *oceanGridFilename* (``string``) -- filename for ocean grid file. Default: "ocean_hgrid.nc"
            * *writeLandmask* (``boolean``) -- set True to write land mask file. Default: False
            * *landmaskFilename* (``string``) -- filename used to write the land mask. Default: "land_mask.nc"
            * *writeOceanmask* (``boolean``) -- set True to write ocean mask file. Default: False
            * *oceanmaskFilename* (``string``) -- filename used to write the ocean mask. Default: "ocean_mask.nc"
            * *tileName* (``string``) -- name to assign to the solo tile. Default: "tile1"
            * *MINIMUM_DEPTH* (``float``) -- minimum depth of ocean in meters. Default: 0.0
            * *MASKING_DEPTH* (``float``) -- masking depth of ocean in meters. Default: 0.0
            * *MAXIMUM_DEPTH* (``float``) -- maximum depth of ocean in meters. Default: -99999.0
            * *writeCouplerMosaic* (``boolean``) -- set False to skip creation of coupler mosaic file. Default: False
            * *couplerMosaicFilename* (``string``) -- set False to skip creation of coupler mosaic file. Default: "mosaic.nc"
            * *writeExchangeGrids* (``boolean``) -- set False to skip creation of exchange grids. Default: False
            * *overwrite* (``boolean``) -- set True to overwrite existing files. Default: False
            * *inputDirectory* (``string``) -- absolute or relative path to write model input files. Default: "INPUT"
            * *relativeToINPUTDir* (``string``) -- absolute or relative path for mosaic files to the INPUT directory. Default: "./"

        **Keyword arguments (ROMS)**:

            * *topographyVariable* (``string``) -- grid name for ROMS topography containing depths.  Some ROMS
              grids also contain a `hraw` which might be useful. Default: h

        .. note::

            In the original ROMS to MOM6 conversion script, any land mask points are masked to a depth of zero(0).
            This version sets the depth to the `MASKING_DEPTH`.  If the mask or clamping depth is known from the
            ROMS grid, please set `MASKING_DEPTH` appropriately or the land mask depths will be set to zero(0)
            which is the default.
        '''

        # Define the two parameters we need to perform a conversion
        sourceGrid = None
        targetGrid = None

        if not('type' in self.gridInfo.keys()):
            msg = ('ERROR: No current grid defined.  Please create or read a grid before converting.')
            self.printMsg(msg, level=logging.ERROR)
            return

        # Match source grids first, then the available targets
        if self.gridInfo['type'] == 'ROMS':
            sourceGrid = self.gridInfo['type']
            if target in ['MOM6']:
                targetGrid = target

        if not(sourceGrid) or not(targetGrid):
            msg = ('ERROR: The source grid (%s) is not supported or is incompatible with the target grid (%s).' %\
                (sourceGrid, target))
            self.printMsg(msg, level=logging.ERROR)
            return

        # Import source and target grid module types
        sourceGridModule = sourceGrid.lower()
        targetGridModule = targetGrid.lower()

        try:
            mdlSource = importlib.import_module('gridtools.grids.%s' % (sourceGridModule))
        except:
            msg = ('ERROR: Failed to load grid module for %s.' % (sourceGrid))
            self.printMsg(msg, level=logging.ERROR)
            return

        try:
            mdlTarget = importlib.import_module('gridtools.grids.%s' % (targetGridModule))
        except:
            msg = ('ERROR: Failed to load grid module for %s.' % (targetGrid))
            self.printMsg(msg, level=logging.ERROR)
            return

        # Check and set any defaults to kwargs
        utils.checkArgument(kwargs, 'writeTopography', False)
        utils.checkArgument(kwargs, 'topographyFilename', "ocean_topog.nc")
        utils.checkArgument(kwargs, 'writeMosaic', False)
        utils.checkArgument(kwargs, 'mosaicFilename', "ocean_mosaic.nc")
        utils.checkArgument(kwargs, 'oceanGridFilename', "ocean_hgrid.nc")
        utils.checkArgument(kwargs, 'writeLandmask', False)
        utils.checkArgument(kwargs, 'landmaskFilename', "land_mask.nc")
        utils.checkArgument(kwargs, 'writeOceanmask', False)
        utils.checkArgument(kwargs, 'oceanmaskFilename', "ocean_mask.nc")
        utils.checkArgument(kwargs, 'tileName', "tile1")
        utils.checkArgument(kwargs, 'MINIMUM_DEPTH', 0.0)
        utils.checkArgument(kwargs, 'MASKING_DEPTH', -9999.0)
        utils.checkArgument(kwargs, 'MAXIMUM_DEPTH', 99999.0)
        utils.checkArgument(kwargs, 'writeExchangeGrids', False)
        utils.checkArgument(kwargs, 'writeCouplerMosaic', False)
        utils.checkArgument(kwargs, 'couplerMosaicFilename', "mosaic.nc")
        utils.checkArgument(kwargs, 'overwrite', False)
        utils.checkArgument(kwargs, 'inputDirectory', "INPUT")
        utils.checkArgument(kwargs, 'relativeToINPUTDir', "./")

        # ROMS specific kwargs
        utils.checkArgument(kwargs, 'topographyVariable', 'h')

        # Sanity checks for *_DEPTH arguments
        if kwargs['MASKING_DEPTH'] > kwargs['MINIMUM_DEPTH']:
            msg = ('WARNING: convertGrid: MASKING_DEPTH is deeper than MINIMUM_DEPTH and therefore ignored.')
            self.printMsg(msg, level=logging.WARNING)
            kwargs['MASKING_DEPTH'] = -9999.0
        if not(sanity.saneDepthOptions(**kwargs)):
            msg = ('ERROR: Invalid *_DEPTH options passed. (MAXIMUM_DEPTH(%f) >= MINIMUM_DEPTH(%f) >= MASKING_DEPTH(%f))' %\
                (kwargs['MAXIMUM_DEPTH'], kwargs['MINIMUM_DEPTH'], kwargs['MASKING_DEPTH']))
            self.printMsg(msg, level=logging.INFO)
            return

        # Create a templating mechanism later, for now perform direct calls into each
        # model type based on current grid type and target.

        # ROMS to MOM6: :cite:p:`Ilicak_2020_ROMS_to_MOM6`
        if sourceGrid == 'ROMS' and targetGrid == 'MOM6':
            # Obtain respective class objects so we can access the full
            # suite of class functions.
            roms = mdlSource.ROMS()
            mom6 = mdlTarget.MOM6()
            # roms_grid = read_ROMS_grid(roms_grid_filename)
            roms.read_ROMS_grid(self)
            # roms_grid = trim_ROMS_grid(roms_grid)
            roms.trim_ROMS_grid()
            # mom6_grid = convert_ROMS_to_MOM6(mom6_grid, roms_grid)
            mom6.setup_MOM6_grid(**kwargs)
            romsGrid = roms.getGrid()
            mom6.convert_ROMS_to_MOM6(romsGrid, **kwargs)
            # Special update to kwargs: this is not seen by higher level calls
            # It is needed here for a corner case to support makeSoloMosaic()
            kwargs['topographyGrid'] = mom6.mom6_grid['cell_grid']['depth']
            # mom6_grid = approximate_MOM6_grid_metrics(mom6_grid)
            mom6.approximate_MOM6_grid_metrics()

            # Replace the grid
            self.grid = mom6.getGrid()
            self.gridInfo['type'] = targetGrid

            # There is another routine that can be used to formally save the grid
            # write_MOM6_supergrid_file(mom6_grid)
            if kwargs['writeTopography']:
                # write_MOM6_topography_file(mom6_grid)
                mom6.write_MOM6_topography_file(self, **kwargs)
            if kwargs['writeMosaic']:
                # write_MOM6_solo_mosaic_file(mom6_grid)
                mom6.write_MOM6_solo_mosaic_file(self, **kwargs)
            if kwargs['writeLandmask']:
                # write_MOM6_land_mask_file(mom6_grid)
                mom6.write_MOM6_land_mask_file(self, **kwargs)
            if kwargs['writeOceanmask']:
                # write_MOM6_ocean_mask_file(mom6_grid)
                mom6.write_MOM6_ocean_mask_file(self, **kwargs)
            if kwargs['writeExchangeGrids']:
                # write_MOM6_exchange_grid_file(mom6_grid, 'atmos',  'land')
                # write_MOM6_exchange_grid_file(mom6_grid, 'atmos', 'ocean')
                # write_MOM6_exchange_grid_file(mom6_grid,  'land', 'ocean')
                mom6.write_MOM6_exchange_grid_files(self, **kwargs)
            if kwargs['writeCouplerMosaic']:
                # write_MOM6_coupler_mosaic_file(mom6_grid)
                mom6.write_MOM6_coupler_mosaic_file(self, **kwargs)

            msg = ('INFO: Successful conversion of grid (%s => %s).' % (sourceGrid, targetGrid))
            self.printMsg(msg, level=logging.INFO)
            return
            
    def openGrid(self, inputUrl, **kwargs):
        '''Open a grid file.  This creates and open
        file pointer which is local to the gridtools object.

	Specify with file: or OpenDAP (http://, https://) or ds:.

        To access the opened grid, use: `obj.xrDS`.  This grid now needs
        to be formally read by `readGrid()` and the grid will be
        available to `obj.grid` and `obj.nativeGrid`.
        '''

        # If we have a file pointer and it is open, close it and re-open the new file
        if self.xrOpen:
            self.closeGrid()

        # Process keyword arguments
        gridType = kwargs.pop('gridType', 'MOM6')
        chunks = kwargs.pop('chunks', None)

        # Some keyword arguments need to be kept upstream
        kwargs['chunks'] = chunks

        if gridType == 'ROMS':
            gridid = kwargs.pop('gridid', None)
            if gridid:
                self.gridInfo['ROMS_gridid'] = gridid

            # If just the gridid is supplied, then just return
            # the grid is read in readGrid().
            if not(inputUrl) or inputUrl is None:
                self.xrOpen = True
                self.gridInfo['type'] = gridType
                return
            
        try:
            if chunks:
                self.xrChunks = chunks

            self.xrDS = self.openDataset(inputUrl, **kwargs)
            # Update only if we are not None
            if self.xrDS is not None:
                self.xrOpen = True
                self.xrFilename = inputUrl
                self.gridInfo['type'] = gridType
        except:
            msg = "ERROR: Unable to load grid: %s" % (inputUrl)
            self.printMsg(msg, level=logging.ERROR)
            self.xrDS = None
            self.xrOpen = False
            # If in DEBUG mode, stop on error to load the inputUrl
            self.debugMsg("DEBUG: Stopping on read error of grid file.")

    def readGrid(self, **kwargs):
        '''Read a grid.  This is more of a convenience function for applications
        that need to pass grids to gridtools instead of using the openGrid function.
        
        This can be generalized to work with "other" grids if we desired? (ROMS, HyCOM, etc).
        This routine does not verify the read grid vs. type of grid specified.

        .. note::
            A copy of the native grid native structure can be found
            by using `obj.nativeGrid`.  The `obj.grid` variable may
            be modified by the gridtools library.

        '''

        # Process keyword arguments
        defaultModelType = 'MOM6'
        if 'type' in self.gridInfo.keys():
            defaultModelType = self.gridInfo['type']

        gridType = kwargs.pop('gridType', defaultModelType)
        local = kwargs.pop('local', None)
        localFilename = kwargs.pop('localFilename', None)

        if localFilename:
            self.xrFilename = localFilename

        # if a dataset is being loaded via readGrid(local=), close any existing dataset
        if local:
            if self.xrOpen:
                self.closeGrid()
            self.xrOpen = True
            self.xrDS = local
            self.grid = local
            # This should be an xarray with an available copy method
            self.nativeGrid = local.copy()
            return

        if self.xrOpen:
            # Save grid metadata
            self.gridInfo['type'] = gridType
            self.grid = self.xrDS
            # This will be None until a recognized grid type is found
            self.nativeGrid = None

            # Do specific grid type reads and place into nativeGrid object
            if gridType == 'MOM6':
                self.nativeGrid = self.xrDS.copy()

            if gridType == 'ROMS':

                if 'ROMS_gridid' in self.gridInfo.keys():
                    sourceGridModule = gridType.lower()
                    try:
                        mdlSource = importlib.import_module('gridtools.grids.%s' % (sourceGridModule))
                    except:
                        msg = ('ERROR: Failed to load grid module for %s.' % (sourceGrid))
                        self.printMsg(msg, level=logging.ERROR)
                        return

                    romsMdl = mdlSource.ROMS()
                    self.nativeGrid = romsMdl.get_ROMS_grid(self.gridInfo['ROMS_gridid'])

                # If we loaded a ROMS grid via gridid, then we need to populate the gridutils
                # variable with native items.
                if len(self.grid) == 0:
                    # Lon and Lat center grid points
                    self.grid['lon'] = (('ny', 'nx'), self.nativeGrid.hgrid.lon_rho)
                    self.grid['lat'] = (('ny', 'nx'), self.nativeGrid.hgrid.lat_rho)

                    # Ocean mask values
                    self.grid['mask'] = (('ny', 'nx'), self.nativeGrid.hgrid.mask)

                    self.grid = self.grid.set_coords(['lon', 'lat'])
                else:
                    #breakpoint()
                    pass

        

    def removeFillValueAttributes(self, data=None, stringVars=None):
        '''Helper function to format the netCDF file to emulate the
        current styles.

        :param data: variables to format
        :type data: xarray
        :param stringVars: dictionary of string variables and lengths
        :type stringVars: dict()
        :return: netCDF encoding
        :rtype: dict()

        For *data*, the ``_FillValue`` is masked.

        For *stringVars*, supply a string length.  e.g. ``{'tile': 255}``
        This will result in an encoding of ``{'dtype': 'S255', 'char_dim_name': 'string'}``.

        '''

        ncEncoding = dict()
        ncVars = []
        if data is not None:
            # The data object may be a single variable
            if not(hasattr(data, 'variables')):
                if hasattr(data, 'name'):
                    ncVars = list([data.name])
            else:
                ncVars = list(data.variables)

            # Also apply to coordinate variables
            if hasattr(data, 'coords'):
                ncVars = ncVars + list(data.coords)
        else:
            ncVars = list(self.grid.variables)

        for ncVar in ncVars:
            ncEncoding[ncVar] = {'_FillValue': None}

        if stringVars:
            for ncVar in stringVars.keys():
                if ncVar in ncVars:
                    ncEncoding[ncVar] = {'dtype': 'S%d' % (stringVars[ncVar]), 'char_dim_name': 'string'}

        return ncEncoding
    
    def saveGrid(self, filename=None, directory=None):
        '''
        This operation is destructive using the last known filename which can be overridden.
        '''
        if filename:
            if directory:
                filename = os.path.join(directory, filename)
            self.xrFilename = filename
        else:
            if not(self.xrFilename):
                msg = ("ERROR: Save grid failed.  A grid filename was not specified.")
                grd.printMsg(msg, logging.ERROR)
                return

        # Generic longitude check
        if self.grid['x'].attrs['units'] == 'degrees_east':
            self.grid['x'].values = np.where(self.grid['x'].values>180, self.grid['x'].values-360, self.grid['x'].values)

        #Duplicate
        #self.grid.to_netcdf(self.xrFilename, encoding=self.removeFillValueAttributes())

        # Save the grid here
        try:
            self.grid.to_netcdf(self.xrFilename, encoding=self.removeFillValueAttributes())
            msg = "Successfully wrote netCDF file to %s" % (self.xrFilename)
            self.printMsg(msg, level=logging.INFO)
        except:
            msg = "Failed to write netCDF file to %s" % (self.xrFilename)
            self.printMsg(msg, level=logging.INFO)

    def makeSoloMosaic(self, **kwargs):
        '''
        This replicates some of the processes of ``make_solo_mosaic`` from :cite:p:`GFDL_MSG_2021_FRE_nctools`.
        This routine is also based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.

        A grid must be created or read.  This function has the following keyword arguments
        and default values.  This is a MOM6 specific function to write out various files depending on
        arguments passed.

        **Keyword arguments**:

            * *topographyGrid* (``xarray``) -- topographic grid to be used with the model grid. REQUIRED. Default: None
            * *topographyFilename* (``string``) -- filename used to write topographic grid. Default: "ocean_topog.nc"
            * *mosaicFilename* (``string``) -- filename for mosaic file. Default: "ocean_mosaic.nc"
            * *oceanGridFilename* (``string``) -- filename for ocean grid file. Default: "ocean_hgrid.nc"
            * *writeLandmask* (``boolean``) -- set True to write land mask file. Default: False
            * *landmaskFilename* (``string``) -- filename used to write the land mask. Default: "land_mask.nc"
            * *writeOceanmask* (``boolean``) -- set True to write ocean mask file. Default: False
            * *oceanmaskFilename* (``string``) -- filename used to write the ocean mask. Default: "ocean_mask.nc"
            * *tileName* (``string``) -- name to assign to the solo tile. Default: "tile1"
            * *MINIMUM_DEPTH* (``float``) -- minimum depth of ocean in meters. Default: 0.0
            * *MASKING_DEPTH* (``float``) -- masking depth of ocean in meters. Default: 0.0
            * *MAXIMUM_DEPTH* (``float``) -- maximum depth of ocean in meters. Default: -99999.0
            * *writeCouplerMosaic* (``boolean``) -- set False to skip creation of coupler mosaic file. Default: True
            * *couplerMosaicFilename* (``string``) -- set False to skip creation of coupler mosaic file. Default: "mosaic.nc"
            * *writeExchangeGrids* (``boolean``) -- set False to skip creation of exchange grids. Default: True
            * *overwrite* (``boolean``) -- set True to overwrite existing files. Default: False
            * *inputDirectory* (``string``) -- absolute or relative path to write model input files. Default: "INPUT"
            * *relativeToINPUTDir* (``string``) -- absolute or relative path for mosaic files to the INPUT directory. Default: "./"

        .. note::
            Using the defaults, this routine will write the following files to the ``INPUT`` directory with
            one tile named ``tile1``:

                * ``mosaic.nc``
                * ``ocean_mosaic.nc``
                * ``ocean_topog.nc``
                * ``atmos_mosaic_tile1Xland_mosaic_tile1.nc``
                * ``atmos_mosaic_tile1Xocean_mosaic_tile1.nc``
                * ``land_mosaic_tile1Xocean_mosaic_tile1.nc``

            If any of these files exist, the file will **NOT** be replaced and a warning will be issued.

            For *oceanGridFile*, if the filename is not provided, the routine will attempt to use
            the name provided when the grid was read.  The filename may need to be set if the grid
            was just constructed using the library.
        '''

        # Check and set any defaults to kwargs
        utils.checkArgument(kwargs, 'topographyFilename', "ocean_topog.nc")
        utils.checkArgument(kwargs, 'mosaicFilename', "ocean_mosaic.nc")
        utils.checkArgument(kwargs, 'oceanGridFilename', "ocean_hgrid.nc")
        utils.checkArgument(kwargs, 'writeLandmask', False)
        utils.checkArgument(kwargs, 'landmaskFilename', "land_mask.nc")
        utils.checkArgument(kwargs, 'writeOceanmask', False)
        utils.checkArgument(kwargs, 'oceanmaskFilename', "ocean_mask.nc")
        utils.checkArgument(kwargs, 'tileName', "tile1")
        utils.checkArgument(kwargs, 'MINIMUM_DEPTH', 0.0)
        utils.checkArgument(kwargs, 'MASKING_DEPTH', 0.0)
        utils.checkArgument(kwargs, 'MAXIMUM_DEPTH', -99999.0)
        utils.checkArgument(kwargs, 'writeExchangeGrids', True)
        utils.checkArgument(kwargs, 'writeCouplerMosaic', True)
        utils.checkArgument(kwargs, 'couplerMosaicFilename', "mosaic.nc")
        utils.checkArgument(kwargs, 'overwrite', False)
        utils.checkArgument(kwargs, 'inputDirectory', "INPUT")
        utils.checkArgument(kwargs, 'relativeToINPUTDir', "./")

        if len(self.grid.variables) == 0:
            # No grid found
            msg = ("ERROR: A grid first must be defined by reading and existing grid or creating a new grid.")
            self.printMsg(msg, level=logging.ERROR)
            return

        mdl = importlib.import_module('gridtools.grids.mom6')
        mom6 = mdl.MOM6()
        # Supergrid is stored via GridUtils.saveGrid()
        mom6.write_MOM6_topography_file(self, **kwargs)
        mom6.write_MOM6_solo_mosaic_file(self, **kwargs)
        if kwargs['writeLandmask']:
            mom6.write_MOM6_land_mask_file(self, **kwargs)
        if kwargs['writeOceanmask']:
            mom6.write_MOM6_ocean_mask_file(self, **kwargs)
        if kwargs['writeExchangeGrids']:
            mom6.write_MOM6_exchange_grid_files(self, **kwargs)
        if kwargs['writeCouplerMosaic']:
            mom6.write_MOM6_coupler_mosaic_file(self, **kwargs)
    
    # plot operations plot functions
    # Plot Operations Plot Functions
    # Plotting specific functions
    # These functions should not care what grid is loaded. 
    # Plotting is affected by plotParameters and gridParameters.

    def newFigure(self, figsize=None, dpi=None):
        '''Establish a new matplotlib figure.'''

        if figsize:
            figsize = self.getPlotParameter('figsize', default=figsize)
        else:
            figsize = self.getPlotParameter('figsize', default=self.plotParameterDefaults['figsize'])

        if dpi:
            dpi = self.getPlotParameter('dpi', default=dpi)
        else:
            dpi = self.getPlotParameter('dpi', default=self.plotParameterDefaults['dpi'])

        fig = Figure(figsize=figsize, dpi=dpi)
        
        #dpiVal = mpl.rcParams['figure.dpi']
        #print(dpiVal)

        return fig
    
    def plotGrid(self, **kwargs):
        '''Perform a plot operation.  This function supports plotting a variable from a data
        source or the model grid that was loaded or created.  A plot may contain both.

        :return: Returns a tuple of matplotlib objects (figure, axes)
        :rtype: tuple

        In general, a projection is necessary to plot a variable or model grid.

        :Example:

        >>> grd = gridUtils()
        >>> grd.setPlotParameters(
                {
                    ...other grid options...,
                    'projection': {
                        'name': 'Mercator',
                        ...other projection options...,
                    },
                })
        >>> grd.plotGrid()

        **Keyword arguments**:

            * *showModelGrid* (``boolean``) -- set False to hide the model grid. Default: True
            * *plotVariables* (``dict()``) -- one or more variables and plot parameters. Default: None

        **Keyword arguments for plotVariables**:

            * *vals* (``xarray``) -- one dataset, variable or grid of information.
            * *cmap* (``str or Colormap``) -- A Colormap instance or
              registered colormap name. Default: ``rcParams["image.cmap"]`` or ``viridis``
            * *norm* (``Normalize``) -- A Normalize instance. Default:
              The data range is mapped to the colorbar range using linear scaling.
            * *levels* (``list()``) -- Discrete levels for plotting. Default: None
            * *cbar_kwargs* (``dict()``) -- Keyword arguments that are
              applied to the colorbar. See: `matplotlib.figure.Figure.colorbar() <https://matplotlib.org/stable/api/figure_api.html#matplotlib.figure.Figure.colorbar>`_
              Default: dict()

        Useful information on `plot shading <https://matplotlib.org/stable/gallery/images_contours_and_fields/pcolormesh_grids.html#sphx-glr-gallery-images-contours-and-fields-pcolormesh-grids-py>`_ for grid cell or centered over a grid point.  Useful example for `adjusting the colorbar <https://matplotlib.org/stable/tutorials/colors/colorbar_only.html#sphx-glr-tutorials-colors-colorbar-only-py>`_ and using a `different colormap <https://matplotlib.org/stable/tutorials/colors/colormaps.html>`_.
        '''

        # Set defaults for keyword arguments
        if not('showModelGrid' in kwargs.keys()):
            kwargs['showModelGrid'] = True
        if not('plotVariables' in kwargs.keys()):
            kwargs['plotVariables'] = dict()

        plotProjection = self.getPlotParameter('name', subKey='projection', default=None)

        if not(plotProjection):
            msg = "ERROR: Please set the plot 'projection' parameter 'name'."
            self.printMsg(msg, level=logging.ERROR)
            return (None, None)

        # initiate new plot, infer projection within the plotting procedure
        f = self.newFigure()

        # declare projection options - note that each projection uses a different
        # combination of these parameters and rarely all are used for one projection
        central_longitude = self.getPlotParameter('lon_0', subKey='projection', default=0.0)
        central_latitude = self.getPlotParameter('lat_0', subKey='projection', default=0.0)
        lat_1 = self.getPlotParameter('lat_1', subKey='projection', default=0.0)
        lat_2 = self.getPlotParameter('lat_2', subKey='projection', default=0.0)
        standard_parallels = (lat_1, lat_2)
        satelliteHeight = self.getPlotParameter('satelliteHeight', default=35785831.0)
        true_scale_latitude = self.getPlotParameter('lat_ts', subKey='projection', default=central_latitude)

        # declare varying crs based on plotProjection
        crs = None
        if plotProjection == 'LambertConformalConic':
            crs = cartopy.crs.LambertConformal(
            central_longitude=central_longitude, central_latitude=central_latitude,
            standard_parallels=standard_parallels)
        if plotProjection == 'Mercator':
            crs = cartopy.crs.Mercator(central_longitude=central_longitude)
        if plotProjection == 'NearsidePerspective':
            crs = cartopy.crs.NearsidePerspective(central_longitude=central_longitude,
                central_latitude=central_latitude, satellite_height=satelliteHeight)
        if plotProjection == 'Stereographic':
            if central_latitude not in (-90., 90.):
                msg = "ERROR: Stereographic projection requires lat_0 to be +90.0 or -90.0 degrees."
                self.printMsg(msg, level=logging.ERROR)
                return (None, None)
            crs = cartopy.crs.Stereographic(central_longitude=central_longitude,
                central_latitude=central_latitude, true_scale_latitude=true_scale_latitude)
        if plotProjection == 'NorthPolarStereo':
            crs = cartopy.crs.NorthPolarStereo(central_longitude=central_longitude,
                true_scale_latitude=true_scale_latitude)
        if plotProjection == 'SouthPolarStereo':
            crs = cartopy.crs.SouthPolarStereo(central_longitude=central_longitude,
                true_scale_latitude=true_scale_latitude)

        if crs == None:
            #warnings.warn("Unable to plot this projection: %s" % (plotProjection))
            msg = "Unable to plot this projection: %s" % (plotProjection)
            self.printMsg(msg, level=logging.ERROR)
            return (None, None)

        ax = f.subplots(subplot_kw={'projection': crs})
        mapExtent = self.getPlotParameter('extent', default=[])
        mapCRS = self.getPlotParameter('extentCRS', default=cartopy.crs.PlateCarree())
        if len(mapExtent) == 0:
            ax.set_global()
        else:
            ax.set_extent(mapExtent, crs=mapCRS)
        ax.stock_img()
        ax.coastlines()
        ax.gridlines()
        title = self.getPlotParameter('title', default=None)
        if title:
            ax.set_title(title)
            
        try:
            nj = self.grid.dims['nyp']
            ni = self.grid.dims['nxp']
        except:
            msg = "ERROR: Unable to plot. Missing grid dimensions."
            self.printMsg(msg, level=logging.ERROR)
            return (None, None)

        iColor = self.getPlotParameter('iColor', default='k')
        jColor = self.getPlotParameter('jColor', default='k')
        transform = self.getPlotParameter('transform', default=cartopy.crs.Geodetic())
        iLinewidth = self.getPlotParameter('iLinewidth', default=1.0)
        jLinewidth = self.getPlotParameter('jLinewidth', default=1.0)

        # Plot the model grid only if specified
        if kwargs['showModelGrid']:
            plotAllVertices = self.getPlotParameter('showGridCells', default=False)
            plotSupergrid = self.getPlotParameter('showSupergrid', default=False)
            plotStep = 2
            if plotSupergrid:
                plotStep = 1
            #self.printMsg("Current grid parameters:", level=logging.INFO)

            # plotting vertices
            # For a non conforming projection, we have to plot every line between
            # the points of each grid box

            for i in range(0, ni+1, plotStep):
                if (i == 0 or i == (ni-1)) or plotAllVertices:
                    if i <= ni-1:
                        ax.plot(self.grid['x'][:,i], self.grid['y'][:,i], iColor, linewidth=iLinewidth, transform=transform)
            for j in range(0, nj+1, plotStep):
                if (j == 0 or j == (nj-1)) or plotAllVertices:
                    if j <= nj-1:
                        ax.plot(self.grid['x'][j,:], self.grid['y'][j,:], jColor, linewidth=jLinewidth, transform=transform)

            # DEBUG PLOT (0,0)
            ax.scatter(self.grid['x'][0,0], self.grid['y'][0,0], color="red", s=5, transform=transform)

        # Loop through provided variables
        if kwargs['plotVariables']:
            for pVar in kwargs['plotVariables'].keys():
                ds = xr.Dataset()
                # xarray=0.19.0 requires unpacking of Dataset variables by using .data
                ds[pVar] = (('ny','nx'), kwargs['plotVariables'][pVar]['values'].data)
                s1 = ds[pVar].shape
                s2 = self.grid['x'].shape
                # See if we are on the same grid, if not assume the variable to plot was
                # on the regular grid and subset our supergrid to a regular grid for plotting
                if s1 == s2:
                    # xarray=0.19.0 requires unpacking of Dataset variables by using .data
                    ds['x'] = (('ny','nx'), self.grid['x'].data)
                    ds['y'] = (('ny','nx'), self.grid['y'].data)
                else:
                    # xarray=0.19.0 requires unpacking of Dataset variables by using .data
                    ds['x'] = (('ny','nx'), self.grid['x'][1::2,1::2].data)
                    ds['y'] = (('ny','nx'), self.grid['y'][1::2,1::2].data)

                # xarray plot needs coordinate variables for lon and lat
                ds = ds.set_coords(['y', 'x'])

                # Set cmap, norm, levels
                cmap = self.setPlotCMap(kwargs['plotVariables'][pVar])
                norm = self.setPlotNorm(kwargs['plotVariables'][pVar])
                levels = self.setPlotLevels(kwargs['plotVariables'][pVar])
                cbar_kwargs = self.setPlotCbarkwargs(kwargs['plotVariables'][pVar])

                ds[pVar].plot(x='x', y='y', ax=ax, transform=transform, cmap=cmap,
                    norm=norm, levels=levels, cbar_kwargs=cbar_kwargs)

                # Configure plot parameters, title is covered up by the plot?
                ax = self.updateAxes(ax, kwargs['plotVariables'][pVar])

        return f, ax

    def setPlotCMap(self, varArgs):
        '''Set user defined color map or use matplotlib default.'''
        if 'cmap' in varArgs.keys():
            return varArgs['cmap']

        return mpl.cm.viridis

    def setPlotNorm(self, varArgs):
        if 'norm' in varArgs.keys():
            return varArgs['norm']

        return None

    def setPlotLevels(self, varArgs):
        if 'levels' in varArgs.keys():
            return varArgs['levels']

        return None

    def setPlotCbarkwargs(self, varArgs):
        if 'cbar_kwargs' in varArgs.keys():
            return varArgs['cbar_kwargs']

        return dict()

    def updateAxes(self, ax, varArgs):
        '''Apply figure options to axes based on parameters passed to variable.'''

        if 'title' in varArgs.keys():
            ax.set_title(varArgs['title'])

        return ax

    # grid parameter operations grid parameter functions
    # Grid Parameter Operations Grid Parameter Functions

    def clearGridParameters(self):
        '''Clear grid parameters.  This does not erase any grid data.'''
        self.gridInfo['gridParameters'] = dict()
        self.gridInfo['gridParameterKeys'] = self.gridInfo['gridParameters'].keys()

    def deleteGridParameters(self, gList, subKey=None):
        '''This deletes a given list of grid parameters.'''

        # Top level subkeys
        if subKey:
            if subKey in self.gridInfo['gridParameterKeys']:
                subKeys = self.gridInfo[subKey].keys()
                for k in gList:
                    if k in subKeys:
                        self.gridInfo[subKey].pop(k, None)
            return

        # Top level keys
        for k in gList:
            if k in self.gridInfo['gridParameterKeys']:
                self.self.gridInfo['gridParameters'].pop(k, None)
                            
        self.gridInfo['gridParameterKeys'] = self.gridInfo['gridParameters'].keys()

    def extendGrid(self, jStart, jEnd, iStart, iEnd, gridMethod='auto', gridProj='auto'):
        '''Extend the current grid by jStart, jEnd, iStart, iEnd points using
        the specified method.  The grid can be extended using 'spherical' space
        or 'latlon' space.  If the method is 'auto', the routine tries to 
        determine which to use.  The grid is extended in all directions
        using the maximum of provided parameters and then clipped to
        the proper dimensions.  Grids extended using 'spherical' space
        require the projection used when the grid was created to perform
        forward and reverse transformation of coordinates.

        This function assumes an existing grid is present and that
        the variables x and y are longitude and latitude.

        This function returns the extended grid.

        .. note::

            Since MOM6 grids are defined with a supergrid, to extend
            the regular grid one point in all directions, this routine
            should specify to extend the grid two points in all
            directions.

        **Grid Extension Technique**:

            This description shows the extension of a grid by one point.  This
            also applies to any requested grid size.

            Process

            # Original grid (o); Points to fill (.)
            #  . . . . .
            #  . o o o .
            #  . o o o .
            #  . o o o .
            #  . . . . .

            # Step 1: Extend grid along j-direction
            # New points shown by (A)
            #  . . . . .
            #  A o o o A
            #  A o o o A
            #  A o o o A
            #  . . . . .
            #

            # Step 2: Extend grid along the i-direction
            # New points shown by (B)
            #  B B B B B
            #  A o o o A
            #  A o o o A
            #  A o o o A
            #  B B B B B

            # Step 3: Clip grid back to requested size
            # given by iStart, iEnd, jStart, jEnd.

            # To prepend one column of points,
            # please specify extendGrid(0,0,1,0).
            # The grid returned should look like:
            #  A o o o
            #  A o o o
            #  A o o o

            # To prepend one column of points and
            # append a row of points to the end,
            # please specify extendGrid(0,1,1,0).
            # The grid returned should look like:
            #  B B B B
            #  A o o o
            #  A o o o
            #  A o o o

        '''

        # Local variables
        maxIncrease = max(jStart, jEnd, iStart, iEnd)
        x = None
        y = None
        extGrid = xr.Dataset()

        # If gridMethod='auto' try to determine if we should extend
        # the grid via 'spherical' or 'latlon'.

        if gridMethod == 'auto':
            gridMethod = self.extendGridDetectMethod()
            if not(gridMethod in ('spherical','latlon')):
                msg = "ERROR: Unable to automatically detect grid type. Returning an empty grid."
                self.printMsg(msg, level=logging.ERROR)
                self.debugMsg(msg)
                return extGrid

            # INFO
            msg = ("INFO: Auto detected gridding method (%s)." % (gridMethod))
            self.printMsg(msg, level=logging.INFO)

        if gridProj == 'auto':
            if hasattr(self.grid, 'attrs'):
                gridAttr = self.grid.attrs.keys()
                if 'proj' in gridAttr:
                    gridProj = self.grid.attrs['proj']

            # INFO
            msg = ("INFO: Auto detected projection details (%s)." % (gridProj))
            self.printMsg(msg, level=logging.INFO)

        # An existing grid should be present
        try:
            extGrid['x'] = self.grid['x'].copy()
            extGrid['y'] = self.grid['y'].copy()
        except:
            msg = "ERROR: Existing grid not found.  Returning an empty grid."
            self.printMsg(msg, level=logging.ERROR)
            self.debugMsg(msg)
            return extGrid

        extGrid.attrs['extendedGrid'] = False
        if gridMethod == 'spherical':
            extGrid = self.extendGridSpherical(extGrid, maxIncrease, gridProj)
        if gridMethod == 'latlon':
            extGrid = self.extendGridLatLon(extGrid, maxIncrease)

        if extGrid.attrs['extendedGrid']:
            # No need to do anything if requested size equals maxIncrease
            if maxIncrease == iStart and maxIncrease == iEnd and maxIncrease == jStart and maxIncrease == jEnd:
                return extGrid
            # Clip extended grid to requested size
            (ny, nx) = extGrid['x'].shape
            clipGrid = xr.Dataset()
            # Y/lat
            jjStart = maxIncrease - jStart
            jjEnd   = ny - (maxIncrease - jEnd)
            # X/lon
            iiStart = maxIncrease - iStart
            iiEnd   = nx - (maxIncrease - iEnd)
            print("Request:",jStart,jEnd,iStart,iEnd)
            print("MaxIncrease:",maxIncrease)
            print("Grid shape:",ny,nx)
            print("Grid clip:",jjStart,jjEnd,iiStart,iiEnd)
            clipGrid['x'] = extGrid['x'][jjStart:jjEnd,iiStart:iiEnd]
            clipGrid['y'] = extGrid['y'][jjStart:jjEnd,iiStart:iiEnd]
            extGrid = clipGrid
            print("Grid shape:", extGrid['x'].shape)
        else:
            msg = "ERROR: Extending grid failed.  Returning incomplete grid."
            self.printMsg(msg, level=logging.ERROR)
            self.debugMsg(msg)

        return extGrid

    def extendGridSpherical(self, inputGrid, maxIncrease, gridProj):
        '''
        This uniformly extends the input grid by maxIncrease points using spherical coordinates
        in meters.  This function requires a grid projection to accurately perform the forward
        and reverse transformation of grid points.

        To increase the grid size we need maxIncrease points on either size (twice as big).
        '''

        # create the coordinate reference system
        crs = CRS.from_proj4(gridProj)

        # create the projection from lon/lat to x/y
        projObj = Transformer.from_crs(crs.geodetic_crs, crs)

        # Transform lat/lon to spherical coordinates
        gX, gY = projObj.transform(inputGrid['x'], inputGrid['y'])

        # Start with an empty grid
        extGrd = xr.Dataset()
        extGrd.attrs['extendedGrid'] = True

        # Get current size of input grid
        (nyp, nxp) = inputGrid['x'].shape

        # Create extended grid with new size
        x = np.zeros((nyp+(maxIncrease*2), nxp+(maxIncrease*2)))
        y = np.zeros((nyp+(maxIncrease*2), nxp+(maxIncrease*2)))

        # Place array and dimensions into the new grid
        # Copy input grid into the center of the new grid
        extGrd['x'] = (('nyp', 'nxp'), x)
        extGrd['y'] = (('nyp', 'nxp'), y)
        extGrd['x'][maxIncrease:nyp+maxIncrease,maxIncrease:nxp+maxIncrease] = inputGrid['x'][:,:]
        extGrd['y'][maxIncrease:nyp+maxIncrease,maxIncrease:nxp+maxIncrease] = inputGrid['y'][:,:]
        # Get the shape of the new grid
        (extyp, extxp) = x.shape

        # Extend grid along j-direction using meters and transform back to
        # latitude and longitude.
        for j in range(0, nyp):
            (newY, newX) = self.findLineFromPoints(gY[j,:], gX[j,:], maxIncrease, maxIncrease)
            newLon, newLat = projObj.transform(newX, newY, direction='INVERSE')
            ind = maxIncrease
            for newPt in range(0, maxIncrease):
                extGrd['x'][j+maxIncrease,ind-1] = newLon[(newPt*2)]
                extGrd['y'][j+maxIncrease,ind-1] = newLat[(newPt*2)]
                extGrd['x'][j+maxIncrease,extxp-ind] = newLon[(newPt*2)+1]
                extGrd['y'][j+maxIncrease,extxp-ind] = newLat[(newPt*2)+1]
                ind = ind - 1

        # Extend grid along i-direction using meters and transform back to
        # latitude and longitude coordinates.  Need to include
        # the extended points in the j-direction to find
        # the corners.
        for i in range(0, extxp):
            lon = extGrd['x'][maxIncrease:extyp-maxIncrease,i].data
            lat = extGrd['y'][maxIncrease:extyp-maxIncrease,i].data
            gXX, gYY = projObj.transform(lon, lat)
            (newY, newX) = self.findLineFromPoints(gYY, gXX, maxIncrease, maxIncrease)
            newLon, newLat = projObj.transform(newX, newY, direction='INVERSE')
            ind = maxIncrease
            for newPt in range(0, maxIncrease):
                extGrd['x'][ind-1,i] = newLon[(newPt*2)]
                extGrd['y'][ind-1,i] = newLat[(newPt*2)]
                extGrd['x'][extyp-ind,i] = newLon[(newPt*2)+1]
                extGrd['y'][extyp-ind,i] = newLat[(newPt*2)+1]
                ind = ind - 1

        return extGrd

    def extendGridLatLon(self, inputGrid, maxIncrease):
        '''
        This uniformly extends the input grid by maxIncrease points using latitude and longitude
        coordinates in degrees.

        To increase the grid size we need maxIncrease points on either size (twice as big).
        '''

        # Start with an empty grid
        extGrd = xr.Dataset()
        extGrd.attrs['extendedGrid'] = True

        # Get shape of the input grid
        (nyp, nxp) = inputGrid['x'].shape

        # Create extended grid with new size
        x = np.zeros((nyp+(maxIncrease*2), nxp+(maxIncrease*2)))
        y = np.zeros((nyp+(maxIncrease*2), nxp+(maxIncrease*2)))

        # Place array and dimensions into the new grid
        # Copy input grid into the center of the new grid
        extGrd['x'] = (('nyp', 'nxp'), x)
        extGrd['y'] = (('nyp', 'nxp'), y)
        extGrd['x'][maxIncrease:nyp+maxIncrease,maxIncrease:nxp+maxIncrease] = inputGrid['x'][:,:]
        extGrd['y'][maxIncrease:nyp+maxIncrease,maxIncrease:nxp+maxIncrease] = inputGrid['y'][:,:]
        # Get the shape of the new grid
        (extyp, extxp) = x.shape

        # Extend grid along j-direction using latitude
        # and longitude coordinates.
        for j in range(0, nyp):
            (newLat, newLon) = self.findLineFromPoints(inputGrid['y'][j,:], inputGrid['x'][j,:], maxIncrease, maxIncrease)
            ind = maxIncrease
            for newPt in range(0, maxIncrease):
                # jStart (head)
                extGrd['x'][j+maxIncrease,ind-1] = newLon[(newPt*2)]
                extGrd['y'][j+maxIncrease,ind-1] = newLat[(newPt*2)]
                # jEnd (tail)
                extGrd['x'][j+maxIncrease,extxp-ind] = newLon[(newPt*2)+1]
                extGrd['y'][j+maxIncrease,extxp-ind] = newLat[(newPt*2)+1]
                ind = ind - 1

        # Extend grid along i-direction using latitude
        # and longitude coordinates.  Need to include
        # the extended points in the j-direction to find
        # the corners.
        for i in range(0, extxp):
            xpts = extGrd['x'][maxIncrease:extyp-maxIncrease,i].data
            ypts = extGrd['y'][maxIncrease:extyp-maxIncrease,i].data
            (newLat, newLon) = self.findLineFromPoints(ypts, xpts, maxIncrease, maxIncrease)
            ind = maxIncrease
            for newPt in range(0, maxIncrease):
                extGrd['x'][ind-1,i] = newLon[(newPt*2)]
                extGrd['y'][ind-1,i] = newLat[(newPt*2)]
                extGrd['x'][extyp-ind,i] = newLon[(newPt*2)+1]
                extGrd['y'][extyp-ind,i] = newLat[(newPt*2)+1]
                ind = ind - 1

        return extGrd

    def extendGridDetectMethod(self):
        '''
        This function looks at the grid metadata and searches for hints
        to see how the grid should be extended.

        **Sources probed for information**:
        
            * Global attribute: projection
            * Variable 'tile' attribute: geometry
        '''

        # Simple cases
        if hasattr(self.grid, 'attrs'):
            gridAttr = self.grid.attrs.keys()
            if 'projection' in gridAttr:
                gridProjection = self.grid.attrs['projection']
                if gridProjection == 'Mercator':
                    return 'latlon'
                if gridProjection in ('LambertConformalConic','Stereographic'):
                    return 'spherical'
            if 'proj' in gridAttr:
                projString = self.grid.attrs['proj']
                if projString.find('proj=lcc') >=0 or projString.find('proj=stere') >=0:
                    return 'spherical'
                if projString.find('proj=merc') >=0:
                    return 'latlon'

        if hasattr(self.grid, 'variables'):
            gridVars = self.grid.variables.keys()
            if 'tile' in gridVars:
                tileAttr = self.grid.variables['tile'].attrs.keys()
                if 'geometry' in tileAttr:
                    gridGeometry = self.grid.variables['tile'].attrs['geometry']
                    if gridGeometry == 'spherical':
                        return 'spherical'
                    # This may not be right
                    return 'latlon'

        return None


    def findLineFromPoints(self, ptsY, ptsX, nY, nX):
        '''Find the extension points at the end of given set of points.
        This routine assumes a nearly linear regularly spaced array of points
        is provided.

        Returned are the new points on the given line.

        ([y1, y2], [x1, x2]) where (y1, x1) is the head of
        the line and (y2, x2) is the tail of the line.

        NOTE: Number of points to extend should be the same nY = nX.  If
        the points are not regularly spaced, extension of a line with
        a large number of points is not going to work very well.
        '''

        newy = []
        newx = []

        diffY = np.diff(ptsY)
        diffX = np.diff(ptsX)

        # lat
        for ind in range(1, nY+1):
            newy.append(ptsY[0] - (diffY[0]*ind))
            newy.append(ptsY[-1] + (diffY[-1]*ind))

        # lon
        for ind in range(1, nX+1):
            newx.append(ptsX[0] - (diffX[0]*ind))
            newx.append(ptsX[-1] + (diffX[-1]*ind))

        return (newy, newx)

    def getGridParameter(self, gkey, subKey=None, default=None, inform=True):
        '''Return the requested grid parameter or the default if none is available.
        The routine will emit a message by default.  Use inform=False to suppress
        messages emitted by this function.
        '''
        if subKey:
            if subKey in self.gridInfo['gridParameterKeys']:
                if gkey in self.gridInfo['gridParameters'][subKey].keys():
                    return self.gridInfo['gridParameters'][subKey][gkey]
            return default
        
        if gkey in self.gridInfo['gridParameterKeys']:
            return self.gridInfo['gridParameters'][gkey]
        
        if inform:
            msg = "WARNING: Using (%s) for default parameter for (%s)." % (default, gkey)
            self.printMsg(msg, level=logging.DEBUG)
        return default
        
    def setGridParameters(self, gridParameters, subKey=None):
        """Generic method for setting gridding parameters using dictionary arguments.
    
        :param gridParameters: grid parameters to set or update
        :type gridParameters: dictionary
        :param subKey: an entry in gridParameters that contains a dictionary of information to set or update
        :type subKey: string
        :return: none
        :rtype: none
        
        .. note::
            Core gridParameter list.  See other grid functions for other potential options.  
            Defaults are **bold**.  See the user manual for more
            details.
            
            **Primary keys**

            * *centerUnits* (``string``) -- Grid center point units [**'degrees'**, 'meters']
            * *centerX* (``float``) -- Grid center in the j direction
            * *centerY* (``float``) -- Grid center in the i direction
            * *dx* (``float``) -- grid length in the j direction
            * *dy* (``float``) -- grid length in the i direction
            * *dxUnits* (``string``) -- grid length units [**'degrees'**, 'meters']
            * *dyUnits* (``string``) -- grid length units [**'degrees'**, 'meters']
            * *nx* (``integer``) -- number of grid points along the j direction
            * *ny* (``integer``) -- number of grid points along the i direction
            * *tilt* (``float``) -- degrees to rotate the grid (*LambertConformalConic only*)
            * *gridResolution* (``float``) -- grid cell size in i and j direction
            * *gridResolutionX* (``float``) -- grid cell size in the j direction
            * *gridResolutionY* (``float``) -- grid cell size in the i direction
            * *gridResoultionUnits* (``string``) -- grid cell units in the i and j direction [**'degrees'**, 'meters']
            * *gridResoultionXUnits* (``string``) -- grid cell units in the j direction [**'degrees'**, 'meters']
            * *gridResoultionYUnits* (``string``) -- grid cell units in the i direction [**'degrees'**, 'meters']

            **subKey 'projection'**

            * *name* (``string``) -- Grid projection ['LambertConformalConic','Mercator','Stereographic']
            * *lat_0* (``float degrees``) -- Latitude of projection center [**0.0**]
            * *lat_1* (``float degrees``) -- First standard parallel (latitude) [**0.0**]
            * *lat_2* (``float degrees``) -- Second standard parallel (latitude) [**0.0**]
            * *lat_ts* (``float degrees``) -- Latitude of true scale. Defines the latitude where scale is not distorted.
              Takes precedence over ``k_0`` if both options are used together.
              For stereographic, if not set, will default to ``lat_0``.
            * *lon_0* (``float degrees``) -- Longitude of projection center [**0.0**]
            * *ellps* (``string``) -- See ``proj -le`` for a list of available ellipsoids [**'GRS80'**]
            * *R'* (``float meters``) -- Radius of the sphere given in meters. If both R and ellps are given, R takes precedence.
            * *x_0* (``float meters``) -- False easting [**0.0**]
            * *y_0* (``float meters``) -- False northing [**0.0**]
            * *k_0* (``float``) -- Depending on projection, this value determines the
              scale factor for natural origin or the ellipsoid [**1.0**]

            The subkey 'projection' mostly follows proj.org terminology for any giving projection.
            See: `Lambert Conformal Conic <https://proj.org/operations/projections/lcc.html>`_,
            `Mercator <https://proj.org/operations/projections/merc.html>`_ and
            `Stereographic <https://proj.org/operations/projections/stere.html>`_ for more details.
                
            :MOM6 specific options:
                * *gridMode* (``integer``) -- 2 = supergrid(*); 1 = actual grid [1 or **2**]

        .. warning::
            These options are similar to :func:`setPlotParameters` which control how this
            grid or other information is plotted.  For instance, the **grid** projection and
            the **plot** projection can be in *different* projections.
            
        """
        
        # For now pass all keys into the plot parameter dictionary.  Sanity checking is done
        # by the respective makeGrid functions.
        for k in gridParameters.keys():
            if subKey:
                self.gridInfo['gridParameters'][subKey][k] = gridParameters[k]
            else:
                self.gridInfo['gridParameters'][k] = gridParameters[k]
        
        if not(subKey):
            self.gridInfo['gridParameterKeys'] = self.gridInfo['gridParameters'].keys()

    def showGridMetadata(self):
        """Show current grid metadata."""
        print(self.gridInfo)
            
    def showGridParameters(self):
        """Show current grid parameters."""
        if len(self.gridInfo['gridParameterKeys']) > 0:
            self.printMsg("Current grid parameters:", level=logging.INFO)
            for k in self.gridInfo['gridParameterKeys']:
                self.printMsg("%20s: %s" % (k,self.gridInfo['gridParameters'][k]), level=logging.INFO)
        else:
            self.printMsg("No grid parameters found.", level=logging.ERROR)

    def subsetGrid(self, scaleFactor):
        """Subsets current grid by the specified scale factor.  Scale factor must
        be an integer and be evenly divisble into the regular grid.  A subsetted
        grid is returned or None on any error.
        """

        # Get regular grid size
        (nyp, nxp) = self.grid['x'].shape
        ny = int((nyp - 1) / 2)
        nx = int((nxp - 1) / 2)

        # Check for grids that are not divisible by the scale factor
        if ny % scaleFactor != 0 or nx % scaleFactor != 0:
            self.printMsg(".", level=logging.ERROR)
            return None

        newGrd = gridtools.gridutils.GridUtils()
        newGrd.grid['x'] = self.grid['x'][::scaleFactor,::scaleFactor]
        newGrd.grid['y'] = self.grid['y'][::scaleFactor,::scaleFactor]

        # Copy global level metadata
        for attr in self.grid.attrs.keys():
            newGrd.grid.attrs[attr] = self.grid.attrs[attr]

        # Recompute metrics
        newGrd.computeGridMetricsSpherical()

        return newGrd
    
    # plot parameter operations plot parameter routines
    # Plot Parameter Operations Plot Parameter Routines
        
    def deletePlotParameters(self, pList, subKey=None):
        """This deletes a given list of plot parameters."""
        
        # Top level subkeys
        if subKey:
            if subKey in self.gridInfo['plotParameterKeys']:
                subKeys = self.gridInfo[subKey].keys()
                for k in pList:
                    if k in subKeys:
                        self.gridInfo[subKey].pop(k, None)
            return

        # Top level keys
        for k in pList:
            if k in self.gridInfo['plotParameterKeys']:
                self.self.gridInfo['plotParameters'].pop(k, None)
                
        self.gridInfo['plotParameterKeys'] = self.gridInfo['plotParameters'].keys()

    def getPlotParameter(self, pkey, subKey=None, default=None, inform=True):
        '''Return the requested plot parameter or the default if none is available.
        
           To access dictionary values in projection, use the subKey argument.

           This function will emit an informational message when a default parameter
           is being used.  Use inform=False to suppress the messages.
        '''

        # Top level subkey access
        if subKey:
            if subKey in self.gridInfo['plotParameterKeys']:
                try:
                    if pkey in self.gridInfo['plotParameters'][subKey].keys():
                        return self.gridInfo['plotParameters'][subKey][pkey]
                except:
                    msg = "Attempt to use a subkey(%s) which is not really a subkey? or maybe it should be?" % (subKey)
                    self.printMsg(msg, level=logging.WARNING)
            return default

        # Top level key access
        if pkey in self.gridInfo['plotParameterKeys']:
            return self.gridInfo['plotParameters'][pkey]

        msg = "WARNING: Using (%s) for default plot parameter for (%s)." % (default, pkey)
        self.printMsg(msg, level=logging.DEBUG)
        return default

    def resetPlotParameters(self):
        '''Resets plot parameters for a grid.'''
        # Need to use .copy on plotParameterDefaults or we get odd results
        self.gridInfo['plotParameters'] = self.plotParameterDefaults.copy()
        self.gridInfo['plotParameterKeys'] = self.gridInfo['plotParameters'].keys()

    def showPlotParameters(self):
        """Show current plot parameters."""
        if len(self.gridInfo['plotParameterKeys']) > 0:
            self.printMsg("Current plot parameters:", level=logging.INFO)
            for k in self.gridInfo['plotParameterKeys']:
                self.printMsg("%20s: %s" % (k,self.gridInfo['plotParameters'][k]), level=logging.INFO)
        else:
            self.printMsg("No plot parameters found.", level=logging.INFO)

    def setPlotParameters(self, plotParameters, subKey=None):
        """A generic method for setting plotting parameters using dictionary arguments.  These
        parameters are applied to plots using the grid or any requested field.  The **grid**
        projection may be different than the requested **plot** projection.

        :param plotParameters: plot parameters to set or update
        :type plotParameters: dictionary
        :param subkey: an entry in plotParameters that contains a dictionary of information to set or update
        :type subKey: string
        :return: none
        :rtype: none
        
        .. note::
            Plot parameters persist for as long as the python :class:`GridUtils` object exists.

            See the user manual for additional details.
            
            **Primary keys**

            * *figsize* (``(float inches, float inches)``) -- matplotlib figure size (width, height)
              Default: **(5.0, 3.75)**
            * *extent* (``[x0, x1, y0, y1]``) -- map extent of given coordinate system (see *extentCRS*)
              If no extent is given, **[]**, then the global extent, ``set_global()``, is used.
              See `matplotlib geoaxes <https://scitools.org.uk/cartopy/docs/latest/matplotlib/geoaxes.html>`_.
              Default: **[]**
            * *extentCRS* (``cartopy.crs method``) -- cartopy crs
              You must have the cartopy.crs module loaded to change this setting.
              See `Cartopy projection list <https://scitools.org.uk/cartopy/docs/latest/crs/projections.html>`_.
              Default: **cartopy.crs.PlateCarree()**
            * *showGrid* (``boolean``) -- show the grid outline. Default: **True**
            * *showGridCells* (``boolean``) -- show the grid cells. Default: **False**
            * *showSupergrid* (``boolean``) -- show the MOM6 supergrid cells.
              Default: **False**
            * *title* (``string``) -- set plot title.
              Default: **None**
            * *iColor* (``string``) -- matplotlib color for i vertices.
              Default: **'k'** (black)
            * *jColor* (``string``) -- matplotlib color for j vertices.
              Default: **'k'** (black)
            * *iLinewidth* (``float points``) -- matplotlib linewidth for i vertices.
              Default: **1.0**
            * *jLinewidth* (``float points``) -- matplotlib linewidth for j vertices.
              Default: **1.0**

            Line width in matplotlib is generally defined by a numerical value over the default
            dots per inch (dpi).  The nominal dpi value is 72 dots per inch.  A line width of
            one (1.0) is 1/72nd of an inch at 72 dpi. A Stack Overflow post discusses
            `dpi and figure size <https://stackoverflow.com/questions/47633546/relationship-between-dpi-and-figure-size>`_
            in good detail.

            **subKey 'projection'**

            * *name* (``string``) -- Grid projection ['LambertConformalConic','Mercator','Stereographic']
            * *lat_0* (``float degrees``) -- Latitude of projection center [**0.0**]
            * *lat_1* (``float degrees``) -- First standard parallel (latitude) [**0.0**]
            * *lat_2* (``float degrees``) -- Second standard parallel (latitude) [**0.0**]
            * *lat_ts* (``float degrees``) -- Latitude of true scale. Defines the latitude where scale is not distorted.
              Takes precedence over ``k_0`` if both options are used together.
              For stereographic, if not set, will default to ``lat_0``.
            * *lon_0* (``float degrees``) -- Longitude of projection center [**0.0**]
            * *ellps* (``string``) -- See ``proj -le`` for a list of available ellipsoids [**'GRS80'**]
            * *R* (``float meters``) -- Radius of the sphere given in meters. If both R and ellps are given, R takes precedence.
            * *x_0* (``float meters``) -- False easting [**0.0**]
            * *y_0* (``float meters``) -- False northing [**0.0**]
            * *k_0* (``float``) -- Depending on projection, this value determines the
              scale factor for natural origin or the ellipsoid [**1.0**]
                
            The subkey 'projection' mostly follows proj.org terminology for any giving projection.
            See: `Lambert Conformal Conic <https://proj.org/operations/projections/lcc.html>`_,
            `Mercator <https://proj.org/operations/projections/merc.html>`_ and
            `Stereographic <https://proj.org/operations/projections/stere.html>`_ for more details.

        .. warning::
            These options are similar to :func:`setGridParameters` which controls the representation
            of the grid.  In this library, it is possible that the **grid** projection and
            the **plot** projection can be in *different* projections.
        """
        
        # For now pass all keys into the plot parameter dictionary.  Sanity checking is done
        # by the respective plotGrid* fuctions.
        for k in plotParameters.keys():
            try:
                if subKey:
                    self.gridInfo['plotParameters'][subKey][k] = plotParameters[k]
                else:
                    self.gridInfo['plotParameters'][k] = plotParameters[k]
            except:
                msg = 'Failed to assign a plotParameter(%s) with "%s"' %\
                        (k, plotParameters[k])
                if subKey:
                    msg = '%s with subkey "%s"' % (msg, subKey)
                self.debugMsg(msg)

        if not(subKey):
            self.gridInfo['plotParameterKeys'] = self.gridInfo['plotParameters'].keys()

    # data source operations data source routines
    # Data Source Operations Data Source Routines

    def addDataSource(self, dataSource, delete=False):
        '''Add a data source to the catalog.  See: datasource.addDataSource()'''
        self.dataSourcesObj.addDataSource(dataSource, delete=delete)

    def checkAvailableVariables(self, dsData, varList):
        '''Check for available variables in a data source.  If any variable is missing,
        issue a warning and return False.  If all variables are available, return
        True.
        '''

        allHere = True
        dsVars = list(dsData.variables)
        for varKey in varList:
            if not(varKey in dsVars):
                self.printMsg("WARNING: Requested variable (%s) was not found in dataset." % (varKey), level=logging.WARNING)
                allHere = False

        return allHere

    def convertToMathExpression(self, sourceExpression):
        '''Convert a source expression to a python expression for evaluation.

           Ex: "-[elevation]" => "-dsData['elevation']"
        '''

        # Recursively replace [] with dsData[]
        reExp = '\[([a-zA-Z0-9_].*?)\]'
        reCmp = re.compile(reExp)
        srch = reCmp.search(sourceExpression)
        limitIterations = 10
        while srch and limitIterations > 0:
            limitIterations = limitIterations - 1
            varName = srch.groups()[0]
            sourceExpression = sourceExpression.replace(srch.group(), "dsData['%s']" % (varName))
            srch = reCmp.search(sourceExpression)

        return sourceExpression

    def openDataset(self, dsName, **kwargs):
        '''Open a dataset using the data source catalog or url that can
        point to a raw dataset using a prefix file: in the data source name.
        The url can be an OpenDAP dataset: e.g.
        https://opendap.jpl.nasa.gov/opendap/allData/ghrsst/data/L4/GLOB/NCDC/AVHRR_AMSR_OI/2011/001/20110101-NCDC-L4LRblend-GLOB-v01-fv02_0-AVHRR_AMSR_OI.nc.bz2

        **Keyword arguments**

            * *chunks* (``int, tuple of int or mapping of hashable to int``) -- xarray chunk description.
            * *gridid* (``ROMS model grid ID``) -- Model grid identification using the gridid.txt file.
              The environment variable `ROMS_GRIDID_FILE` must be set.
	'''
        # Process keyword arguments
        chunks = kwargs.pop('chunks', None)

        dsUrl = urllib.parse.urlparse(dsName)
        # At this point, we assume the dsName is a local filename
        urlToOpen = dsName

        # OpenDAP
        if dsUrl.scheme in ['http','https']:
            urlToOpen = dsObj['url']
            try:
                dsData = xr.open_dataset(urlToOpen)
            except:
                self.printMsg("ERROR: The remote data source (%s) is was not found or could not be opened." % (urlToOpen), level=logging.ERROR)
                return None
            return dsData

        # Local file spec
        if dsUrl.scheme == 'file':
            urlToOpen = dsUrl.path
            if not(os.path.isfile(urlToOpen)):
                self.printMsg("ERROR: The data source (%s) is was not found." % (urlToOpen), level=logging.ERROR)
                return None
            dsData = xr.open_dataset(urlToOpen)
            return dsData

        # Gridtools catalog entry
        dsObj = dict()
        if dsUrl.scheme == 'ds':
            dsPath = dsUrl.path
            if dsPath in self.dataSourcesObj.catalog.keys():
                dsObj = self.dataSourcesObj.catalog[dsPath]
            else:
                self.printMsg("ERROR: The data source (%s) is not defined." % (dsName), level=logging.ERROR)
                return None

            # Parse the catalog url, what to pass to xarray open_dataset
            # scheme='file' => path
            # scheme='http', scheme='https' => dsObj['url']
            dsUrl = urllib.parse.urlparse(dsObj['url'])
            urlToOpen = None
            if dsUrl.scheme in ['http','https']:
                urlToOpen = dsObj['url']
            if dsUrl.scheme == 'file':
                urlToOpen = dsUrl.path
            if 'chunks' in dsObj.keys():
                if not(chunks):
                    chunks = dsObj['chunks']

        dsData = None
        try:
            if chunks:
                dsData = xr.open_dataset(urlToOpen, chunks=chunks)
            else:
                dsData = xr.open_dataset(urlToOpen)
        except:
            self.printMsg("ERROR: The data source (%s) could not be opened." % (dsName), level=logging.ERROR)
            return dsData

        # Apply variableMap if dataset was read from the data source catalog
        if dsObj and 'variableMap' in dsObj.keys():
            dsVars = list(dsData.variables)
            # Map variables from data source to library standard variables
            for varTarget in dsObj['variableMap'].keys():
                varSource = dsObj['variableMap'][varTarget]
                if varSource in dsVars:
                    if varSource != varTarget:
                        dsData = dsData.rename({varSource: varTarget})

        return dsData

    def saveDataset(self, dsName, dsData, **kwargs):
        '''This allows saving variables to a file.

        :param dsName: data source name or filename
        :type dsName: string
        :param dsData: dataset, data array or data object
        :type dsData: xarray object
        :return: none
        :rtype: none

        **Keyword arguments**

            * *overwrite* (``boolean``) -- set to True to allow overwriting. Default: False
            * *hashVariables* (``list()``) -- names of variables to add a sha256sum attribute
            * *mapVariables* (``dict()``) -- map variable names to names stored in the
              output file.  This argument takes precidence over all arguments.

        .. note::
            (Unimplemented) If the `dsName` is a data source (`ds:`) any variable map
            specified will be reversed before writing the final file.
        '''

        # Process keyword arguments
        overwrite = kwargs.pop('overwrite', False)
        hashVariables = kwargs.pop('hashVariables', list())
        mapVariables = kwargs.pop('mapVariables', dict())

        dsUrl = urllib.parse.urlparse(dsName)
        # At this point, we assume the dsName is a local filename
        urlToOpen = dsName

        # OpenDAP
        if dsUrl.scheme in ['http','https']:
            urlToOpen = dsObj['url']
            msg = ("WARNING: Saving to a remote location is unimplemented.")
            self.printMsg(msg, level=logging.WARNING)
            return

        # Local file spec
        if dsUrl.scheme == 'file':
            urlToOpen = dsUrl.path
            if not(os.path.isfile(urlToOpen)):
                self.printMsg("ERROR: The data source (%s) is was not found." % (urlToOpen), level=logging.ERROR)
                return None

        # Gridtools catalog entry
        dsObj = dict()
        if dsUrl.scheme == 'ds':
            dsPath = dsUrl.path
            if dsPath in self.dataSourcesObj.catalog.keys():
                dsObj = self.dataSourcesObj.catalog[dsPath]
            else:
                self.printMsg("ERROR: The data source (%s) is not defined." % (dsName), level=logging.ERROR)
                return None

            # Parse the catalog url, what to pass to xarray open_dataset
            # scheme='file' => path
            # scheme='http', scheme='https' => dsObj['url']
            dsUrl = urllib.parse.urlparse(dsObj['url'])
            urlToOpen = None
            if dsUrl.scheme in ['http','https']:
                msg = ("WARNING: Saving to a remote location is unimplemented.")
                self.printMsg(msg, level=logging.WARNING)
                return
            if dsUrl.scheme == 'file':
                urlToOpen = dsUrl.path

        # Apply variable map to make sure variables are named correctly
        for vKey in mapVariables.keys():
            if vKey in dsData or dsData.coords:
                dsData = dsData.rename({vKey: mapVariables[vKey]})
            else:
                if not(hasattr(dsData, 'variables')) and hasattr(dsData, 'name'):
                    if dsData.name == vKey:
                        dsData.name == mapVariables[vKey]

        # Provide a new hash to selected variables
        if len(hashVariables) > 0:
            for hVar in hashVariables:
                if hVar in dsData or hVar in dsData.coords:
                    dsData[hVar].attrs['sha256'] = utils.sha256sum(dsData[hVar])
            # Edge case where dsData is only one variable
            if not(hasattr(dsData, 'variables')):
                if hasattr(dsData, 'name'):
                    if dsData.name in hashVariables:
                        dsData.attrs['sha256'] = utils.sha256sum(dsData)

        if os.path.isfile(urlToOpen) and not(overwrite):
            msg = ("WARNING: Use overwrite=True to overwrite existing file (%s)." % (urlToOpen))
            self.printMsg(msg, level=logging.WARNING)
            return

        try:
            dsData.to_netcdf(urlToOpen, encoding=self.removeFillValueAttributes(data=dsData))
            msg = ("INFO: Successfully wrote to file (%s)." % (urlToOpen))
            self.printMsg(msg, level=logging.INFO)
        except:
            raise
            msg = ("ERROR: Unable to save data to file (%s). The object passed to dsData should be a xarray." %\
                    (urlToOpen))
            self.printMsg(msg, level=logging.WARNING)
            return

    def applyEvalMap(self, dsName, dsData):
        '''Apply constructed equations through python eval() to manipulate data source fields.
           Data source catalog entries must be prefixed with ds:.  If GEBCO is defined
           as a data source in the catalog, use: ds:GEBCO.  All catalog entries start
           with a slash.
        '''

        dsUrl = urllib.parse.urlparse(dsName)
        dsEntry = None
        if dsUrl.scheme != 'ds':
            self.printMsg("ERROR: Data source catalog entries must have a ds: prefix.", level=logging.ERROR)
            return
        else:
            dsEntry = dsUrl.path

        dsObj = None
        if dsEntry in self.dataSourcesObj.catalog.keys():
            dsObj = self.dataSourcesObj.catalog[dsEntry]
        else:
            self.printMsg("ERROR: The data source (%s) is not defined." % (dsName), level=logging.ERROR)
            return

        # Apply evalMap
        if 'evalMap' in dsObj.keys():
            # Perform evaluations
            # If using chunks, evaluate later
            # Evaluations will create additional fields
            # if the name is unique, otherwise it will overwrite the field.
            for varTarget in dsObj['evalMap'].keys():
                mathExpression = self.convertToMathExpression(dsObj['evalMap'][varTarget])
                try:
                    dsData[varTarget] = eval(mathExpression)
                except:
                    msg = ("ERROR: Failed to apply evalMap to (%s)." % (varTarget))
                    self.printMsg(msg, level=logging.ERROR)

    def useDataSource(self, dsObj):
        # Attach data source object to grid tools object
        self.dataSourcesObj = dsObj
        # Attach grid tools object to data source object
        dsObj.grdObj = self

    # external operations external routines
    # External Operations External Routines
    # These routines are directly wired out to its counterparts

    # bathyutils routines

    def applyExistingLandmask(self, dsData, dsVariable, maskFile, maskVariable, **kwargs):
        '''This modifies a given bathymetry using an existing land mask.
        See :py:func:`~gridtools.bathyutils.applyExistingLandmask`.
        '''
        from . import bathyutils
        return bathyutils.applyExistingLandmask(self, dsData, dsVariable, maskFile, maskVariable, **kwargs)

    def applyExistingOceanmask(self, dsData, dsVariable, maskFile, maskVariable, **kwargs):
        '''This modifies a given bathymetry using an existing ocean mask.
        See :py:func:`~gridtools.bathyutils.applyExistingOceanmask`.
        '''
        from . import bathyutils
        return bathyutils.applyExistingOceanmask(self, dsData, dsVariable, maskFile, maskVariable, **kwargs)

    def computeBathymetricRoughness(self, dsName, **kwargs):
        '''This generates h2 and other fields.
        See: :func:`gridtools.bathyutils.computeBathymetricRoughness()`'''
        from . import bathyutils
        return bathyutils.computeBathymetricRoughness(self, dsName, **kwargs)

    def ice9(self, **kwargs):
        '''This calls the ice-9 algorithm from bathyutils.
        See: :func:`gridtools.bathyutils.ice9()`'''
        from . import bathyutils
        return bathyutils.ice9(self, **kwargs)

    # meshutils routines

    def generateGridByRefinement(self, dsName, **kwargs):
        '''Generates a grid from a data source using refinement regridding.'''
        from . import meshutils
        return meshutils.generateGridByRefinement(self, dsName, **kwargs)

    def writeLandmask(self, dsData, dsVariable, outVariable, outFile, **kwargs):
        '''Write a land mask based on provided information.'''
        from . import meshutils
        meshutils.writeLandmask(self, dsData, dsVariable, outVariable, outFile, **kwargs)
        return

    def writeOceanmask(self, dsData, dsVariable, outVariable, outFile, **kwargs):
        '''Write a ocean mask based on provided information.'''
        from . import meshutils
        meshutils.writeOceanmask(self, dsData, dsVariable, outVariable, outFile, **kwargs)
        return

    # topoutils routines

    def regridTopo(self, dsData, gridGeoLoc = "corner",
        topoVarName = "elevation", coarsenInt = 10, method = 'conservative',
        superGrid = True, periodic = True, gridDimX = None, gridDimY = None,
        gridLatName = None, gridLonName = None, topoDimX = None, topoDimY = None,
        topoLatName = None, topoLonName = None, convert_to_depth = True):
        '''Generate a bathymetry and ocean mask for a given data source
        topography or bathymetry.  See :func:`gridtools.topoutils.TopoUtils.regridTopo`.
        '''
        from . import topoutils

        topoObj = topoutils.TopoUtils()
        return topoObj.regridTopo(self, dsData, gridGeoLoc = gridGeoLoc,\
            topoVarName = topoVarName, coarsenInt = coarsenInt, method = method,\
            superGrid = superGrid, periodic = periodic,\
            gridDimX = gridDimX, gridDimY = gridDimY,\
            gridLatName = gridLatName, gridLonName = gridLonName,\
            topoDimX = topoDimX, topoDimY = topoDimY,\
            topoLatName = topoLatName, topoLonName = topoLonName,\
            convert_to_depth = convert_to_depth)
