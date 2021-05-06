# General imports and definitions
import os, sys, datetime, logging
import cartopy, warnings, pdb
import numpy as np
import xarray as xr
from pyproj import CRS, Transformer

# Needed for panel.pane                
from matplotlib.figure import Figure
# not needed for mpl >= 3.1
# Does not cause any problems to continue to use it
from matplotlib.backends.backend_agg import FigureCanvas  

# Required for:
#  * ROMS to MOM6 grid conversion
#  * Computation of MOM6 grid metrics
import spherical

# GridUtils() application
from app import App

class GridUtils:

    def __init__(self, app={}):
        # Constants
        self.PI_180 = np.pi/180.
        # Adopt GRS80 ellipse from proj
        self._default_Re = 6.378137e6
        self._default_ellps = 'GRS80'
        self._default_availableGridTypes = ['MOM6']
        
        # File pointers
        self.xrOpen = False
        self.xrDS = xr.Dataset()
        self.grid = self.xrDS
        # Internal parameters
        self.usePaneMatplotlib = False
        self.msgBox = None
        # Private variables begin with a _
        # Grid parameters
        # Locals
        self.gridMade = False
        self.gridInfo = {}
        self.gridInfo['dimensions'] = {}
        self.gridInfo['gridParameters'] = {}
        self.gridInfo['gridParameterKeys'] = self.gridInfo['gridParameters'].keys()
        # Defaults
        self.plotParameterDefaults = {
            'figsize': (8, 6),
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

    # Utility functions

    def addMessage(self, msg):
        '''Append new message to message buffer.'''
        self.msgBuffer.append(msg)
        return

    def app(self):
        '''By calling this function, the user is requesting the application functionality of GridUtils().
           return the dashboard, but GridUtils() also has an internal pointer to the application.'''
        appObj = App(grd=self)
        self.app = appObj
        return appObj.dashboard

    def application(self, app={}):
        '''Convienence function to attach application items to GridUtil so it can update certain portions of the application.

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

    def clearMessage(self):
        '''This clears the message buffer of messages.'''
        self.msgBuffer = []
        return

    def debugMsg(self, msg, level = -1):
        '''This function has a specific purpose to aid in debugging and
        activating pdb breakpoints.  NOTE: pdb breakpoints tend not to
        work very well when running under the application.  It tends to
        terminate the bokeh/tornado server.

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
            pdb.set_trace()

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

        softwareRevision = "0.1"

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
        self.printMsg("New DEBUG level (%d)" % (newLevel))
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

            Level     Numeric value
            CRITICAL  50
            ERROR     40
            WARNING   30
            INFO      20
            DEBUG     10
            NOTSET    0
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

            Level     Numeric value
            CRITICAL  50
            ERROR     40
            WARNING   30
            INFO      20
            DEBUG     10
        '''
        if type(newLevel) == str:
            try:
                newLevel = logging.getLevelName(newLevel)
            except:
                newLevel = logging.INFO
                
        self.verboseLevel = newLevel

    # Grid operations

    def clearGrid(self):
        '''Call this when you want to erase the current grid.  This also
        clobbers any current grid and plot parameters.
        Do not call this method between plots of the same grid in different
        projections.'''

        # If there are file resources open, close them first.
        if self.xrOpen:
            self.closeDataset()

        self.xrFilename = None
        self.xrDS = xr.Dataset()
        self.grid = self.xrDS
        self.gridInfo = {}
        self.gridInfo['dimensions'] = {}
        self.clearGridParameters()
        self.resetPlotParameters()

    def computeGridMetrics(self):
        '''Compute MOM6 grid metrics: angle_dx, dx, dy and area.'''

        self.grid.attrs['grid_version'] = "0.2"
        self.grid.attrs['code_version'] = "GridTools: %s" % (self.getVersion())
        self.grid.attrs['history'] = "%s: created grid with GridTools library" % (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        self.grid.attrs['projection'] = self.gridInfo['gridParameters']['projection']['name']
        try:
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

        #R = 6370.e3 # Radius of sphere
        # TODO: get ellipse setting
        #R = self._default_Re
        R = self.getRadius(self.gridInfo['gridParameters'])

        # Make a copy of the lon grid as values are changed for computation
        lon = self.grid.x.copy()
        lat = self.grid.y

        # Approximate edge lengths as great arcs
        self.grid['dx'] = (('nyp', 'nx'),  R * spherical.angle_through_center( (lat[ :,1:],lon[ :,1:]), (lat[:  ,:-1],lon[:  ,:-1]) ))
        self.grid.dx.attrs['units'] = 'meters'
        self.grid['dy'] = (('ny' , 'nxp'), R * spherical.angle_through_center( (lat[1:, :],lon[1:, :]), (lat[:-1,:  ],lon[:-1,:  ]) ))
        self.grid.dy.attrs['units'] = 'meters'

        # Scaling by latitude?
        cos_lat = np.cos(np.radians(lat))

        # Presize the angle_dx array
        angle_dx = np.zeros(lat.shape)
        # Fix lon so they are 0 to 360 for computation of angle_dx
        lon = np.where(lon < 0., lon+360, lon)
        angle_dx[:,1:-1] = np.arctan2( (lat[:,2:] - lat[:,:-2]) , ((lon[:,2:] - lon[:,:-2]) * cos_lat[:,1:-1]) )
        angle_dx[:, 0  ] = np.arctan2( (lat[:, 1] - lat[:, 0 ]) , ((lon[:, 1] - lon[:, 0 ]) * cos_lat[:, 0  ]) )
        angle_dx[:,-1  ] = np.arctan2( (lat[:,-1] - lat[:,-2 ]) , ((lon[:,-1] - lon[:,-2 ]) * cos_lat[:,-1  ]) )
        self.grid['angle_dx'] = (('nyp', 'nxp'), angle_dx)
        self.grid.angle_dx.attrs['units'] = 'radians'

        self.grid['area'] = (('ny','nx'), R * R * spherical.quad_area(lat, lon))
        self.grid.area.attrs['units'] = 'meters^2'

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

    def makeGrid(self):
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
        gridResolution = self.getGridParameter('gridResolution', default='Error')
        gridResolutionX = self.getGridParameter('gridResolutionX', default='Error')
        gridResolutionY = self.getGridParameter('gridResolutionY', default='Error')
        gridResolutionUnits = self.getGridParameter('gridResolutionUnits', default='degrees')
        gridResolutionXUnits = self.getGridParameter('gridResolutionXUnits', default='degrees')
        gridResolutionYUnits = self.getGridParameter('gridResolutionYUnits', default='degrees')

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
                    self.grid.x.attrs['units'] = 'degrees_east'
                    self.grid['y'] = (('nyp','nxp'), latGrid)
                    self.grid.y.attrs['units'] = 'degrees_north'

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
                        self.grid.x.attrs['units'] = 'degrees_east'
                        self.grid['y'] = (('nyp','nxp'), latGrid)
                        self.grid.y.attrs['units'] = 'degrees_north'

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
                        self.grid.x.attrs['units'] = 'degrees_east'
                        self.grid['y'] = (('nyp','nxp'), latGrid)
                        self.grid.y.attrs['units'] = 'degrees_north'

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
            self.grid.x.attrs['units'] = 'degrees_east'
            self.grid['y'] = (('nyp','nxp'), latGrid)
            self.grid.y.attrs['units'] = 'degrees_north'

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
            self.grid.x.attrs['units'] = 'degrees_east'
            self.grid['y'] = (('nyp','nxp'), latGrid)
            self.grid.y.attrs['units'] = 'degrees_north'

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
            self.grid.x.attrs['units'] = 'degrees_east'
            self.grid['y'] = (('nyp','nxp'), latGrid)
            self.grid.y.attrs['units'] = 'degrees_north'

            # This technique seems to return a Lambert Conformal Projection with the following properties
            # This only works if the grid does not overlap a polar point
            # (lat_0 - (dy/2), lat_0 + (dy/2))
            self.gridInfo['gridParameters']['projection']['lat_1'] =\
                self.gridInfo['gridParameters']['projection']['lat_0'] - (self.gridInfo['gridParameters']['dy'] / 2.0)
            self.gridInfo['gridParameters']['projection']['lat_2'] =\
                self.gridInfo['gridParameters']['projection']['lat_0'] + (self.gridInfo['gridParameters']['dy'] / 2.0)
            
            newGridCreated = True

        if newGridCreated:
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
                    self.computeGridMetrics()
                else:
                    msg = "NOTE: Grid metrics were not computed."
                    self.printMsg(msg, level=logging.INFO)
        else:
            msg = "WARNING: Grid generation failed."
            self.printMsg(msg, level=logging.WARNING)
                                
    # Original grid generation functions provided by Niki Zadeh

    # Mercator
    def rotate_u(self, x , y, z, ux, uy, uz, theta):
        """Rotate by angle θ around a general axis (ux,uy,uz)."""
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
        # plotting verticies
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
        '''Create a grid in the spherical projection using grid distances in meters.'''

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

            # compute (y, x) from (lon, lat)
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

            # compute (y, x) from (lon, lat)
            lon, lat = proj.transform(yy, xx, direction='INVERSE')

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

    # xarray Dataset operations
    
    def closeDataset(self):
        '''Closes and open dataset file pointer.'''
        if self.xrOpen:
            self.xrDS.close()
            self.xrOpen = False
            
    def openDataset(self, inputFilename):
        '''Open a grid file.  The file pointer is internal to the object.
        To access it, use: obj.xrDS or obj.grid'''
        # check if we have a vailid inputFilename
        if not(os.path.isfile(inputFilename)):
            self.printMsg("Dataset not found: %s" % (inputFilename), level=logging.INFO)
            return
                
        # If we have a file pointer and it is open, close it and re-open the new file
        if self.xrOpen:
            self.closeDataset()
            
        try:
            self.xrDS = xr.open_dataset(inputFilename)
            self.xrOpen = True
            self.xrFilename = inputFilename
        except:
            msg = "ERROR: Unable to load dataset: %s" % (inputFilename)
            self.printMsg(msg, level=logging.ERROR)
            self.xrDS = None
            self.xrOpen = False
            # Stop on error to load a file
            self.debugMsg("")
            
    def readGrid(self, opts={'type': 'MOM6'}, local=None, localFilename=None):
        '''Read a grid.
        
        This can be generalized to work with "other" grids if we desired? (ROMS, HyCOM, etc)
        '''
        # if a dataset is being loaded via readGrid(local=), close any existing dataset
        if local:
            if self.xrOpen:
                self.closeDataset()
            self.xrOpen = True
            self.xrDS = local
            self.grid = local
        else:
            if self.xrOpen:
                if opts['type'] == 'MOM6':
                    # Save grid metadata
                    self.gridInfo['type'] = opts['type']
                    self.grid = self.xrDS
        
        if localFilename:
            self.xrFilename = localFilename

    def removeFillValueAttributes(self):

        ncEncoding = {}
        ncVars = list(self.grid.variables)
        for ncVar in ncVars:
            ncEncoding[ncVar] = {'_FillValue': None}

        return ncEncoding

    
    def saveGrid(self, filename=None):
        '''
        This operation is destructive using the last known filename which can be overridden.
        '''
        if filename:
            self.xrFilename = filename
            if self.grid.x.attrs['units'] == 'degrees_east':
                self.grid.x.values = np.where(self.grid.x.values>180, self.grid.x.values-360, self.grid.x.values)
            self.grid.to_netcdf(self.xrFilename, encoding=self.removeFillValueAttributes())
        try:
            self.grid.to_netcdf(self.xrFilename, encoding=self.removeFillValueAttributes())
            msg = "Successfully wrote netCDF file to %s" % (self.xrFilename)
            self.printMsg(msg, level=logging.INFO)
        except:
            msg = "Failed to write netCDF file to %s" % (self.xrFilename)
            self.printMsg(msg, level=logging.INFO)
    
    # Plotting specific functions
    # These functions should not care what grid is loaded. 
    # Plotting is affected by plotParameters and gridParameters.

    def newFigure(self, figsize=None):
        '''Establish a new matplotlib figure.'''
        
        if figsize:
            figsize = self.getPlotParameter('figsize', default=figsize)             
        else:
            figsize = self.getPlotParameter('figsize', default=self.plotParameterDefaults['figsize'])
            
        fig = Figure(figsize=figsize)
        
        return fig
    
    # insert plotGrid.ipynb here
    
    def plotGrid(self):
        '''Perform a plot operation.

        :return: Returns a tuple of matplotlib objects (figure, axes)
        :rtype: tuple

        To plot a grid, you first must have the projection set.

        :Example:

        >>> grd = gridUtils()
        >>> grd.setPlotParameters(
                {
                    ...other grid options...,
                    'projection': {
                        'name': 'Mercator',
                        ...other projection options...,
                    },
        >>> grd.plotGrid()
        '''

        #if not('shape' in self.gridInfo.keys()):
        #    warnings.warn("Unable to plot the grid.  Missing its 'shape'.")
        #    return (None, None)

        plotProjection = self.getPlotParameter('name', subKey='projection', default=None)

        if not(plotProjection):
            msg = "Please set the plot 'projection' parameter 'name'"
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
        satellite_height = self.getPlotParameter('satellite_height', default=35785831.0)
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
                central_latitude=central_latitude, satellite_height=satellite_height)
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
            msg = "ERROR: Unable to plot.  Missing grid dimensions."
            self.printMsg(msg, level=logging.ERROR)
            return (None, None)

        plotAllVertices = self.getPlotParameter('showGridCells', default=False)
        iColor = self.getPlotParameter('iColor', default='k')
        jColor = self.getPlotParameter('jColor', default='k')
        transform = self.getPlotParameter('transform', default=cartopy.crs.Geodetic())
        iLinewidth = self.getPlotParameter('iLinewidth', default=1.0)
        jLinewidth = self.getPlotParameter('jLinewidth', default=1.0)

        # plotting vertices
        # For a non conforming projection, we have to plot every line between the points of each grid box
        for i in range(0,ni+1,2):
            if (i == 0 or i == (ni-1)) or plotAllVertices:
                if i <= ni-1:
                    ax.plot(self.grid['x'][:,i], self.grid['y'][:,i], iColor, linewidth=iLinewidth, transform=transform)
        for j in range(0,nj+1,2):
            if (j == 0 or j == (nj-1)) or plotAllVertices:
                if j <= nj-1:
                    ax.plot(self.grid['x'][j,:], self.grid['y'][j,:], jColor, linewidth=jLinewidth, transform=transform)

        return f, ax

    # Grid parameter operations

    def clearGridParameters(self):
        '''Clear grid parameters.  This does not erase any grid data.'''
        self.gridInfo['gridParameters'] = {}
        self.gridInfo['gridParameterKeys'] = self.gridInfo['gridParameters'].keys()

    def deleteGridParameters(self, gList, subKey=None):
        """This deletes a given list of grid parameters."""

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

    def getGridParameter(self, gkey, subKey=None, default=None):
        '''Return the requested grid parameter or the default if none is available.'''
        if subKey:
            if subKey in self.gridInfo['gridParameterKeys']:
                if gkey in self.gridInfo['gridParameters'][subKey].keys():
                    return self.gridInfo['gridParameters'][subKey][gkey]
            return default
        
        if gkey in self.gridInfo['gridParameterKeys']:
            return self.gridInfo['gridParameters'][gkey]
        
        msg = "WARNING: Using (%s) for default parameter for (%s)." % (default, gkey)
        self.printMsg(msg, level=logging.DEBUG)
        return default
        
    def setGridParameters(self, gridParameters, subKey=None):
        """Generic method for setting gridding parameters using dictionary arguments.
    
        :param gridParameters: grid parameters to set or update
        :type gridParameters: dictionary
        :param subkey: an entry in gridParameters that contains a dictionary of information to set or update
        :type subKey: string
        :return: none
        :rtype: none
        
        .. note::
            Core gridParameter list.  See other grid functions for other potential options.  
            Defaults are marked with an asterisk(*) below.  See the user manual for more
            details.
            
                'centerUnits': Grid center point units ['degrees'(*), 'meters']
                'centerX': Grid center in the j direction [float]
                'centerY': Grid center in the i direction [float]
                'dx': grid length in the j direction [float]
                'dy': grid length in the i direction [float]
                'dxUnits': grid length units ['degrees'(*), 'meters']
                'dyUnits': grid length units ['degrees'(*), 'meters']
                'nx': number of grid points along the j direction [integer]
                'ny': number of grid points along the i direction [integer]
                'tilt': degrees to rotate the grid [float, only available in LambertConformalConic]
                'gridResolution': grid cell size in i and j direction [float]
                'gridResolutionX': grid cell size in the j direction [float]
                'gridResolutionY': grid cell size in the i direction [float]
                'gridResoultionUnits': grid cell units in the i and j direction ['degrees'(*), 'meters']
                'gridResoultionXUnits': grid cell units in the j direction ['degrees'(*), 'meters']
                'gridResoultionYUnits': grid cell units in the i direction ['degrees'(*), 'meters']

                
                SUBKEY: 'projection' (mostly follows proj.org terminology)
                    'name': Grid projection ['LambertConformalConic','Mercator','Stereographic']
                    'lat_0': Latitude of projection center [degrees, 0.0(*)]
                    'lat_1': First standard parallel (latitude) [degrees, 0.0(*)]
                    'lat_2': Second standard parallel (latitude) [degrees, 0.0(*)]
                    'lat_ts': Latitude of true scale. Defines the latitude where scale is not distorted.
                              Takes precedence over k_0 if both options are used together.
                              For stereographic, if not set, will default to lat_0.
                    'lon_0': Longitude of projection center [degrees, 0.0(*)]
                    'ellps': [GRS80(*)]
                    'R': Radius of the sphere given in meters.
                    'x_0': False easting (meters, 0.0(*))
                    'y_0': False northing (meters, 0.0(*))
                    'k_0': Depending on projection, this value determines the scale factor for natural origin or the ellipsoid (1.0(*))
                
                MOM6 specific options:
                
                'gridMode': 2 = supergrid(*); 1 = actual grid [integer, 1 or 2(*)]

            Not to be confused with plotParameters which control how this grid or other
            information is plotted.  For instance, the grid projection and the requested plot
            can be in different projections.
            
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
    
    # Plot parameter operations
        
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

    def getPlotParameter(self, pkey, subKey=None, default=None):
        '''Return the requested plot parameter or the default if none is available.
        
           To access dictionary values in projection, use the subKey argument.
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
        """A generic method for setting plotting parameters using dictionary arguments.

        :param plotParameters: plot parameters to set or update
        :type plotParameters: dictionary
        :param subkey: an entry in plotParameters that contains a dictionary of information to set or update
        :type subKey: string
        :return: none
        :rtype: none
        
        .. note::
            Plot parameters persist for as long as the python object exists.

            See the user manual for additional details.
            
                'figsize': tells matplotlib the figure size [width, height in inches (5.0, 3.75)]
                'extent': [x0, x1, y0, y1] map extent of given coordinate system (see extentCRS) [default is []]
                    If no extent is given, [], then set_global() is used. 
                    REF: https://scitools.org.uk/cartopy/docs/latest/matplotlib/geoaxes.html
                'extentCRS': cartopy crs [cartopy.crs.PlateCarree()] 
                    You must have the cartopy.crs module loaded to change this setting.
                'showGrid': show the grid outline [True(*)/False]
                'showGridCells': show the grid cells [True/False(*)]
                'showSupergrid': show the MOM6 supergrid cells [True/False(*)]
                'title': add a title to the plot [None(*)]
                'iColor': matplotlib color for i vertices ['k'(*) black]
                'jColor': matplotlib color for j vertices ['k'(*) black]
                'iLinewidth': matplotlib linewidth for i vertices [points: 1.0(*)]
                'jLinewidth': matplotlib linewidth for j vertices [points: 1.0(*)]

                SUBKEY: 'projection' (mostly follows proj.org terminology)
                    'name': Grid projection ['LambertConformalConic','Mercator','Stereographic']
                    'lat_0': Latitude of projection center [degrees, 0.0(*)]
                    'lat_1': First standard parallel (latitude) [degrees, 0.0(*)]
                    'lat_2': Second standard parallel (latitude) [degrees, 0.0(*)]
                    'lat_ts': Latitude of true scale. 
                    'lon_0': Longitude of projection center [degrees, 0.0(*)]
                    'ellps': See proj -le for a list of available ellipsoids [GRS80(*)]
                    'R': Radius of the sphere given in meters.  If both R and ellps are given, R takes precedence.
                    'x_0': False easting (meters, 0.0(*))
                    'y_0': False northing (meters, 0.0(*))
                    'k_0': Depending on projection, this value determines the scale factor for natural origin or the ellipsoid (1.0(*))
                
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

