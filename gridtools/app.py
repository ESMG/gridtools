# GridUtils.App()

# Modules

import os, sys, io, logging
import numpy as np
import cartopy.crs as ccrs
import cartopy
import matplotlib.pyplot as plt
import netCDF4 as nc
import warnings
import xarray as xr
import xgcm
from io import BytesIO
import panel as pn
pn.extension()

# This is called by GridTools() and can't be
# called by itself.

class App:

    def __init__(self, grd=None):

        # Globals
        
        # This application has its own copy of GridTools() object
        self.grd = grd

        # Default filenames
        self.defaultGridFilename = 'gridFile.nc'
        self.defaultLogFilename = 'logFile.log'

        # How we grow the grid from the specified latitude (lat0) or longitude (lon0)
        # TODO: If 'Center' is not chosen then the controls for Central Latitude and Central Longitude no longer make sense.
        # For now: we assume Center/Center for making grids.
        self.xGridModes = ['Left', 'Center', 'Right']
        self.yGridModes = ['Lower', 'Center', 'Upper']

        # For now only MOM6 works.  It could work for other grids!
        #gridTypes = ["MOM6", "ROMS", "WRF"]
        self.gridTypes = ["MOM6"]

        # Generic true/false indicators
        self.trueFalseNames = ["False", "True"]
        self.trueFalseValues = [False, True]
        self.trueFalseDict = dict(zip(self.trueFalseNames, self.trueFalseValues))

        # Log levels
        self.logLevelNames = ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.logLevelValues = [0, 10, 20, 30, 40, 50]
        self.logLevelDict = dict(zip(self.logLevelNames, self.logLevelValues))

        # Debug levels
        self.debugLevelNames = ["OFF", "MESSAGE", "RAISE", "BREAKPOINT"]
        self.debugLevelValues = [0, 1, 2, 3]
        self.debugLevelDict = dict(zip(self.debugLevelNames, self.debugLevelValues))

        # Available plot projections
        self.plotProjections = ["Nearside Perspective", "Mercator", "Lambert Conformal Conic", "Stereographic"]
        self.plotProjectionsGridTools = ["NearsidePerspective", "Mercator", "LambertConformalConic", "Stereographic"]
        self.plotProjectionsDict = dict(zip(self.plotProjections, self.plotProjectionsGridTools))

        # Supported grid projections
        self.projNames = ["Mercator", "Lambert Conformal Conic", "Stereographic"]
        self.gridToolNames = ["Mercator", "LambertConformalConic", "Stereographic"]
        self.projNamesGridTools = dict(zip(self.projNames, self.gridToolNames))
        self.projCarto = [ccrs.Mercator(), ccrs.LambertConformal(), ccrs.Stereographic()]
        self.projDict = dict(zip(self.projNames, self.projCarto))

        # Plot grid modes
        # gridExtent, gridCells, superGrid
        self.plotGridModes = ['gridExtent', 'gridCells', 'superGrid']
        self.plotGridModesDescriptions = ['Grid Extent', 'Grid Cells', 'Supergrid Cells']
        self.plotGridModeDict = dict(zip(self.plotGridModesDescriptions, self.plotGridModes))

        # Grid parameters
        self.gridResolutionUnitNames = ['degrees', 'meters']
        self.gridResolutionXUnitNames = ['degrees', 'meters']
        self.gridResolutionYUnitNames = ['degrees', 'meters']
        self.gridDxUnitNames = ['degrees', 'meters']
        self.gridDyUnitNames = ['degrees', 'meters']

        # Plot colors
        self.plotColors = ['b', 'c', 'g', 'k', 'm', 'r', 'y']
        self.plotColorsDescriptions = ['Blue', 'Cyan', 'Green', 'Black', 'Magenta', 'Red', 'Yellow']
        self.plotColorDict = dict(zip(self.plotColorsDescriptions, self.plotColors))

        # Line types (future feature)
        self.plotLineStyles = ['solid', 'dotted', 'dashed', 'dashdot']
        self.plotLineStylesDescriptions = ['Solid', 'Dotted', 'Dashed', 'DashDot']
        self.plotLineStyleDict = dict(zip(self.plotLineStylesDescriptions, self.plotLineStyles))

        # This controls the default figure size of the plot in the panel application
        # TODO: Improve integration
        # aspect 4:3, default dpi=144
        self.widthIn = 5.0
        self.heightIn = (self.widthIn * 3.0) / 4.0
        self.defaultPlotFigureSize = (self.widthIn, self.heightIn)

        # plotWidgetWidth and plotWidgetHeight
        # NOTE: These values are used by other controls
        self.plotWidgetWidth = 800
        self.plotWidgetHeight = 600

        # Setup for other internals of GridTools()
        self.useNumpyPi = False
        self.enableLogging = False
        self.loggingFilename = None
        self.verboseLevel = 0
        self.debugLevel = 0
        
        self.initializeWidgets()
        self.initializeTabs()
        self.initializeDashboard()

    # Panel application functions

    def clearInformationWindow(self, event):
        self.grd.clearMessage()
        self.statusWidget.value = self.grd.showMessages()
        return

    def updateDataView(self):
        self.dataView[0] = self.grd.grid
        return

    def updateFilename(self, newFilename):
        self.gridFilenameLocal.value = newFilename
        self.gridFilenameRemote.value = newFilename
        return

    def downloadNetCDF(self):
        # See if we have a race condition
        self.saveLocalGridButton.filename = self.gridFilenameLocal.value
        bout = self.grd.grid.to_netcdf(encoding=self.grd.removeFillValueAttributes())
        bio = BytesIO()
        bio.write(bout)
        bio.seek(0)
        return bio

    def loadLocalGrid(self, event):
        if self.localFileSelection.value == None:
            msg = "A grid file has not been selected in the Local File tab."
            self.grd.printMsg(msg, logging.INFO)
            return

        # Test to see if xarray can load the selected file
        try:
            ncTest = xr.load_dataset(localFileSelection.value)
            msg = "The grid file %s was loaded." % (self.localFileSelection.filename)
            self.grd.printMsg(msg, logging.INFO)
            self.grd.clearGrid()
            self.grd.readGrid(local=ncTest, localFilename=self.localFileSelection.filename)
            self.updateDataView()
            self.updateFilename(self.localFileSelection.filename)
        except:
            msg = "The grid file %s was not loadable." % (self.localFileSelection.filename)
            self.grd.printMsg(msg, logging.ERROR)

        return
    
    def loadRemoteGrid(self, event):
        ct = len(self.remoteFileSelection.value)

        if ct == 0:
            msg = "A grid file has not been selected in the Remote File tab."
            self.grd.printMsg(msg, logging.INFO)
            return

        try:
            fileToOpen = self.remoteFileSelection.value[0]
            self.grd.openDataset(self.remoteFileSelection.value[0])
            self.grd.readGrid()
            msg = "The grid file %s was loaded." % (fileToOpen)
            self.grd.printMsg(msg, logging.INFO)
            self.updateDataView()
            self.updateFilename(fileToOpen)
        except:
            msg = "Failed to load grid file: %s" % (fileToOpen)
            self.grd.printMsg(msg, logging.ERROR)

        return

    def saveRemoteGrid(self, event):
        '''Attempt to save grid to remote filesystem using last known grid filename.'''
        self.grd.saveGrid(filename=self.gridFilenameRemote.value)

    def make_grid(self, event):
        updateMessage = "No errors or warnings."
        msg = "Running make_grid()"
        projectionName = self.projNamesGridTools[self.gridProjection.value]
        self.grd.printMsg(msg, logging.INFO)
        self.grd.clearGrid()
        self.grd.setGridParameters({
            'projection': {
                'name': projectionName,
                'ellps': 'WGS84'
            },
            'centerX': float(self.gridCenterX.value),
            'centerY': float(self.gridCenterY.value),
            'centerUnits': self.gridCenterUnits.value,
            'dx': int(self.dx.value),
            'dy': int(self.dy.value),
            'dxUnits': self.dxUnits.value,
            'dyUnits': self.dyUnits.value,
            'gridResolutionX': float(self.gridResolutionX.value),
            'gridResolutionY': float(self.gridResolutionY.value),
            'gridResolutionXUnits': self.gridResolutionXUnits.value,
            'gridResolutionYUnits': self.gridResolutionYUnits.value,
            'gridMode': int(self.gridMode.value),
            'gridType': self.gridType.value,
            'tilt': float(self.gtilt.value)
        })

        if projectionName == 'LambertConformalConic':
            self.grd.setGridParameters({
                'lon_0': float(self.glon0.value),
                'lat_0': float(self.glat0.value),
                'lat_1': float(self.glat1.value),
                'lat_2': float(self.glat2.value)
            }, subKey='projection')

        if projectionName == 'Mercator':
            self.grd.setGridParameters({
                'lon_0': float(self.glon0.value)
            }, subKey='projection')

        if projectionName == 'Stereographic':
            self.grd.setGridParameters({
                'lon_0': float(self.glon0.value),
                'lat_0': float(self.glat0.value),
                'lat_ts': float(self.glatts.value),
            }, subKey='projection')
        
        self.grd.makeGrid()

        #if self.grd.gridMade:
        if hasattr(self.grd.grid, 'x'):

            # Update the plot if we updated the grid
            self.plotWindow.object = self.make_plot()

            # Update grid info
            self.updateDataView()

            if self.projNamesGridTools[self.gridProjection.value] == 'LambertConformalConic':
                # Grid generation for LCC sets lat_1 and lat_2 based on grid inputs.
                updateMessage = "NOTICE: Grid first and second parallels (lat_1, lat_2) have been changed to (%s, %s)." %\
                    (self.grd.gridInfo['gridParameters']['projection']['lat_1'], self.grd.gridInfo['gridParameters']['projection']['lat_2'])
                self.glat1.value = self.grd.gridInfo['gridParameters']['projection']['lat_1']
                self.glat2.value = self.grd.gridInfo['gridParameters']['projection']['lat_2']

            msg = "Make grid succeeded: %s" % (updateMessage)
            self.grd.printMsg(msg, logging.INFO)
        else:
            msg = "ERROR: Make grid failed."
            self.grd.printMsg(msg, logging.ERROR)

        return

    def make_plot(self):
        msg = "Running make_plot()"
        self.grd.printMsg(msg, logging.INFO)

        selectedProjection = self.plotProjection.value
        projectionName = self.plotProjectionsDict[self.plotProjection.value]

        if self.plotTitle.value != "":
            mp_title = self.plotTitle.value
        else:
            if self.gtilt.value < 0.0 or self.gtilt.value > 0.0:
                mp_title = "%s: " % (selectedProjection) + str(self.dx.value) + "x" + str(self.dy.value) + " with " + str(self.gtilt.value) + " degree tilt"
            else:
                mp_title = "%s: " % (selectedProjection) + str(self.dx.value) + "x" + str(self.dy.value)

        # Check plotGridMode.value to set plot parameter showGridCells
        showGridCellsState = False
        pGridMode = self.plotGridModeDict[self.plotGridMode.value]
        if pGridMode == 'gridCells':
            showGridCellsState = True

        # Determine plot extent (this may vary depending on selected projection)
        plotExtentState = []
        # If we are not using the global projection, use the user supplied extents
        if not(self.plotUseGlobal.value):
            x0pt = self.plotExtentX0.value
            x1pt = self.plotExtentX1.value
            y0pt = self.plotExtentY0.value
            y1pt = self.plotExtentY1.value

            plotExtentState = [x0pt, x1pt, y0pt, y1pt]

        # These inputs will have to change based on selected projection
        self.grd.setPlotParameters(
            {
                'figsize': self.defaultPlotFigureSize,
                'projection' : {
                    'name': projectionName,
                    'ellps': 'WGS84'
                },
                'extent': plotExtentState,
                'iLinewidth': self.plotYLineWidth.value,
                'jLinewidth': self.plotXLineWidth.value,
                'showGridCells': showGridCellsState,
                'title': mp_title,
                'iColor': self.plotColorDict[self.plotYColor.value],
                'jColor': self.plotColorDict[self.plotXColor.value]
            }
        )
        
        # LambertConformalConic
        if projectionName == 'LambertConformalConic':
            self.grd.setPlotParameters({
                'lon_0': float(self.plon0.value),
                'lat_0': float(self.plat0.value),
                'lat_1': float(self.plat1.value),
                'lat_2': float(self.plat2.value)
            }, subKey='projection')

        # NearsidePerspective
        if projectionName == 'NearsidePerspective':
            self.grd.setPlotParameters({
                'lon_0': float(self.plon0.value),
                'lat_0': float(self.plat0.value),
                'satellite_height': 35785831.0,
            }, subKey='projection')

        # Mercator
        if projectionName == 'Mercator':
            self.grd.setPlotParameters({
                'lon_0': float(self.plon0.value)
            }, subKey='projection')

        # Stereographic
        if projectionName == 'Stereographic':
            self.grd.setPlotParameters({
                'lon_0': float(self.plon0.value),
                'lat_0': float(self.plat0.value),
                'lat_ts': float(self.platts.value)
            }, subKey='projection')

        if self.grd.xrOpen:
            (figure, axes) = self.grd.plotGrid()
            msg = "Running make_plot(): done"     
            self.grd.printMsg(msg, logging.INFO)
        else:
            if self.grd.gridMade == False:
                (figure, axes) = self.errorNoGridFigure()
                msg = "Running make_plot(): plotting failure - unspecified grid."
                self.grd.printMsg(msg, logging.ERROR)
            else:
                (figure, axes) = self.errorFigure()
                msg = "Running make_plot(): plotting failure"
                self.grd.printMsg(msg, logging.ERROR)
        return figure

    
    def errorNoGridFigure(self):
        '''Creates a plot for the scenario where the user has not specified the grid before making a plot'''
        
        f = self.grd.newFigure()
        central_longitude = self.grd.getPlotParameter('lon_0', subKey='projection', default=0.0)
        central_latitude = self.grd.getPlotParameter('lat_0', subKey='projection', default=90.0)
        satellite_height = self.grd.getPlotParameter('satellite_height', default=35785831)
        crs = cartopy.crs.NearsidePerspective(central_longitude=central_longitude, central_latitude=central_latitude, satellite_height=satellite_height)
        ax = f.subplots(subplot_kw={'projection': crs})
        if self.grd.usePaneMatplotlib:
            FigureCanvas(f)
        mapExtent = self.grd.getPlotParameter('extent', default=[])
        mapCRS = self.grd.getPlotParameter('extentCRS', default=cartopy.crs.PlateCarree())
        ax.set_global()
        ax.coastlines()
        ax.gridlines()
        ax.set_title("Unspecified Grid", color='red')
        ax.text(0.5, 0.55, 'please create your grid before plotting', transform=ax.transAxes,
                fontsize=10, color='blue', alpha=0.4,
                ha='center', va='center', rotation='0')
        return f, ax
    
    def errorFigure(self):
        '''Create Blank Plot to signal plotting failure. This signals a problem within the user specifications in relation to code capabilities.  '''
        
        f = self.grd.newFigure()
        central_longitude = self.grd.getPlotParameter('lon_0', subKey='projection', default=0.0)
        central_latitude = self.grd.getPlotParameter('lat_0', subKey='projection', default=90.0)
        satellite_height = self.grd.getPlotParameter('satellite_height', default=35785831)
        crs = cartopy.crs.NearsidePerspective(central_longitude=central_longitude, central_latitude=central_latitude, satellite_height=satellite_height)
        ax = f.subplots(subplot_kw={'projection': crs})
        if self.grd.usePaneMatplotlib:
            FigureCanvas(f)
        mapExtent = self.grd.getPlotParameter('extent', default=[])
        mapCRS = self.grd.getPlotParameter('extentCRS', default=cartopy.crs.PlateCarree())
        ax.set_global()
        ax.coastlines()
        ax.gridlines()
        ax.set_title("Plot Failure", color='red')
        ax.text(0.5, 0.55, 'please check plot/grid parameters and retry', transform=ax.transAxes,
                fontsize=10, color='red', alpha=0.4,
                ha='center', va='center', rotation='0')
        return f, ax
    
    def initializePlot(self):
        ''' Plot the initial image upon loading up the application. This is developed to differentiate between plot failure and the first plot.'''
        f = self.grd.newFigure()
        satellite_height = self.grd.getPlotParameter('satellite_height', default=35785831)
        crs = cartopy.crs.NearsidePerspective(central_longitude=290, central_latitude=30, satellite_height=satellite_height)
        ax = f.subplots(subplot_kw={'projection': crs})
        if self.grd.usePaneMatplotlib:
            FigureCanvas(f)
        mapExtent = self.grd.getPlotParameter('extent', default=[])
        mapCRS = self.grd.getPlotParameter('extentCRS', default=cartopy.crs.PlateCarree())
        ax.set_global()
        ax.stock_img()
        ax.coastlines()
        ax.gridlines()
        ax.set_title("Welcome! Please specify your grid and plot parameters")

        return f
    
    def plotRefresh(self, event):
        self.plotWindow.object = self.make_plot()
        return

    def showManual(self):
        manualTabs = pn.Tabs()

        pageMain = pn.WidgetBox('''
        # Instructions
        This is the instruction manual for the application portion of the grid tool library.  Information
        here focus on the operation of this application.  Additional details about
        the MOM6 model can be found in the [MOM6 User Manual](https://mom6.readthedocs.io/){target="_blank"}.
        Additional information about the operation of the grid tool library can be found in the
        [manual](https://github.com/ESMG/gridtools/blob/main/docs/manual/GridUtils.md){target="_blank"}.
        # Information
        Some actions of the application will produce information that will be displayed in the "Information"
        window above.  The window can be cleared by clicking the "Clear Information" button.  If "Logging" is
        enabled, all information in that window are kept.
        # Tabs
        Access to this manual is broken into tabs and unfortunately cannot be hyperlinked together.  Major
        tabs include "Plot", "Grid" and "Setup".
        ## Plot
        The plot tab controls how grids are shown in the "Grid Plot" tab.  Controls include "Projection",
        "Extent" and "Style".  Please see the application manual tab called "Plot" for more information.
        ## Grid
        The grid tab controls how grids are created.  Controls include "Center", "Projection", "Spacing",
        and "Advanced".  Please see the application manual tab called "Grid".
        ## Setup
        The setup tab allows control over "Logging" and other preferences specific to the application.
        ''', width=self.plotWidgetWidth)

        pagePlot = pn.WidgetBox('''
        # Plot
        This tab explains the controls for plotting grids.
        ## Projection
        **Projection**: The plot projection may be different than the grid projection. In most cases, the plot
        and grid projection is the same to demonstrate conformality of the generated grid.

        **Central Longitude**: lon_0 defines the central longitude or central meridian for plotting.  The plot
        is centered over this longitude.  The plot extent may change the view of the plot.  For example,
        for the spherical plots will line up with the selected longitude.

        **Central Latitude**: lat_0 defines the central latitude or latitude of origin for plotting.  The
        plot extent may change the view of the plot.

        **First Parallel**: lat_1 defines the first standard parallel used for Lambert Conformal Conic
        projections.

        **Second Parallel**: lat_2 defines the second standard parallel used for Lambert Conformal Conic
        projections.

        **Latitude of True Scale**: lat_ts defines the latitude where scale is not distorted.  This
        is used in Lambert Conformal Conic and Mercator.  If this setting is used with the scale
        factor (k_0), lat_ts takes precedence.

        **NOTE**: Other projection options described have not been implemented yet.

        ## Extent
        This controls the plot extent in degrees which may override plotting grids over its
        center point.  A checkbox is provided to override the extent parameters and provide
        a global view for the plot.

        ## Style
        This allows some limited changes to the plot style and how to show the grid or grid cells.

        **Plot title**: A title in this text box will be shown on the "Grid Plot".

        **Grid Style**: The grid style tells the plot to just show the grid, show the grid cells or
        show the supergrid cells.

        **x Color**: For a non-rotated grid, this is the j direction color of the grid line.
        
        **y Color**: For a non-rotated grid, this is the i direction color of the grid line.

        **x Line Width**: This is the width in points (1/72 of an inch).  The default width is
        one (1) point.  For super dense grids, using 1/10th (0.1) of a point may show the
        grid with a semiopaque plot.  This is the width of grid lines in the j direction.

        **y Line Width**: This is the width of grid lines in the i direction.

        ''', width=self.plotWidgetWidth)

        pageGrid = pn.WidgetBox('''
        # Grid
        This contains several controls that affect how the grid is generated.
        ## Center
        **Grid Center(X)** and **Grid Center(Y)** are specified in degrees.  This is the absolute center of
        the grid to be generated.  Other controls define grid size and resolution which determines
        how many grid points are generated.

        ## Projection
        These are the same controls as found for the plot projection except they affect the grid
        generation. The additional control is **Tilt** which controls the tilt of the generated
        grid.  The grid rotation is specified in degrees and the rotation is clockwise.

        ## Spacing
        These are the primary controls for controlling the number of grid points in the
        generated grid.

        **dx**: is the total grid distance along the j direction.  Please select the proper
        **dx Units** in degrees or meters.

        **dy**: is the total grid distance along the i direction.  Please select the proper
        **dy Units** in degrees or meters.

        **Grid Resoloution(X)**: This is the distance of individual grid cells in the j direction.
        Please select the proper *Grid Resolution Units(X)* in degrees or meters.

        **Grid Resoloution(Y)**: This is the distance of individual grid cells in the i direction.
        Please select the proper *Grid Resolution Units(X)* in degrees or meters.

        ## Advanced

        ### Grid Reference
        This controls how the grid is grown from the selected latitude (Center Y) and longitude (Center X) using
        degrees or meters.  By default, the grid is grown from the center point
        in both directions based on the size (dy, dx) and grid resolution.
        In the future, grids may be build with other fixed points of reference.

        ### Grid Type
        For now, only MOM6 is supported.  Other grid types may be possible in the future.

        ### Grid Mode
        For MOM6 grids, mode is 2 requests generation of the supergrid.
        This computes vertices for the grid cells and vertices through the center points of the
        grid cells.  At present, this mode should not be anything other than 2 for MOM6 grids.

        **Grid Representation**

        Additional details of the
        [MOM6](https://github.com/ESMG/gridtools/blob/main/docs/grids/MOM6.md){target="_blank"}
        grid and
        [MOM6/ROMS](https://github.com/ESMG/gridtools/blob/main/docs/grids/MOM6ROMS.md){target="_blank"}
        grids can be found in the grid section of
        the user manual.
        ''', width=self.plotWidgetWidth)

        pageSetup = pn.WidgetBox('''
        # Setup
        Please see the "Logging" tab for information about logging under the Setup tab.

        A python wrapper library, numpypi, has been written to provide bitwise-the-same computations
        for some of the numpy math functions.  NOTE: This feature has not been implemented.
        ''', width=self.plotWidgetWidth)

        pageLogging = pn.WidgetBox('''
        # Logging

        Please see the user manual for more information about
        [logging](https://github.com/ESMG/gridtools/blob/main/docs/manual/Logging.md){target="_blank"}.

        **Log filename**: is the filename in which informational messages are saved.

        **Erase log file**: this button may be used to periodically erase the log file for the saving of
        log information.

        **Log level**: For messages emitted to the "Information" panel or using iterative means, you can
        control the amount of detail presented to you or logged in a file.  The logging levels from
        low to high are: NOTSET, DEBUG, INFO, WARNING, ERROR and CRITICAL.  The level set means only
        messages of that level or higher will be shown or logged.  If you want to see all available
        detail, use NOTSET.  NOTE: The detail sent to the "Information" window by default is INFO or
        higher.  The detail sent to a log file, if enabled, is WARNING or higher.  The function for
        emitting messages is `GridUtils.printMsg()`.

        **Debug level**:
        This is a special feature mainly for developers.  If you are planning to "hack" this code, you can
        utilize this feature to assist with debugging existing or new code.  The available debug levels
        do not operate like the logging levels.  For operational use, the debug level is usually OFF.  You
        can use the MESSAGE level to simply emit messsages for debugging.  The debug level RAISE, can emit a
        message and then raise a python exception.  This can normally be done in a try/except block where you
        can try a bit of code and in the except block raise the exception after emitting a debugging message.
        The last level is BREAKPOINT.  This is similar to RAISE except that after the message is emitted, the
        program will attempt to start the python debugger (pdb) using `pdb.set_trace()`.  All messages sent
        via `GridUtils.debugMsg()` are shown at the DEBUG level.

        **NOTE**: Setting breakpoints do not work very well in the application.  The application
        is running a server.  When a breakpoint is triggered, it will crash the server running the application.
        ''', width=self.plotWidgetWidth)

        pageNumpyPi = pn.WidgetBox('''
        # numpypi
        Activating numpypi will replace some mathematical routines in numpy with slower
        routines that will produce bitwise identical results.  For more information on
        this package, please [consult this webpage](https://github.com/adcroft/numpypi){target="_blank"}.
        NOTE: The numpypi module provides portable intrinsic functions that return the
        same bitwise floating-point values on different platforms.  Not all numpy 
        routines are replaced.
        ''', width=self.plotWidgetWidth)

        manualTabs.extend([
            ('Main', pageMain),
            ('Plot', pagePlot),
            ('Grid', pageGrid),
            ('Setup', pageSetup),
            ('Logging', pageLogging),
            ('Numpypi', pageNumpyPi),
        ])

        return manualTabs
    
    def initializeWidgets(self):
        # Widgets
        
        # The text area input box can show many lines and automatically adds a scroll bar for a long message
        self.statusWidget = pn.widgets.TextAreaInput(name='Information', value="", background="skyblue", height=100,
                width=self.plotWidgetWidth+100)
        self.clearLogButton = pn.widgets.Button(name='Clear Information', button_type='primary', height=50, width=125)
        self.clearLogButton.on_click(self.clearInformationWindow)

        # Grid Controls
        # Use: Niki's defaults for rapid testing
        # 30x20 tilt 30 deg lat_0 40.0 lon_0 230.0 Res 1.0
        self.gridProjection = pn.widgets.Select(name='Projection', options=self.projNames, value=self.projNames[1])
        self.gridType = pn.widgets.Select(name="Grid Type", options=self.gridTypes, value=self.gridTypes[0])
        self.gridType.disabled = True
        self.gridResolutionX = pn.widgets.Spinner(name="Grid Resolution(X)", value=1.0, step=0.1, start=0.0, end=1000000.0, width=100)
        self.gridResolutionY = pn.widgets.Spinner(name="Grid Resolution(Y)", value=1.0, step=0.1, start=0.0, end=1000000.0, width=100)
        self.gridResolutionXUnits = pn.widgets.Select(name="Grid Resolution Units(X)", options=self.gridResolutionUnitNames, value=self.gridResolutionUnitNames[0])
        self.gridResolutionYUnits = pn.widgets.Select(name="Grid Resolution Units(Y)", options=self.gridResolutionUnitNames, value=self.gridResolutionUnitNames[0])
        self.gridMode = pn.widgets.Spinner(name="Grid Mode", value=2, step=1, start=1, end=2, width=80)
        self.gridMode.disabled = True
        self.unitNames = ['degrees', 'meters']
        self.dxUnits = pn.widgets.Select(name='dx Units', options=self.unitNames, value=self.unitNames[0])
        self.dyUnits = pn.widgets.Select(name='dy Units', options=self.unitNames, value=self.unitNames[0])
        self.dx = pn.widgets.Spinner(name="dx", value=20.0, step=1.0, start=0.0, end=10000000, width=100)
        self.dy = pn.widgets.Spinner(name="dy", value=30.0, step=1.0, start=0.0, end=10000000, width=100)
        self.glon0 = pn.widgets.Spinner(name="Central Longitude(lon_0) (0 to 360)", value=230.0, step=1.0, start=0.0, end=360.0, width=100)
        self.glat0 = pn.widgets.Spinner(name="Central Latitude(lat_0) (-90 to 90)", value=40.0, step=1.0, start=-90.0, end=90.0, width=100)
        self.glat1 = pn.widgets.Spinner(name="First Parallel(lat_1) (-90 to 90)", value=40.0, step=1.0, start=-90.0, end=90.0, width=100)
        self.glat2 = pn.widgets.Spinner(name="Second Parallel(lat_2) (-90 to 90)", value=40.0, step=1.0, start=-90.0, end=90.0, width=100)
        self.glatts = pn.widgets.Spinner(name="Latitude of True Scale(lat_ts) (-90 to 90)", value=40.0, step=1.0, start=-90.0, end=90.0, width=100)
        self.gtilt = pn.widgets.Spinner(name="Tilt (-90 to 90)", value=30.0, step=0.1, start=-90.0, end=90.0, width=100)
        self.gridCenterX = pn.widgets.Spinner(name='Grid Center(Longitude or X)', value=230.0, step=0.1, start=0.0, end=360.0, width=100)
        self.gridCenterY = pn.widgets.Spinner(name='Grid Center(Latitude or Y)', value=40.0, step=0.1, start=0.0, end=90.0, width=100)
        self.gridCenterUnits = pn.widgets.Select(name='Grid Center Units', options=self.unitNames, value=self.unitNames[0])
        self.gridControlUpdateButton = pn.widgets.Button(name='Make Grid', button_type='primary')
        self.gridControlUpdateButton.on_click(self.make_grid)
        self.xGridControl = pn.widgets.Select(name='Grid Mode(X)', options=self.xGridModes, value=self.xGridModes[1])
        self.xGridControl.disabled = True
        self.yGridControl = pn.widgets.Select(name='Grid Mode(Y)', options=self.yGridModes, value=self.yGridModes[1])
        self.yGridControl.disabled = True

        # Plot Controls
        # Use Niki's defaults for rapid testing
        # extent: -160, -100, 60, 20

        # Projection
        self.plotProjection = pn.widgets.Select(name='Projection', options=self.plotProjections, value=self.plotProjections[0])
        self.plon0 = pn.widgets.Spinner(name="Central Longitude(lon_0) (0 to 360)", value=230.0, step=1.0, start=0.0, end=360.0, width=100)
        self.plat0 = pn.widgets.Spinner(name="Central Latitude(lat_0) (-90 to 90)", value=40.0, step=1.0, start=-90.0, end=90.0, width=100)
        self.plat1 = pn.widgets.Spinner(name="First Parallel(lat_1) (-90 to 90)", value=40.0, step=1.0, start=-90.0, end=90.0, width=100)
        self.plat2 = pn.widgets.Spinner(name="Second Parallel(lat_2) (-90 to 90)", value=40.0, step=1.0, start=-90.0, end=90.0, width=100)
        self.platts = pn.widgets.Spinner(name="Latitude of True Scale(lat_ts) (-90 to 90)", value=40.0, step=1.0, start=-90.0, end=90.0, width=100)

        # Extent
        # CARTOPY: (x0, x1, y0, y1)
        #  https://scitools.org.uk/cartopy/docs/latest/matplotlib/geoaxes.html
        self.plotExtentX0 = pn.widgets.Spinner(name="Longitude(x0) (-180 to 180)", value=-160.0, step=1.0, start=-180.0, end=180.0, width=100)
        self.plotExtentX1 = pn.widgets.Spinner(name="Longitude(x1) (-180 to 180)", value=-100.0, step=1.0, start=-180.0, end=180.0, width=100)
        self.plotExtentY0 = pn.widgets.Spinner(name="Latitude(y0) (-90 to 90)", value=20.0, step=1.0, start=-90.0, end=90.0, width=100)
        self.plotExtentY1 = pn.widgets.Spinner(name="Latitude(y1) (-90 to 90)", value=60.0, step=1.0, start=-90.0, end=90.0, width=100)
        self.plotUseGlobal = pn.widgets.Checkbox(name="Use global extent (disables custom extent)")

        # Style
        self.plotTitle = pn.widgets.TextInput(name='Plot title', value="", width=250)
        self.plotGridMode = pn.widgets.Select(name='Grid Style', options=self.plotGridModesDescriptions, value=self.plotGridModesDescriptions[1])
        self.plotXColor = pn.widgets.Select(name='x Color', options=self.plotColorsDescriptions, value=self.plotColorsDescriptions[3])
        self.plotYColor = pn.widgets.Select(name='y Color', options=self.plotColorsDescriptions, value=self.plotColorsDescriptions[3])
        self.plotXLineWidth = pn.widgets.Spinner(name="x Line Width", value=1.0, step=0.1, start=0.01, end=10.0, width=80)
        self.plotYLineWidth = pn.widgets.Spinner(name="y Line Width", value=1.0, step=0.1, start=0.01, end=10.0, width=80)

        # Grid Save/Load controls

        # Grid file name
        # NOTE: Sharing a text field is not recommended.  It will display
        # more than once, but only one will actually update.
        self.gridFilenameLocal = pn.widgets.TextInput(name='Grid filename', value=self.defaultGridFilename, width=200)
        self.gridFilenameRemote = pn.widgets.TextInput(name='Grid filename', value=self.defaultGridFilename, width=200)

        # File download button and call back function
        # We can't put a variable in the filename= argument below.  It isn't updated
        # when the assigned variable is updated.  Any updates need to be done to
        # saveLocalGridButton.filename when the local file name is changed.  We
        # also discovered if we updated in the callback it also works.  Might
        # encounter a race condition later.  Watch for it.
        self.saveLocalGridButton = pn.widgets.FileDownload(
            label="Download Grid",
            button_type='success',
            callback=self.downloadNetCDF,
            filename=self.defaultGridFilename)

        # Local file selection
        self.localFileSelection = pn.widgets.FileInput(accept='.nc')

        # Remote file selection
        self.remoteFileSelection = pn.widgets.FileSelector('~', file_pattern='*.nc')

        # Load grid buttons
        self.loadLocalGridButton = pn.widgets.Button(name='Load Local Grid', button_type='primary')
        self.loadLocalGridButton.on_click(self.loadLocalGrid)

        self.loadRemoteGridButton = pn.widgets.Button(name='Load Remote Grid', button_type='primary')
        self.loadRemoteGridButton.on_click(self.loadRemoteGrid)

        self.saveRemoteGridButton = pn.widgets.Button(name='Save Remote Grid', button_type='success')
        self.saveRemoteGridButton.on_click(self.saveRemoteGrid)

        # Plot controls
        self.plotControlUpdateButton = pn.widgets.Button(name='Plot', button_type='primary')
        self.plotControlUpdateButton.on_click(self.plotRefresh)

        # The plot itself wrapped in a widget
        # Use panel.pane.Matplotlib(matplotlib.figure)
        self.plotWindow = pn.pane.Matplotlib(self.initializePlot(), width=self.plotWidgetWidth, height=self.plotWidgetHeight)

        # This presents a data view summary of the xarray object
        self.dataView = pn.Column(self.grd.grid, width=self.plotWidgetWidth)

        # Setup controls
        self.logEnableControl = pn.widgets.Checkbox(name="Enable file logging")
        self.logEnableControl.param.watch(self.logEnableCallback, 'value')
        #self.grd.debugMsg('breakpoint',3)
        self.logFilenameControl = pn.widgets.TextInput(name='Log filename', value=self.defaultLogFilename, width=200)
        self.logLevelControl = pn.widgets.Select(name='Log level', options=self.logLevelNames, value=self.logLevelNames[3])
        self.logLevelControl.param.watch(self.logLevelCallback, 'value')
        self.logEraseButton = pn.widgets.Button(name='Erase log file', button_type='danger', height=50, width=200)
        self.logEraseButton.on_click(self.deleteLogfile)
        self.informationLevelControl = pn.widgets.Select(name='Information level', options=self.logLevelNames, value=self.logLevelNames[2])
        self.debugLevelControl = pn.widgets.Select(name='Debug level', options=self.debugLevelNames, value=self.debugLevelNames[0])
        self.debugLevelControl.param.watch(self.debugLevelCallback, 'value')
        self.enableNumpyPiControl = pn.widgets.Checkbox(name="Enable numpypi bitwise-the-same")
        self.enableNumpyPiControl.disabled = True

    def deleteLogfile(self, event):
        '''This function is called as a result of pushing the "Erase logfile" button in the application.
        This places a call into GridTools.deleteLogfile(filename).'''
        self.grd.deleteLogfile(self.logFilenameControl.value)
        return

    def logEnableCallback(self, event):
        msg = "logEnableCallback event"
        self.grd.printMsg(msg, logging.DEBUG)
        if hasattr(event, 'name') and hasattr(event, 'old') and hasattr(event, 'new') and hasattr(event, 'type'):
            if event.name == 'value' and event.type == 'changed':
                if event.new == True:
                    self.grd.enableLogging(self.logFilenameControl.value)
                if event.new == False:
                    self.grd.disableLogging()
        else:
            msg = "Illegal event passed to App.logEnableCallback()"
            self.grd.printMsg(msg, logging.ERROR)

        return

    def logLevelCallback(self, event):
        msg = "logLevelCallback event"
        self.grd.printMsg(msg, logging.DEBUG)
        if hasattr(event, 'name') and hasattr(event, 'old') and hasattr(event, 'new') and hasattr(event, 'type'):
            if event.name == 'value' and event.type == 'changed':
                self.grd.setLogLevel(self.logLevelDict[event.new])
        
    def debugLevelCallback(self, event):
        msg = "debugLevelCallback event"
        self.grd.printMsg(msg, logging.DEBUG)
        if hasattr(event, 'name') and hasattr(event, 'old') and hasattr(event, 'new') and hasattr(event, 'type'):
            if event.name == 'value' and event.type == 'changed':
                self.grd.setDebugLevel(self.debugLevelDict[event.new])
        
    def initializeTabs(self):
        # Tabs

        # Plot, Grid and Setup controls
        self.controlTabs = pn.Tabs()
        self.plotControlTabs = pn.Tabs()
        self.gridControlTabs = pn.Tabs()
        self.setupControlTabs = pn.Tabs()

        # If the Alt layout works, we can replace the existing.
        self.displayTabs = pn.Tabs()
        self.saveLoadTabs = pn.Tabs()

        # Pull controls together

        # Plot controls
        self.plotProjectionControls = pn.WidgetBox('# Plot Projection',
                                                   self.plotProjection,
                                                   self.plon0,
                                                   self.plat0,
                                                   self.plat1,
                                                   self.plat2,
                                                   self.platts,
                                                   self.plotControlUpdateButton)
        self.plotExtentControls = pn.WidgetBox('# Plot Extent',
                                               self.plotExtentX0,
                                               self.plotExtentX1,
                                               self.plotExtentY0,
                                               self.plotExtentY1,
                                               self.plotUseGlobal,
                                               self.plotControlUpdateButton)
        self.plotStyleControls = pn.WidgetBox('# Plot Style',
                                              self.plotTitle,
                                              self.plotGridMode,
                                              self.plotXColor,
                                              self.plotYColor,
                                              self.plotXLineWidth,
                                              self.plotYLineWidth,
                                              self.plotControlUpdateButton)

        # Grid controls
        self.gridCenterControls = pn.WidgetBox('# Grid Center',
                                               self.gridCenterX,
                                               self.gridCenterY,
                                               self.gridCenterUnits,
                                               self.gridControlUpdateButton)
        self.gridProjectionControls = pn.WidgetBox('# Grid Projection', self.gridProjection, self.glon0, self.glat0, self.glat1, self.glat2, self.glatts, self.gtilt, self.gridControlUpdateButton)
        self.gridSpacingControls = pn.WidgetBox('# Grid Spacing',
                                                self.dx,
                                                self.dxUnits,
                                                self.dy,
                                                self.dyUnits,
                                                self.gridResolutionX,
                                                self.gridResolutionXUnits,
                                                self.gridResolutionY,
                                                self.gridResolutionYUnits,
                                                self.gridControlUpdateButton)
        self.gridAdvancedControls = pn.WidgetBox(
            """
            See "Grids" Manual tab for details about these controls.
            ## Grid Reference
            """, self.xGridControl, self.yGridControl, """    
            ## Grid Type
            For now, only MOM6 grids are supported.
            """, self.gridType, """
            ## Grid Mode
            For now, MOM6 grids require grid mode 2.
            """, self.gridMode)

        # Setup controls
        self.loggingControls = pn.WidgetBox('# Logging','''
        These controls allow you to limit the level of output put into the Information window.  Logging to
        an external file is also available.  See the Manual tab called "Logging" for more information.
        ''',
                self.logFilenameControl,
                self.logEnableControl,
                self.logEraseButton,
                self.logLevelControl,
                self.informationLevelControl,
                self.debugLevelControl
        )

        self.numpyPiControls = pn.WidgetBox('''
        # numpypi
        See Manual tab "Numpypi" for more information.

        NOTE: This control does not do anything yet and is disabled.
        ''',
                self.enableNumpyPiControl)

        # Place controls into respective tabs

        # Control hierarchy (left panel)
        # Plot
        #  Projection
        #  Extent
        #  Style
        # Grid
        #  Center
        #  Projection
        #  Spacing
        #  Advanced
        # Setup
        #  Logging

        # Top level
        self.controlTabs.extend([
            ('Plot', self.plotControlTabs),
            ('Grid', self.gridControlTabs),
            ('Setup', self.setupControlTabs)
        ])

        # Plot
        self.plotControlTabs.extend([
            ('Projection', self.plotProjectionControls),
            ('Extent', self.plotExtentControls),
            ('Style', self.plotStyleControls)
        ])

        # Grid
        self.gridControlTabs.extend([
            ('Center', self.gridCenterControls),
            ('Projection', self.gridProjectionControls),
            ('Spacing', self.gridSpacingControls),
            ('Advanced', self.gridAdvancedControls)
        ])

        self.localFilesWindow = pn.WidgetBox(
            '''
            # Local Files
            If you are running this notebook on the same computer as your web browser, accessing files
            from the Local Files tab and the Remote Files tab should look the same.  If you are running
            this notebook on a remote system, you may need to use the Remote Files tab to load grids on
            the remote system.  There may be size limit for loading/downloading files via the web
            browser (Local Files). You may change the grid filename prior to saving the grid.  Do not
            use it for file selection.  At this time, we only accept NetCDF file formats. 
            ''', '''### Upload Grid''', self.localFileSelection, self.loadLocalGridButton,
            ''' ### Download Grid''', self.gridFilenameLocal, self.saveLocalGridButton)

        self.remoteFilesWindow = pn.WidgetBox(self.loadRemoteGridButton, self.gridFilenameRemote, self.saveRemoteGridButton,
            '''
            # Remote Files
            This tab loads and saves grids to the remote system.  If you are running this notebook
            on the same system, either file tab will work.  You may change the grid filename prior
            to saving the grid.  Do not use it for file selection.
            ''', self.remoteFileSelection)

        self.saveLoadTabs.extend([
            ('Local Files', self.localFilesWindow),
            ('Remote Files', self.remoteFilesWindow)
        ])

        # Plotting area, data view, local/remote file access and manual
        self.displayTabs.extend([
            ('Grid Plot', self.plotWindow),
            ('Grid Info', self.dataView),
            ('Local Files', self.localFilesWindow),
            ('Remote Files', self.remoteFilesWindow),
            ('Manual', self.showManual())
        ])

        # Setup
        self.setupControlTabs.extend([
            ('Logging', self.loggingControls),
            ('Numpypi', self.numpyPiControls)
        ])
        
    def initializeDashboard(self):

        # Pull all the final dashboard together in an application
        self.dashboard = pn.WidgetBox(
            pn.Column(pn.Row(self.clearLogButton, self.statusWidget), sizing_mode='stretch_width', width_policy='max'),
            pn.Row(self.controlTabs, self.displayTabs)
        )
        
        # Attach application to GridUtils for integration into panel, etc
        # Do this just before launching the application
        self.grd.application(
            app={
                'messages': self.statusWidget,
                'defaultFigureSize': self.defaultPlotFigureSize
            }
        )
