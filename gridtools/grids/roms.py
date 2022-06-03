'''
Generic class and utility functions for handling
ROMS grids.
'''

from pyproj import CRS, Transformer
from pyproj import Proj
import datetime, warnings
import xarray as xr
import netCDF4 as netCDF

from .roms_hgrid import *
from .roms_vgrid import *
from . import roms_io as io
from gridtools.gridutils import GridUtils
from matplotlib import cm, colors

class ROMS(object):

    def __init__(self, grd=None):
        self._grid_type = "ROMS"
        self.roms_grid = dict()

        # Allow passing of gridtools object primarily
        # to allow for a logging facility for scattered
        # print statements.
        self.grd = grd

    def getGrid(self, variable=None):
        '''Return the ROMS grid to the caller.
        '''

        return self.roms_grid

    def read_ROMS_grid(self, grd, hVar='h'):
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
        self.roms_grid['rho']['h'] = grd.grid[hVar] # on the rho grid, but not called "h_rho"

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
        hgrd.name = gridinfo.name
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
            print('ROMS: Assuming spherical is integer', spherical, type(spherical))

        #Get horizontal grid
        if ((spherical == 0) or (spherical == 'F')):
            #cartesian grid
            print('ROMS: Load cartesian grid from file')
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
            print('ROMS: Load geographical grid from file')
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

    def edit_mask_mesh(self, hgrid, proj=None, **kwargs):

        # Call out to masked hgrid_roms function
        return edit_mask_mesh(hgrid, proj=proj, **kwargs)

    def write_ROMS_grid(self, grd, filename='roms_grd.nc'):
        """
        write_ROMS_grid(grd, filename)

        Write ROMS_CGrid class on a NetCDF file.

        This function is based on code from :cite:p:`ESMG_pyroms_2021`.
        """

        Mm, Lm = grd.hgrid.x_rho.shape


        # Write ROMS grid to file
        nc = netCDF.Dataset(filename, 'w', format='NETCDF3_64BIT')
        nc.Description = 'ROMS grid'
        nc.Author = 'pyroms.grid.write_grd'
        nc.Created = datetime.datetime.now().isoformat()
        nc.type = 'ROMS grid file'

        nc.createDimension('xi_rho', Lm)
        nc.createDimension('xi_u', Lm-1)
        nc.createDimension('xi_v', Lm)
        nc.createDimension('xi_psi', Lm-1)

        nc.createDimension('eta_rho', Mm)
        nc.createDimension('eta_u', Mm)
        nc.createDimension('eta_v', Mm-1)
        nc.createDimension('eta_psi', Mm-1)

        nc.createDimension('xi_vert', Lm+1)
        nc.createDimension('eta_vert', Mm+1)

        nc.createDimension('bath', None)

        if hasattr(grd.vgrid, 's_rho') is True and grd.vgrid.s_rho is not None:
            N, = grd.vgrid.s_rho.shape
            nc.createDimension('s_rho', N)
            nc.createDimension('s_w', N+1)

        def write_nc_var(var, name, dimensions, long_name=None, units=None):
            nc.createVariable(name, 'f8', dimensions)
            if long_name is not None:
                nc.variables[name].long_name = long_name
            if units is not None:
                nc.variables[name].units = units
            nc.variables[name][:] = var
            print(' ... wrote ', name)

        if hasattr(grd.vgrid, 's_rho') is True and grd.vgrid.s_rho is not None:
            write_nc_var(grd.vgrid.theta_s, 'theta_s', (), 'S-coordinate surface control parameter')
            write_nc_var(grd.vgrid.theta_b, 'theta_b', (), 'S-coordinate bottom control parameter')
            write_nc_var(grd.vgrid.Tcline, 'Tcline', (), 'S-coordinate surface/bottom layer width', 'meter')
            write_nc_var(grd.vgrid.hc, 'hc', (), 'S-coordinate parameter, critical depth', 'meter')
            write_nc_var(grd.vgrid.s_rho, 's_rho', ('s_rho'), 'S-coordinate at RHO-points')
            write_nc_var(grd.vgrid.s_w, 's_w', ('s_w'), 'S-coordinate at W-points')
            write_nc_var(grd.vgrid.Cs_r, 'Cs_r', ('s_rho'), 'S-coordinate stretching curves at RHO-points')
            write_nc_var(grd.vgrid.Cs_w, 'Cs_w', ('s_w'), 'S-coordinate stretching curves at W-points')

        write_nc_var(grd.vgrid.h, 'h', ('eta_rho', 'xi_rho'), 'bathymetry at RHO-points', 'meter')
        #ensure that we have a bath dependancy for hraw
        if len(grd.vgrid.hraw.shape) == 2:
            hraw = np.zeros((1, grd.vgrid.hraw.shape[0], grd.vgrid.hraw.shape[1]))
            hraw[0,:] = grd.vgrid.hraw
        else:
            hraw = grd.vgrid.hraw

        write_nc_var(hraw, 'hraw', ('bath', 'eta_rho', 'xi_rho'), 'raw bathymetry at RHO-points', 'meter')
        write_nc_var(grd.hgrid.f, 'f', ('eta_rho', 'xi_rho'), 'Coriolis parameter at RHO-points', 'second-1')
        write_nc_var(1./grd.hgrid.dx, 'pm', ('eta_rho', 'xi_rho'), 'curvilinear coordinate metric in XI', 'meter-1')
        write_nc_var(1./grd.hgrid.dy, 'pn', ('eta_rho', 'xi_rho'), 'curvilinear coordinate metric in ETA', 'meter-1')
        write_nc_var(grd.hgrid.dmde, 'dmde', ('eta_rho', 'xi_rho'), 'XI derivative of inverse metric factor pn', 'meter')
        write_nc_var(grd.hgrid.dndx, 'dndx', ('eta_rho', 'xi_rho'), 'ETA derivative of inverse metric factor pm', 'meter')
        write_nc_var(grd.hgrid.xl, 'xl', (), 'domain length in the XI-direction', 'meter')
        write_nc_var(grd.hgrid.el, 'el', (), 'domain length in the ETA-direction', 'meter')

        write_nc_var(grd.hgrid.x_rho, 'x_rho', ('eta_rho', 'xi_rho'), 'x location of RHO-points', 'meter')
        write_nc_var(grd.hgrid.y_rho, 'y_rho', ('eta_rho', 'xi_rho'), 'y location of RHO-points', 'meter')
        write_nc_var(grd.hgrid.x_u, 'x_u', ('eta_u', 'xi_u'), 'x location of U-points', 'meter')
        write_nc_var(grd.hgrid.y_u, 'y_u', ('eta_u', 'xi_u'), 'y location of U-points', 'meter')
        write_nc_var(grd.hgrid.x_v, 'x_v', ('eta_v', 'xi_v'), 'x location of V-points', 'meter')
        write_nc_var(grd.hgrid.y_v, 'y_v', ('eta_v', 'xi_v'), 'y location of V-points', 'meter')
        write_nc_var(grd.hgrid.x_psi, 'x_psi', ('eta_psi', 'xi_psi'), 'x location of PSI-points', 'meter')
        write_nc_var(grd.hgrid.y_psi, 'y_psi', ('eta_psi', 'xi_psi'), 'y location of PSI-points', 'meter')
        write_nc_var(grd.hgrid.x_vert, 'x_vert', ('eta_vert', 'xi_vert'), 'x location of cell vertices', 'meter')
        write_nc_var(grd.hgrid.y_vert, 'y_vert', ('eta_vert', 'xi_vert'), 'y location of cell vertices', 'meter')

        if hasattr(grd.hgrid, 'lon_rho'):
            write_nc_var(grd.hgrid.lon_rho, 'lon_rho', ('eta_rho', 'xi_rho'), 'longitude of RHO-points', 'degree_east')
            write_nc_var(grd.hgrid.lat_rho, 'lat_rho', ('eta_rho', 'xi_rho'), 'latitude of RHO-points', 'degree_north')
            write_nc_var(grd.hgrid.lon_u, 'lon_u', ('eta_u', 'xi_u'), 'longitude of U-points', 'degree_east')
            write_nc_var(grd.hgrid.lat_u, 'lat_u', ('eta_u', 'xi_u'), 'latitude of U-points', 'degree_north')
            write_nc_var(grd.hgrid.lon_v, 'lon_v', ('eta_v', 'xi_v'), 'longitude of V-points', 'degree_east')
            write_nc_var(grd.hgrid.lat_v, 'lat_v', ('eta_v', 'xi_v'), 'latitude of V-points', 'degree_north')
            write_nc_var(grd.hgrid.lon_psi, 'lon_psi', ('eta_psi', 'xi_psi'), 'longitude of PSI-points', 'degree_east')
            write_nc_var(grd.hgrid.lat_psi, 'lat_psi', ('eta_psi', 'xi_psi'), 'latitude of PSI-points', 'degree_north')
            write_nc_var(grd.hgrid.lon_vert, 'lon_vert', ('eta_vert', 'xi_vert'), 'longitude of cell vertices', 'degree_east')
            write_nc_var(grd.hgrid.lat_vert, 'lat_vert', ('eta_vert', 'xi_vert'), 'latitude of cell vertices', 'degree_north')

        nc.createVariable('spherical', 'c')
        nc.variables['spherical'].long_name = 'Grid type logical switch'
        nc.variables['spherical'][:] = grd.hgrid.spherical
        print(' ... wrote ', 'spherical')

        write_nc_var(grd.hgrid.angle_rho, 'angle', ('eta_rho', 'xi_rho'), 'angle between XI-axis and EAST', 'radians')

        write_nc_var(grd.hgrid.mask_rho, 'mask_rho', ('eta_rho', 'xi_rho'), 'mask on RHO-points')
        write_nc_var(grd.hgrid.mask_u, 'mask_u', ('eta_u', 'xi_u'), 'mask on U-points')
        write_nc_var(grd.hgrid.mask_v, 'mask_v', ('eta_v', 'xi_v'), 'mask on V-points')
        write_nc_var(grd.hgrid.mask_psi, 'mask_psi', ('eta_psi', 'xi_psi'), 'mask on psi-points')

        nc.close()

    def transect(self, var, istart, iend, jstart, jend, grd, Cpos='rho', vert=False, \
                spval=1e37):
        """
        transect, z, lon, lat = transect(var, istart, iend, jstart, jend, grd)

        optional switch:
          - Cpos='rho', 'u' or 'v'       specify the C-grid position where
                                         the variable rely
          - vert=True/False              If True, return the position of
                                         the verticies
          - spval                        special value
          - rtol                         tolerance parameter

        return a vertical transect between the points P1=(istart, jstart)
               and P2=(iend, jend) from 3D variable var

        lon, lat and z contain the C-grid position of the section for plotting.

        If vert=True, lon, lat and z contain contain the position of the
        verticies (to be used with pcolor)
        """

        # compute the depth on Arakawa-C grid position and get grid information

        if Cpos == 'u':
            if vert == True:
                z = grd.vgrid.z_w[0,:]
                z = 0.5 * (z[:,:-1,:] + z[:,1:,:])
                z = np.concatenate((z[:,0:1,:], z, z[:,-1:,:]), 1)
                if grd.hgrid.spherical == 'T':
                    x = 0.5 * (grd.hgrid.lon_vert[:,:-1] + grd.hgrid.lon_vert[:,1:])
                    y = 0.5 * (grd.hgrid.lat_vert[:,:-1] + grd.hgrid.lat_vert[:,1:])
                elif grd.hgrid.spherical == 'F':
                    x = 0.5 * (grd.hgrid.x_vert[:,:-1] + grd.hgrid.x_vert[:,1:])
                    y = 0.5 * (grd.hgrid.y_vert[:,:-1] + grd.hgrid.y_vert[:,1:])
            else:
                z = grd.vgrid.z_r[0,:]
                z = 0.5 * (z[:,:,:-1] + z[:,:,1:])
                if grd.hgrid.spherical == 'T':
                    x = grd.hgrid.lon_u[:]
                    y = grd.hgrid.lat_u[:]
                elif grd.hgrid.spherical == 'F':
                    x = grd.hgrid.x_u[:]
                    y = grd.hgrid.y_u[:]
            mask = grd.hgrid.mask_u[:]

        elif Cpos == 'v':
            if vert == True:
                z = grd.vgrid.z_w[0,:]
                z = 0.5 * (z[:,:,:-1] + z[:,:,1:])
                z = np.concatenate((z[:,:,0:1], z, z[:,:,-1:]), 2)
                if grd.hgrid.spherical == 'T':
                    x = 0.5 * (grd.hgrid.lon_vert[:-1,:] + grd.hgrid.lon_vert[1:,:])
                    y = 0.5 * (grd.hgrid.lat_vert[:-1,:] + grd.hgrid.lat_vert[1:,:])
                elif grd.hgrid.spherical == 'F':
                    x = 0.5 * (grd.hgrid.x_vert[:-1,:] + grd.hgrid.x_vert[1:,:])
                    y = 0.5 * (grd.hgrid.y_vert[:-1,:] + grd.hgrid.y_vert[1:,:])
            else:
                z = grd.vgrid.z_r[0,:]
                z = 0.5 * (z[:,-1:,:] + z[:,1:,:])
                if grd.hgrid.spherical == 'T':
                    x = grd.hgrid.lon_v[:]
                    y = grd.hgrid.lat_v[:]
                elif grd.hgrid.spherical == 'F':
                    x = grd.hgrid.x_v[:]
                    y = grd.hgrid.y_v[:]
            mask = grd.hgrid.mask_v[:]

        elif Cpos == 'rho':
            # for temp, salt, rho
            if vert == True:
                z = grd.vgrid.z_w[0,:]
                z = 0.5 * (z[:,:,:-1] + z[:,:,1:])
                z = 0.5 * (z[:,:-1,:] + z[:,1:,:])
                z = np.concatenate((z[:,:,0:1], z, z[:,:,-1:]), 2)
                z = np.concatenate((z[:,0:1,:], z, z[:,-1:,:]), 1)
                if grd.hgrid.spherical == 'T':
                    x = grd.hgrid.lon_vert[:]
                    y = grd.hgrid.lat_vert[:]
                elif grd.hgrid.spherical == 'F':
                    x = grd.hgrid.lon_vert[:]
                    y = grd.hgrid.lat_vert[:]
            else:
                z = grd.vgrid.z_r[0,:]
                if grd.hgrid.spherical == 'T':
                    x = grd.hgrid.lon_rho[:]
                    y = grd.hgrid.lat_rho[:]
                elif grd.hgrid.spherical == 'F':
                    x = grd.hgrid.x_rho[:]
                    y = grd.hgrid.y_rho[:]
            mask = grd.hgrid.mask_rho[:]

        else:
            raise Warning('%s bad position. Valid Arakawa-C are \
                               rho, u or v.' % Cpos)

        # Find the nearest point between P1 (imin,jmin) and P2 (imax, jmax)
        # -----------------------------------------------------------------
        # Initialization
        i0=istart; j0=jstart; i1=iend;  j1=jend
        istart = float(istart); iend = float(iend)
        jstart = float(jstart); jend = float(jend)

        # Compute equation:  j = aj i + bj
        if istart != iend:
            aj = (jend - jstart ) / (iend - istart)
            bj = jstart - aj * istart
        else:
            aj=10000.
            bj=0.

        # Compute equation:  i = ai j + bi
        if jstart != jend:
            ai = (iend - istart ) / ( jend - jstart )
            bi = istart - ai * jstart
        else:
            ai=10000.
            bi=0.

        # Compute the integer pathway:
        # Chose the strait line with the smallest slope
        if (abs(aj) <=  1 ):
            # Here, the best line is y(x)
            print('Here, the best line is y(x)')
            # If i1 < i0 swap points and remember it has been swapped
            if (i1 <  i0 ):
                i  = i0 ; j  = j0
                i0 = i1 ; j0 = j1
                i1 = i  ; j1 = j

            # compute the nearest j point on the line crossing at i
            n=0
            near = np.zeros(((i1-i0+1),4), dtype=int)
            for i in range(i0,i1+1):
                jj = aj*i + bj
                near[n,0] = i
                near[n,1] = jj
                near[n,2] = np.floor(jj)
                near[n,3] = np.ceil(jj)
                n = n + 1

            if vert == False:
                nearp = np.zeros(((i1-i0+1),4), dtype=int)
                nearp = near
            else:
                # compute the nearest j vert point on the line crossing at i
                n=0
                nearp = np.zeros(((i1-i0+2),4), dtype=int)
                for i in range(i0,i1+2):
                    jj = aj*(i-0.5) + bj
                    nearp[n,0] = i
                    nearp[n,1] = jj
                    nearp[n,2] = np.floor(jj)
                    nearp[n,3] = np.ceil(jj)
                    n = n + 1

        else:
            # Here, the best line is x(y)
            print('Here, the best line is x(y)')
            # If j1 < j0 swap points and remember it has been swapped
            if (j1 <  j0 ):
                i  = i0 ; j  = j0
                i0 = i1 ; j0 = j1
                i1 = i  ; j1 = j

            # compute the nearest i point on the line crossing at j
            n=0
            near = np.zeros(((j1-j0+1),4), dtype=int)
            for j in range(j0,j1+1):
                ii = ai*j + bi
                near[n,0] = j
                near[n,1] = ii
                near[n,2] = np.floor(ii)
                near[n,3] = np.ceil(ii)
                n = n + 1

            if vert == False:
                nearp = np.zeros(((j1-j0+1),4), dtype=int)
                nearp = near
            else:
                # compute the nearest i vert point on the line crossing at j
                n=0
                nearp = np.zeros(((j1-j0+2),4), dtype=int)
                for j in range(j0,j1+2):
                    ii = ai*(j-0.5) + bi
                    nearp[n,0] = j
                    nearp[n,1] = ii
                    nearp[n,2] = np.floor(ii)
                    nearp[n,3] = np.ceil(ii)
                    n = n + 1

        # Now interpolate between the nearest point through the section
        # -------------------------------------------------------------
        # Initialize output variables
        nlev = z.shape[0]

        transect = np.zeros((grd.vgrid.N, near.shape[0]))
        zs = np.zeros((nlev, nearp.shape[0]))
        xs = np.zeros((nlev, nearp.shape[0]))
        ys = np.zeros((nlev, nearp.shape[0]))

        # mask variable
        for k in range(var.shape[0]):
            var[k,:,:] = np.ma.masked_where(mask == 0, var[k,:,:])

        for n in range(near.shape[0]):
            if (abs(aj) <=  1 ):
                # check if our position matches a grid cell
                if (near[n,2] == near[n,3]):
                    transect[:,n] = var[:, near[n,2], near[n,0]]
                else:
                    if mask[near[n,3], near[n,0]] == 0 or mask[near[n,2], near[n,0]] == 0:
                        transect[:,n] = spval
                    else:
                        transect[:,n] = (near[n,1] - near[n,2]) * var[:, near[n,3], near[n,0]] + \
                                       (near[n,3] - near[n,1]) * var[:, near[n,2], near[n,0]]
            else:
                # check if our position matches a grid cell
                if (near[n,2] == near[n,3]):
                    transect[:,n] = var[:, near[n,0], near[n,2]]
                else:
                    if mask[near[n,0], near[n,3]] == 0 or mask[near[n,0], near[n,2]] == 0:
                        transect[:,n] = spval
                    else:
                        transect[:,n] = (near[n,1] - near[n,2]) * var[:, near[n,0], near[n,3]] + \
                                       (near[n,3] - near[n,1]) * var[:, near[n,0], near[n,2]]

        for n in range(nearp.shape[0]):
            if (abs(aj) <=  1 ):
                # check if our position matches a grid cell
                if (nearp[n,2] == nearp[n,3]):
                    zs[:,n] = z[:, nearp[n,2], nearp[n,0]]
                    xs[:,n] = x[nearp[n,2], nearp[n,0]]
                    ys[:,n] = y[nearp[n,2], nearp[n,0]]
                else:
                    zs[:,n] = (nearp[n,1] - nearp[n,2]) * z[:, nearp[n,3], nearp[n,0]] + \
                              (nearp[n,3] - nearp[n,1]) * z[:, nearp[n,2], nearp[n,0]]
                    xs[:,n] = (nearp[n,1] - nearp[n,2]) * x[nearp[n,3], nearp[n,0]] + \
                                (nearp[n,3] - nearp[n,1]) * x[nearp[n,2], nearp[n,0]]
                    ys[:,n] = (nearp[n,1] - nearp[n,2]) * y[nearp[n,3], nearp[n,0]] + \
                                (nearp[n,3] - nearp[n,1]) * y[nearp[n,2], nearp[n,0]]
            else:
                # check if our position matches a grid cell
                if (nearp[n,2] == nearp[n,3]):
                    zs[:,n] = z[:, nearp[n,0], nearp[n,2]]
                    xs[:,n] = x[nearp[n,0], nearp[n,2]]
                    ys[:,n] = y[nearp[n,0], nearp[n,2]]
                else:
                    zs[:,n] = (nearp[n,1] - nearp[n,2]) * z[:, nearp[n,0], nearp[n,3]] + \
                              (nearp[n,3] - nearp[n,1]) * z[:, nearp[n,0], nearp[n,2]]
                    xs[:,n] = (nearp[n,1] - nearp[n,2]) * x[nearp[n,0], nearp[n,3]] + \
                                (nearp[n,3] - nearp[n,1]) * x[nearp[n,0], nearp[n,2]]
                    ys[:,n] = (nearp[n,1] - nearp[n,2]) * y[nearp[n,0], nearp[n,3]] + \
                                (nearp[n,3] - nearp[n,1]) * y[nearp[n,0], nearp[n,2]]

        # mask transect
        transect = np.ma.masked_values(transect, spval)

        return transect, zs, xs, ys

    def transectview(self, var, tindex, istart, iend, jstart, jend, gridid, \
              filename=None, spval=1e37, cmin=None, cmax=None, clev=None, \
              fill=False, contour=False, c=None, jrange=None, hrange=None,\
              fts=None, title=None, map=False, \
              pal=None, clb=True, xaxis='lon', outfile=None):
        """
        transectview(self, var, tindex, istart, iend, jstart, jend, gridid,
                     {optional switch})

        optional switch:
          - filename         if defined, load the variable from file
          - spval            specify spval
          - cmin             set color minimum limit
          - cmax             set color maximum limit
          - clev             set the number of color step
          - fill             use contourf instead of pcolor
          - contour          overlay contour
          - c                desired contour level. If not specified,
                             plot every 4 contour level.
          - jrange           j range
          - hrange           h range
          - fts              set font size (default: 12)
          - title            add title to the plot
          - map              if True, draw a map showing transect location
          - pal              set color map (default: cm.jet)
          - clb              add colorbar (defaul: True)
          - xaxis            use lon or lat for x axis
          - outfile          if defined, write figure to file

        plot vertical transect between the points P1=(istart, jstart)
        and P2=(iend, jend) from 3D variable var. If filename is provided,
        var must be a string and the variable will be load from the file.
        grid can be a grid object or a gridid. In the later case, the grid
        object correponding to the provided gridid will be loaded.
        """

        # get grid
        if type(gridid).__name__ == 'ROMS_Grid':
            grd = gridid
        else:
            #grd = pyroms.grid.get_ROMS_grid(gridid)
            grd = self.get_ROMS_grid(gridid)

        # get variable
        if filename == None:
            var = var
        else:
            data = pyroms.io.Dataset(filename)

            var = data.variables[var]

        Np, Mp, Lp = grd.vgrid.z_r[0,:].shape

        if tindex == -1:
            assert len(var.shape) == 3, 'var must be 3D (no time dependency).'
            N, M, L = var.shape
        else:
            assert len(var.shape) == 4, 'var must be 4D (time plus space).'
            K, N, M, L = var.shape

        # determine where on the C-grid these variable lies
        if N == Np and M == Mp and L == Lp:
            Cpos='rho'
            lon = grd.hgrid.lon_vert
            lat = grd.hgrid.lat_vert
            mask = grd.hgrid.mask_rho

        if N == Np and M == Mp and L == Lp-1:
            Cpos='u'
            lon = 0.5 * (grd.hgrid.lon_vert[:,:-1] + grd.hgrid.lon_vert[:,1:])
            lat = 0.5 * (grd.hgrid.lat_vert[:,:-1] + grd.hgrid.lat_vert[:,1:])
            mask = grd.hgrid.mask_u

        if N == Np and M == Mp-1 and L == Lp:
            Cpos='v'
            lon = 0.5 * (grd.hgrid.lon_vert[:-1,:] + grd.hgrid.lon_vert[1:,:])
            lat = 0.5 * (grd.hgrid.lat_vert[:-1,:] + grd.hgrid.lat_vert[1:,:])
            mask = grd.hgrid.mask_v

        # get transect
        if tindex == -1:
            var = var[:,:,:]
        else:
            var = var[tindex,:,:,:]

        if fill == True:
            #transect, zt, lont, latt, = pyroms.tools.transect(var, istart, iend, \
            transect, zt, lont, latt, = self.transect(var, istart, iend, \
                                         jstart, jend, grd, Cpos, spval=spval)
        else:
            #transect, zt, lont, latt, = pyroms.tools.transect(var, istart, iend, \
            transect, zt, lont, latt, = self.transect(var, istart, iend, \
                                         jstart, jend, grd, Cpos, vert=True, spval=spval)

        if xaxis == 'lon':
            xt = lont
        elif xaxis == 'lat':
            xt = latt

        # plot
        if cmin is None:
            cmin = transect.min()
        else:
            cmin = float(cmin)

        if cmax is None:
            cmax = transect.max()
        else:
            cmax = float(cmax)

        if clev is None:
            clev = 100.
        else:
            clev = float(clev)

        dc = (cmax - cmin)/clev ; vc = np.arange(cmin,cmax+dc,dc)

        if pal is None:
            pal = cm.jet
        else:
            pal = pal

        if fts is None:
            fts = 12
        else:
            fts = fts

        #pal.set_over('w', 1.0)
        #pal.set_under('w', 1.0)
        #pal.set_bad('w', 1.0)

        pal_norm = colors.BoundaryNorm(vc,ncolors=256, clip = False)

        # clear figure
        #plt.clf()

        if map:
            # set axes for the main plot in order to keep space for the map
            if fts < 12:
                ax=None
            else:
                ax = plt.axes([0.15, 0.08, 0.8, 0.65])
        else:
            if fts < 12:
                ax=None
            else:
                ax=plt.axes([0.15, 0.1, 0.8, 0.8])

        if fill:
            cf = plt.contourf(xt, zt, transect, vc, cmap = pal, norm = pal_norm, axes=ax)
        else:
            cf = plt.pcolor(xt, zt, transect, cmap = pal, norm = pal_norm, axes=ax)

        if clb:
            clb = plt.colorbar(cf, fraction=0.075,format='%.2f')
            for t in clb.ax.get_yticklabels():
                t.set_fontsize(fts)

        if contour:
            if c is None:
                c = vc[::10]
            if fill:
                plt.contour(xt, zt, transect, c, colors='k', linewidths=0.5, linestyles='solid', axes=ax)
            else:
                xc = 0.5*(xt[1:,:]+xt[:-1,:])
                xc = 0.5*(xc[:,1:]+xc[:,:-1])
                zc = 0.5*(zt[1:,:]+zt[:-1,:])
                zc = 0.5*(zc[:,1:]+zc[:,:-1])
                plt.contour(xc, zc, transect, c, colors='k', linewidths=0.5, linestyles='solid', axes=ax)

        if jrange is not None:
            plt.xlim(jrange)

        if hrange is not None:
            plt.ylim(hrange)

        if title is not None:
            if map:
                # move the title on the right
                xmin, xmax = ax.get_xlim()
                ymin, ymax = ax.get_ylim()
                xt = xmin - (xmax-xmin)/9.
                yt = ymax + (ymax-ymin)/7.
                plt.text(xt, yt, title, fontsize=fts+4)
            else:
                plt.title(title, fontsize=fts+4)

        plt.xlabel('Latitude', fontsize=fts)
        plt.ylabel('Depth', fontsize=fts)

        if map:
            # draw a map with constant-i slice location
            ax_map = plt.axes([0.4, 0.76, 0.2, 0.23])
            varm = np.ma.masked_where(mask[:,:] == 0, var[var.shape[0]-1,:,:])
            lon_min = lon.min()
            lon_max = lon.max()
            lon_0 = (lon_min + lon_max) / 2.
            lat_min = lat.min()
            lat_max = lat.max()
            lat_0 = (lat_min + lat_max) / 2.
            map = Basemap(projection='merc', llcrnrlon=lon_min, llcrnrlat=lat_min, \
                     urcrnrlon=lon_max, urcrnrlat=lat_max, lat_0=lat_0, lon_0=lon_0, \
                     resolution='i', area_thresh=10.)
            x, y = list(map(lon,lat))
            xt, yt = list(map(lont[0,:],latt[0,:]))
            # fill land and draw coastlines
            map.drawcoastlines()
            map.fillcontinents(color='grey')
            #map.drawmapboundary()
            Basemap.pcolor(map, x, y, varm, axes=ax_map)
            Basemap.plot(map, xt, yt, 'k-', linewidth=3, axes=ax_map)

        if outfile is not None:
            if outfile.find('.png') != -1 or outfile.find('.svg') != -1 or outfile.find('.eps') != -1:
                print('Write figure to file', outfile)
                plt.savefig(outfile, dpi=200, facecolor='w', edgecolor='w', orientation='portrait')
            else:
                print('Unrecognized file extension. Please use .png, .svg or .eps file extension.')

        return


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
    an environment variable ROMS_GRIDID_FILE pointing to your
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
        gridid_file = os.getenv("ROMS_GRIDID_FILE")
        try:
            data = open(gridid_file,'r')
        except:
            print("ERROR: Unable to find ROMS model grid.  It is possible that the environment variable")
            print("ROMS_GRIDID_FILE is not properly defined.  This needs to be set to the path so")
            print("the script can locate the gridid.txt file and load the appropriate ROMS model grid.")
            sys.exit()
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
