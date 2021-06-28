'''
Generic class and utility functions for handling
ROMS grids.
'''

from pyproj import CRS, Transformer
from pyproj import Proj
import warnings
import xarray as xr

from .roms_hgrid import *
from .roms_vgrid import *
from . import roms_io as io

class ROMS(object):

    def __init__(self):
        self._grid_type = "ROMS"
        self.roms_grid = dict()

    def getGrid(self, variable=None):
        '''Return the ROMS grid to the caller.
        '''

        return self.roms_grid

    def read_ROMS_grid(self, grd):
        '''Load the ROMS grid previous read by GridUtils().

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        '''

        subgrids = ['psi', 'rho', 'u', 'v'] # also available: 'vert'
        fields = ['lon', 'lat', 'x', 'y', 'mask']

        # Extract fields named based on which grid they are on
        for subgrid in subgrids:
            self.roms_grid[subgrid] = dict()
            for field in fields:
                var_name = field + '_' + subgrid
                #self.roms_grid[subgrid][field] = roms_ds.variables[var_name][:]
                self.roms_grid[subgrid][field] = grd.grid[var_name]
                if (field == 'x') or (field == 'y'):
                     #units = roms_ds.variables[var_name].units.lower()
                     units = grd.grid[var_name].attrs['units'].lower()
                     assert units.startswith('meter')
                elif (field == 'lat') or (field == 'lon'):
                     #units = roms_ds.variables[var_name].units.lower()
                     units = grd.grid[var_name].attrs['units'].lower()
                     assert units.startswith('degree')

        # Extract fields that do not follow the naming pattern
        #self.roms_grid['rho']['h'] = roms_ds.variables['h'][:] # on the rho grid, but not called "h_rho"
        self.roms_grid['rho']['h'] = grd.grid['h'] # on the rho grid, but not called "h_rho"

        self.roms_grid['metadata'] = dict()

        #spherical = roms_ds.variables['spherical'][:]
        spherical = grd.grid['spherical']
        if (spherical == 0) or (spherical == b'F') or (spherical == b'f'):
            self.roms_grid['metadata']['is_spherical'] = False
        elif (spherical == 1) or (spherical == b'T') or (spherical == b't'):
            self.roms_grid['metadata']['is_spherical'] = True
        else:
             warnings.warn('Unrecognized value for spherical in ROMS grid: %s' % str(spherical))

        return

    def trim_ROMS_grid(self):
        '''Remove extraneous points on the outside of the ROMS grid.

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        '''

        old_grid = self.roms_grid
        trim_subgrid = dict()
        # remove the outer:   ( rows,  cols)
        trim_subgrid['psi'] = (False, False) # Cell corners (leave alone)
        trim_subgrid['rho'] = ( True,  True) # Cell centers (remove outer row and column)
        trim_subgrid[ 'u' ] = ( True, False) # U-points (remove outer row)
        trim_subgrid[ 'v' ] = (False,  True) # V-points (remove outer column)

        new_grid = dict()
        for subgrid in old_grid.keys():
            if subgrid == 'metadata':
                 new_grid[subgrid] = dict(old_grid[subgrid])
                 continue
            new_grid[subgrid] = dict()
            trim_rows, trim_cols = trim_subgrid[subgrid]
            for field in old_grid[subgrid].keys():
                if trim_rows and trim_cols:
                    new_grid[subgrid][field] = old_grid[subgrid][field][1:-1,1:-1]
                elif trim_rows:
                    new_grid[subgrid][field] = old_grid[subgrid][field][1:-1, :  ]
                elif trim_cols:
                    new_grid[subgrid][field] = old_grid[subgrid][field][ :  ,1:-1]
                else:
                    new_grid[subgrid][field] = old_grid[subgrid][field][ :  , :  ]

        self.roms_grid = new_grid

        return

    def get_ROMS_grid(self, gridid, zeta=None, hist_file=None, grid_file=None):
        """
        grd = get_ROMS_grid(self, gridid, hist_file=None, grid_file=None)

        Load ROMS grid object.

        gridid is a string with the name of the grid in it.  If hist_file
        and grid_file are not passed into the function, or are set to
        None, then gridid is used to get the grid data from the
        gridid.txt file.

        if hist_file and grid_file are given, and they are the file
        paths to a ROMS history file and grid file respectively, the
        grid information will be extracted from those files, and gridid
        will be used to name that grid for the rest of the python
        session.

        grd.vgrid is a s_coordinate or
        a z_coordinate object, depending on gridid.grdtype.
        grd.vgrid.z_r and grd.vgrid.z_w (grd.vgrid.z for a
        z_coordinate object) can be indexed in order to retreive the
        actual depths. The free surface time serie zeta can be provided
        as an optional argument. Note that the values of zeta are not
        calculated until z is indexed, so a netCDF variable for zeta may
        be passed, even if the file is large, as only the values that
        are required will be retrieved from the file.

        This function is based on code from :cite:p:`ESMG_pyroms_2021`.
        """

        #in this first call to ROMS_gridinfo, we pass in the history file
        #and gridfile info.  If hist_file and grid_file are defined, the
        #grid info will be extracted from those files and will able to be
        #accessed later by gridid
        gridinfo = ROMS_gridinfo(gridid, hist_file=hist_file, grid_file=grid_file)
        name = gridinfo.name

        #we need not pass in hist_file and grid_file here, because the
        #gridinfo file will already have been initialized by the call to
        #ROMS_gridinfo above.
        hgrd = self.get_ROMS_hgrid(gridid)
        vgrid = self.get_ROMS_vgrid(gridid, zeta=zeta)

        #Get ROMS grid
        return ROMS_Grid(name, hgrd, vgrid)

    def get_ROMS_hgrid(self, gridid):
        """
        hgrid = get_ROMS_hgrid(gridid)

        Load ROMS horizontal grid object
        """

        gridinfo = ROMS_gridinfo(gridid)
        grdfile = gridinfo.grdfile

        nc = io.Dataset(grdfile)

        #Check for cartesian or geographical grid
        spherical = nc.variables['spherical'][0]

        #if it is type byte, then convert to string
        try:
          spherical = spherical.decode('utf8')
        except:
          print('Assuming spherical is integer', spherical, type(spherical))

        #Get horizontal grid
        if ((spherical == 0) or (spherical == 'F')):
            #cartesian grid
            print('Load cartesian grid from file')
            if 'x_vert' in list(nc.variables.keys()) and 'y_vert' in list(nc.variables.keys()):
                x_vert = nc.variables['x_vert'][:]
                y_vert = nc.variables['y_vert'][:]
            elif 'x_rho' in list(nc.variables.keys()) and 'y_rho' in list(nc.variables.keys()) \
                     and 'pm' in list(nc.variables.keys()) and 'pn' in list(nc.variables.keys()):
                x_rho = nc.variables['x_rho'][:]
                y_rho = nc.variables['y_rho'][:]
                pm = nc.variables['pm'][:]
                pn = nc.variables['pn'][:]
                try: angle = nc.variables['angle'][:]
                except: angle = np.zeros(x_rho.shape)
                #compute verts from rho point, pm, pn, angle
                x_vert, y_vert = rho_to_vert(x_rho, y_rho, pm, pn, angle)
            else:
                raise ValueError('NetCDF file must contain x_vert and y_vert \
                         or x_rho, y_rho, pm, pn and angle for a cartesian grid')

            if 'x_rho' in list(nc.variables.keys()) and 'y_rho' in list(nc.variables.keys()) and \
                 'x_u' in list(nc.variables.keys()) and 'y_u' in list(nc.variables.keys()) and \
                 'x_v' in list(nc.variables.keys()) and 'y_v' in list(nc.variables.keys()) and \
                 'x_psi' in list(nc.variables.keys()) and 'y_psi' in list(nc.variables.keys()):
                x_rho = nc.variables['x_rho'][:]
                y_rho = nc.variables['y_rho'][:]
                x_u = nc.variables['x_u'][:]
                y_u = nc.variables['y_u'][:]
                x_v = nc.variables['x_v'][:]
                y_v = nc.variables['y_v'][:]
                x_psi = nc.variables['x_psi'][:]
                y_psi = nc.variables['y_psi'][:]
            else:
                x_rho = None
                y_rho = None
                x_u = None
                y_u = None
                x_v = None
                y_v = None
                x_psi = None
                y_psi = None

            if 'pm' in list(nc.variables.keys()) and 'pn' in list(nc.variables.keys()):
                pm = nc.variables['pm'][:]
                dx = 1. / pm
                pn = nc.variables['pn'][:]
                dy = 1. / pn
            else:
                dx = None
                dy = None

            if 'dndx' in list(nc.variables.keys()) and 'dmde' in list(nc.variables.keys()):
                dndx = nc.variables['dndx'][:]
                dmde = nc.variables['dmde'][:]
            else:
                dndx = None
                dmde = None

            if 'angle' in list(nc.variables.keys()):
                angle = nc.variables['angle'][:]
            else:
                angle = None

            #Get cartesian grid
            hgrd = CGrid(x_vert, y_vert, x_rho=x_rho, y_rho=y_rho, \
                         x_u=x_u, y_u=y_u, x_v=x_v, y_v=y_v, \
                         x_psi=x_psi, y_psi=y_psi, dx=dx, dy=dy, \
                         dndx=dndx, dmde=dmde, angle_rho=angle)

            #load the mask
            try:
                hgrd.mask_rho = np.array(nc.variables['mask_rho'][:])
            except:
                hgrd.mask_rho = np.ones(hgrd.x_rho.shape)

        else:
            #geographical grid
            print('Load geographical grid from file')
            #proj = Basemap(projection='merc', resolution=None, lat_0=0, lon_0=0)
            PROJSTRING = "+proj=merc +lat_0=0 +lat_0=0"
            #crs = CRS.from_proj4(PROJSTRING)
            #proj = Transformer.from_crs(crs.geodetic_crs, crs)
            proj = Proj(PROJSTRING, preserve_units=False)

            if 'lon_vert' in list(nc.variables.keys()) and 'lat_vert' in list(nc.variables.keys()):
                lon_vert = nc.variables['lon_vert'][:]
                lat_vert = nc.variables['lat_vert'][:]
            elif 'lon_rho' in list(nc.variables.keys()) and 'lat_rho' in list(nc.variables.keys()) \
                    and 'lon_psi' in list(nc.variables.keys()) and 'lat_psi' in list(nc.variables.keys()):
                lon_rho = nc.variables['lon_rho'][:]
                lat_rho = nc.variables['lat_rho'][:]
                lon_psi = nc.variables['lon_psi'][:]
                lat_psi = nc.variables['lat_psi'][:]
                #compute verts from rho and psi point
                #print("Geo: using rho_to_vert_geo()")
                lon_vert, lat_vert = rho_to_vert_geo(lon_rho, lat_rho, lon_psi, lat_psi)
            else:
                raise ValueError('NetCDF file must contain lon_vert and lat_vert \
                      or lon_rho, lat_rho, lon_psi, lat_psi for a geographical grid')

            if 'lon_rho' in list(nc.variables.keys()) and 'lat_rho' in list(nc.variables.keys()) and \
                  'lon_u' in list(nc.variables.keys()) and 'lat_u' in list(nc.variables.keys()) and \
                  'lon_v' in list(nc.variables.keys()) and 'lat_v' in list(nc.variables.keys()) and \
                  'lon_psi' in list(nc.variables.keys()) and 'lat_psi' in list(nc.variables.keys()):
                lon_rho = nc.variables['lon_rho'][:]
                lat_rho = nc.variables['lat_rho'][:]
                lon_u = nc.variables['lon_u'][:]
                lat_u = nc.variables['lat_u'][:]
                lon_v = nc.variables['lon_v'][:]
                lat_v = nc.variables['lat_v'][:]
                lon_psi = nc.variables['lon_psi'][:]
                lat_psi = nc.variables['lat_psi'][:]
            else:
                lon_rho = None
                lat_rho = None
                lon_u = None
                lat_u = None
                lon_v = None
                lat_v = None
                lon_psi = None
                lat_psi = None

            if 'pm' in list(nc.variables.keys()) and 'pn' in list(nc.variables.keys()):
                pm = nc.variables['pm'][:]
                dx = 1. / pm
                pn = nc.variables['pn'][:]
                dy = 1. / pn
            else:
                dx = None
                dy = None

            if 'dndx' in list(nc.variables.keys()) and 'dmde' in list(nc.variables.keys()):
                dndx = nc.variables['dndx'][:]
                dmde = nc.variables['dmde'][:]
            else:
                dndx = None
                dmde = None

            if 'angle' in list(nc.variables.keys()):
                angle = nc.variables['angle'][:]
            else:
                angle = None

            #Get geographical grid
            hgrd = CGrid_geo(lon_vert, lat_vert, proj, \
                             lon_rho=lon_rho, lat_rho=lat_rho, \
                             lon_u=lon_u, lat_u=lat_u, lon_v=lon_v, lat_v=lat_v, \
                             lon_psi=lon_psi, lat_psi=lat_psi, dx=dx, dy=dy, \
                             dndx=dndx, dmde=dmde, angle_rho=angle)

            #load the mask
            try:
                hgrd.mask_rho = np.array(nc.variables['mask_rho'][:])
            except:
                hgrd.mask_rho = np.ones(hgrd.lat_rho.shape)

        return hgrd

    def get_ROMS_vgrid(self, gridid, zeta=None):
        """
        vgrid = get_ROMS_vgrid(gridid)

        Load ROMS vertical grid object. vgrid is a s_coordinate or
        a z_coordinate object, depending on gridid.grdtype.
        vgrid.z_r and vgrid.z_w (vgrid.z for a z_coordinate object)
        can be indexed in order to retreive the actual depths. The
        free surface time serie zeta can be provided as an optional
        argument. Note that the values of zeta are not calculated
        until z is indexed, so a netCDF variable for zeta may be passed,
        even if the file is large, as only the values that are required
        will be retrieved from the file.
        """

        gridinfo = ROMS_gridinfo(gridid)
        grdfile = gridinfo.grdfile

        nc = io.Dataset(grdfile)

        #Get vertical grid
        try:
            h = nc.variables['h'][:]
        except:
            raise ValueError('NetCDF file must contain the bathymetry h')

        try:
            hraw = nc.variables['hraw'][:]
        except:
            hraw = None

        if gridinfo.grdtype == 'roms':
            Vtrans = gridinfo.Vtrans
            theta_b = gridinfo.theta_b
            theta_s = gridinfo.theta_s
            Tcline = gridinfo.Tcline
            N = gridinfo.N
            if Vtrans == 1:
                vgrid = s_coordinate(h, theta_b, theta_s, Tcline, N, hraw=hraw, zeta=zeta)
            elif Vtrans == 2:
                vgrid = s_coordinate_2(h, theta_b, theta_s, Tcline, N, hraw=hraw, zeta=zeta)
            elif Vtrans == 4:
                vgrid = s_coordinate_4(h, theta_b, theta_s, Tcline, N, hraw=hraw, zeta=zeta)
            elif Vtrans == 5:
                vgrid = s_coordinate_5(h, theta_b, theta_s, Tcline, N, hraw=hraw, zeta=zeta)
            else:
                raise Warning('Unknown vertical transformation Vtrans')

        elif  gridinfo.grdtype == 'z':
            N = gridinfo.N
            depth = gridinfo.depth
            vgrid = z_coordinate(h, depth, N)

        else:
            raise ValueError('Unknown grid type')

        return vgrid

    def edit_mask_mesh(self, hgrid, proj=None, crs=None, **kwargs):

        # Call out to masked hgrid_roms function
        return edit_mask_mesh(hgrid, proj=proj, crs=crs, **kwargs)

class ROMS_Grid(object):
    """
    grd = ROMS_Grid(hgrid, vgrid)

    ROMS Grid object combining horizontal and vertical grid

    This class is based on code from :cite:p:`ESMG_pyroms_2021`.
    """

    def __init__(self, name, hgrid=CGrid, vgrid=s_coordinate):
        self.name = name
        self.hgrid = hgrid
        self.vgrid = vgrid

class ROMS_gridinfo(object):
    '''
    gridinfo = ROMS_gridinfo(gridid,grid_file=None,hist_file=None)

    Return an object with grid information for gridid.

    There are two ways to define the grid information.  If grid_file
    and hist_file are not passed to the object when it is created, the
    information is retrieved from gridid.txt.
    To add new grid please edit your gridid.txt. You need to define
    an environment variable PYROMS_GRIDID_FILE pointing to your
    gridid.txt file. Just copy an existing grid and modify the
    definition accordingly to your case (Be carefull with
    space and blank line).

    If grid_file is the path to a ROMS grid file, and hist_file is the
    path to a ROMS history file, then the grid information will be
    read from those files.  Gridid can then be used to refer to this
    grid information so that the grid and history files do not be
    included in subsequent calls.

    This class is based on code from :cite:p:`ESMG_pyroms_2021`.
    '''

    # Shared variables across all ROMS_gridinfo objects

    #define a dictionary that will remember gridid's that are defined from
    #a history and grid file. Because this is defined in this model's name
    #space, it will remain persistent.  The keys are the gridid, and the
    #values are ROMS_gridinfo objects.
    gridid_dictionary = dict()

    def __init__(self, gridid, grid_file=None, hist_file=None):
      #first determine if the information for the gridid has already been obtained.
      if gridid in self.gridid_dictionary:
        #print 'CJMP> gridid found in gridid_dictionary, grid retrieved from dictionary'
        saved_self = self.gridid_dictionary[gridid]
        for attrib in list(saved_self.__dict__.keys()):
          setattr(self, attrib, getattr(saved_self,attrib))
      else:
        #nope, we need to get the information from gridid.txt or from
        #the grid and history files from the model
        self.id = gridid
        self._get_grid_info(grid_file,hist_file)

        #now save the data in the dictionary, so we don't need to get it again
        self.gridid_dictionary[gridid] = self

    def _get_grid_info(self, grid_file, hist_file):

      #check if the grid_file and hist_files are both null; if so get data from gridid.txt
      if (type(grid_file) == type(None)) & (type(hist_file) == type(None)):
        #print 'CJMP> gridid not in dictionary, data will be retrieved from gridid.txt'
        gridid_file = os.getenv("PYROMS_GRIDID_FILE")
        data = open(gridid_file,'r')
        lines = data.readlines()
        data.close()

        line_nb = 0
        info = []
        for line in lines:
            s = line.split()
            if s[0] == 'id':
                #print(s[2], self.id)
                if s[2] == self.id:
                    for l in range(line_nb, line_nb+5):
                        s = lines[l].split()
                        info.append(s[2])
                        line_nb = line_nb + 1
                    if info[4] == 'roms':
                        for l in range(line_nb, line_nb+4):
                            s = lines[l].split()
                            info.append(s[2])
                    if info[4] == 'z':
                        s = lines[line_nb].split()
                        info.append(s[3:-1])
                        while s[-1:] == ['\\']:
                            line_nb = line_nb + 1
                            s = lines[line_nb].split()
                            info.append(s[:-1])
            line_nb = line_nb + 1

        if info == []:
            raise ValueError('Unknown gridid. Please check your gridid.txt file')

        if info[4] == 'roms':
            self.name     =          info[1]
            self.grdfile  =          info[2]
            self.N        =   np.int(info[3])
            self.grdtype  =          info[4]
            self.Vtrans   =   np.int(info[5])
            self.theta_s  = np.float(info[6])
            self.theta_b  = np.float(info[7])
            self.Tcline   = np.float(info[8])

        elif info[4] == 'z':
            nline = len(info)
            dep = info[5]
            for line in range(6,nline):
                dep = dep + info[line]
            dep = np.array(dep, dtype=np.float)

            self.name    =        info[1]
            self.grdfile =        info[2]
            self.N       = np.int(info[3])
            self.grdtype =        info[4]
            self.depth   = dep

        else:
            raise ValueError('Unknown grid type. Please check your gridid.txt file')

      else: #lets get the grid information from the history and grid files
        #print 'CJMP> getting grid info from ROMS history and grid files'
        assert type(grid_file)!=type(None), 'if specify history file you must specify grid file'
        assert type(hist_file)!=type(None), 'if specify grid file you must specify history file'

        #open history file and get necessary grid information from it.
        hist = netCDF.Dataset(hist_file, 'r')
        # TODO: convert to xarray
        #hist = xr.open_dataset(hist_file)

        #put data into ROMS_gridinfo object
        self.name = self.id
        self.grdfile = grid_file
        self.N = len(hist.dimensions['s_rho'])
        self.grdtype = 'roms'

        #now write this to deal with both ROMS 3 and 2
        try:
          self.Vtrans = np.float(hist.Vstretching)
          self.theta_s = np.float(hist.theta_s)
          self.theta_b = np.float(hist.theta_b)
          self.Tcline = np.float(hist.Tcline)
        except AttributeError:
          try:
            self.Vtrans = np.float(hist.variables['Vstretching'][:])
          except:
            print('variable Vtransform not found in history file. Defaulting to Vtrans=1')
            self.Vtrans = 1
          self.theta_s = np.float(hist.variables['theta_s'][:])
          self.theta_b = np.float(hist.variables['theta_b'][:])
          self.Tcline = np.float(hist.variables['Tcline'][:])
