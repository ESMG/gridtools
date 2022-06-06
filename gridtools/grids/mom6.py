'''
Generic class and utility funtions for handling MOM6 grids.
'''

import logging, os
import numpy as np
import xarray as xr

from .. import utils
from .. import spherical

class MOM6(object):

    def __init__(self):
        self._grid_type = "MOM6"
        self.mom6_grid = dict()
        self.initMOM6 = False

        # Generic metadata
        self.mom6_grid['netcdf_info'] = dict()
        self.mom6_grid['netcdf_info']['grid_version']  = '0.2' # taken from make_solo_mosaic
        self.mom6_grid['netcdf_info']['code_version']  = utils.get_git_repo_version_info() ### for production
        argv = ["gridtools.grid.mom6.convert_ROMS_to_MOM6 + kwargs"]
        self.mom6_grid['netcdf_info']['history_entry'] = utils.get_history_entry(argv)

    def getGrid(self):
        '''Returns the converted grid as an xarray data structure.

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        '''

        ds = xr.Dataset()

        ds['tile'] = self.mom6_grid['netcdf_info']['tile_str']

        if 'lon' in self.mom6_grid['supergrid'].keys():
            lonGrid = self.mom6_grid['supergrid']['lon']
            ds['x'] = (('nyp','nxp'), lonGrid)
            ds['x'].attrs['standard_name'] = 'geographic_longitude'
            ds['x'].attrs['units'] = 'degrees_east'
            ds['x'].attrs['sha256'] = utils.sha256sum( lonGrid )

            latGrid = self.mom6_grid['supergrid']['lat']
            ds['y'] = (('nyp','nxp'), latGrid)
            ds['y'].attrs['standard_name'] = 'geographic_latitude'
            ds['y'].attrs['units'] = 'degrees_north'
            ds['y'].attrs['sha256'] = utils.sha256sum( latGrid )

            ds.tile.attrs['geometry'] = "spherical"
        else:
            xGrid = self.mom6_grid['supergrid']['x']
            ds['x'] = (('nyp','nxp'), xGrid)
            ds['x'].attrs['standard_name'] = 'geographic_longitude'
            ds['x'].attrs['units'] = 'meters'
            ds['x'].attrs['sha256'] = utils.sha256sum( xGrid )

            yGrid = self.mom6_grid['supergrid']['y']
            ds['y'] = (('nyp','nxp'), yGrid)
            ds['y'].attrs['standard_name'] = 'geographic_latitude'
            ds['y'].attrs['units'] = 'meters'
            ds['y'].attrs['sha256'] = utils.sha256sum( yGrid )

            ds.tile.attrs['geometry'] = "cartesian"

        # xarray=0.19.0 requires unpacking of Dataset variables by using .data
        ds['dx'] = (('nyp', 'nx'), self.mom6_grid['supergrid']['dx'].data)
        ds['dx'].attrs['units'] = 'meters'
        ds['dx'].attrs['sha256'] = utils.sha256sum( self.mom6_grid['supergrid']['dx'] )
        # xarray=0.19.0 requires unpacking of Dataset variables by using .data
        ds['dy'] = (('ny', 'nxp'), self.mom6_grid['supergrid']['dy'].data)
        ds['dy'].attrs['units'] = 'meters'
        ds['dy'].attrs['sha256'] = utils.sha256sum( self.mom6_grid['supergrid']['dy'] )
        # xarray=0.19.0 requires unpacking of Dataset variables by using .data
        ds['area'] = (('ny','nx'), self.mom6_grid['supergrid']['area'].data)
        ds['area'].attrs['units'] = 'meters^2'
        ds['area'].attrs['sha256'] = utils.sha256sum( self.mom6_grid['supergrid']['area'] )
        # xarray=0.19.0 requires unpacking of Dataset variables by using .data
        ds['angle_dx'] = (('nyp','nxp'), self.mom6_grid['supergrid']['angle'].data)
        ds['angle_dx'].attrs['units'] = 'radians'
        ds['angle_dx'].attrs['sha256'] = utils.sha256sum( self.mom6_grid['supergrid']['angle'] )

        self._add_global_attributes(ds)

        return ds

    def setup_MOM6_grid(self, **kwargs):
        '''Create an empty MOM6 data structure.

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.

        **Keyword arguments**:

            * *tileName* (``string``) -- name to assign to the solo tile. Default: "tile1"
            * *inputDirectory* (``string``) -- absolute or relative path to write model input files. Default: "INPUT"
            * *relativeToINPUTDir* (``string``) -- absolute or relative path for mosaic files to the INPUT directory.
              Default: "./" which refers to the "INPUT" directory.
            * *supergridName* (``string``) -- name to assign to the supergrid filename. Default: "ocean_hgrid.nc"
            * *topographyFilename* (``string``) -- filename used to write topographic grid. Default: "ocean_topog.nc"
            * *mosaicFilename* (``string``) -- filename for mosaic file. Default: "ocean_mosaic.nc"
            * *landmaskFilename* (``string``) -- filename used to write the land mask. Default: "land_mask.nc"
            * *oceanmaskFilename* (``string``) -- filename used to write the ocean mask. Default: "ocean_mask.nc"

        :return: none
        :rtype: none
        '''

        # Check and set any defaults to kwargs
        utils.checkArgument(kwargs, 'tileName', "tile1")
        utils.checkArgument(kwargs, 'inputDirectory', "INPUT")
        utils.checkArgument(kwargs, 'relativeToINPUTDir', "./")
        utils.checkArgument(kwargs, 'supergridFilename', "ocean_hgrid.nc")
        utils.checkArgument(kwargs, 'topographyFilename', "ocean_topog.nc")
        utils.checkArgument(kwargs, 'mosaicFilename', "ocean_mosaic.nc")
        utils.checkArgument(kwargs, 'landmaskFilename', "land_mask.nc")
        utils.checkArgument(kwargs, 'oceanmaskFilename', "ocean_mask.nc")

        self.tile_str = kwargs['tileName']
        self.atmos_tile = 'atmos_mosaic_' + self.tile_str
        self.land_tile  =  'land_mosaic_' + self.tile_str
        self.ocean_tile = 'ocean_mosaic_' + self.tile_str

        self.mom6_grid['filenames'] = dict()

        # Always use './' as the directory for files, since FMS always initializes from the
        # "INPUT" directory
        self.mom6_grid['filenames']['directory']            = kwargs['relativeToINPUTDir']

        self.mom6_grid['filenames']['supergrid']            = kwargs['supergridFilename']
        self.mom6_grid['filenames']['topography']           = kwargs['topographyFilename']
        self.mom6_grid['filenames']['mosaic']               = kwargs['mosaicFilename']
        self.mom6_grid['filenames']['land_mask']            = kwargs['landmaskFilename']
        self.mom6_grid['filenames']['ocean_mask']           = kwargs['oceanmaskFilename']
        self.mom6_grid['filenames']['atmos_land_exchange']  = '%sX%s.nc' % (self.atmos_tile, self.land_tile)
        self.mom6_grid['filenames']['atmos_ocean_exchange'] = '%sX%s.nc' % (self.atmos_tile, self.ocean_tile)
        self.mom6_grid['filenames']['land_ocean_exchange']  = '%sX%s.nc' % (self.land_tile, self.ocean_tile)

        # Moved parts into __init__
        #self.mom6_grid['netcdf_info'] = dict()
        self.mom6_grid['netcdf_info']['tile_str']      = self.tile_str
        # No longer needed
        #self.mom6_grid['netcdf_info']['string_length'] = 255
        #self.mom6_grid['netcdf_info']['grid_version']  = '0.2' # taken from make_solo_mosaic
        #self.mom6_grid['netcdf_info']['code_version']  = '$Name: tikal $' ### for testing
        #self.mom6_grid['netcdf_info']['code_version']  = get_git_repo_version_info() ### for production
        #self.mom6_grid['netcdf_info']['code_version']  = 'TODO'
        #argv = ["gridtools.grid.mom6.convert_ROMS_to_MOM6 + kwargs"]
        #self.mom6_grid['netcdf_info']['history_entry'] = get_history_entry(argv)
        #self.mom6_grid['netcdf_info']['history_entry'] = 'TODO'

        self.mom6_grid['supergrid'] = dict()
        self.mom6_grid['cell_grid'] = dict()

        self.initMOM6 = True
        return

    def convert_ROMS_to_MOM6(self, roms_grid, **kwargs):
        '''Convert the ROMS grid data into a skeleton MOM6 grid, mainly by
        merging the four sets of point locations from the ROMS grid
        into a single supergrid for MOM6.

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        '''

        # Determine values from other possible arguments
        minimum_depth = 0.0
        masking_depth = -99999.0
        maximum_depth = -99999.0
        if 'MINIMUM_DEPTH' in kwargs.keys():
            minimum_depth = kwargs['MINIMUM_DEPTH']
        if 'MAXIMUM_DEPTH' in kwargs.keys():
            maximum_depth = kwargs['MAXIMUM_DEPTH']
        if 'MASKING_DEPTH' in kwargs.keys():
            masking_depth = kwargs['MASKING_DEPTH']

        # MINIMUM_DEPTH < MASKING_DEPTH, if MASKING_DEPTH is undefined, set it to MINIMUM_DEPTH
        if minimum_depth < masking_depth:
            masking_depth = minimum_depth
        if masking_depth < -99990.0:
            masking_depth = minimum_depth

        ny, nx = roms_grid['rho']['lon'].shape # trimmed
        self.mom6_grid['cell_grid']['nx'] = nx
        self.mom6_grid['cell_grid']['ny'] = ny

        # Double the size of the *trimmed* ROMS grid to merge the four
        # sets of points.
        nx *= 2
        ny *= 2

        self.mom6_grid['supergrid']['nx'] = nx
        self.mom6_grid['supergrid']['ny'] = ny

        if roms_grid['metadata']['is_spherical']:
            copy_fields = ['lon', 'lat']
        else:
            copy_fields = ['x', 'y']

        # Copy points from ROMS grid
        for field in copy_fields:
            self.mom6_grid['supergrid'][field] = np.zeros((ny+1, nx+1))
            self.mom6_grid['supergrid'][field][ ::2, ::2] = roms_grid['psi'][field] # outer
            self.mom6_grid['supergrid'][field][1::2,1::2] = roms_grid['rho'][field] # inner
            self.mom6_grid['supergrid'][field][1::2, ::2] = roms_grid[ 'u' ][field] # between e/w
            self.mom6_grid['supergrid'][field][ ::2,1::2] = roms_grid[ 'v' ][field] # between n/s

        # Create an ocean and land mask, any land mask depths are zeroed out.
        # 0 = land, 1 = water, but sometimes some huge number indicates
        # "missing" values, which we'll assume to be water
        mask = roms_grid['rho']['mask']
        #mask[mask != 0] = 1
        mask = np.where(mask != 0, 1, 0)
        #self.mom6_grid['cell_grid']['depth'] = roms_grid['rho']['h'] * mask
        # TODO: This can be improved instead of just clobbering land points with masking_depth
        self.mom6_grid['cell_grid']['depth'] = xr.where(mask, roms_grid['rho'][kwargs['topographyVariable']], masking_depth)
        self.mom6_grid['cell_grid']['ocean_mask'] = mask
        self.mom6_grid['cell_grid']['land_mask'] = np.logical_not(mask)

        return

    def approximate_MOM6_grid_metrics(self, **kwargs):
        '''Fill in missing MOM6 supergrid metrics by computing best guess values.

        **Keyword arguments**:

        * *angleCalcMethod* (``integer``) -- set the method for calculating angle_dx. Default: 0

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        '''

        nx = self.mom6_grid['supergrid']['nx']
        ny = self.mom6_grid['supergrid']['ny']

        # Declare shapes
        self.mom6_grid['supergrid']['dx']    = np.zeros((ny+1,nx  ))
        self.mom6_grid['supergrid']['dy']    = np.zeros((ny,  nx+1))
        self.mom6_grid['supergrid']['angle'] = np.zeros((ny+1,nx+1))
        self.mom6_grid['supergrid']['area']  = np.zeros((ny,  nx  ))

        # Rebuild to use generic routines; for now these are copies as well
        if 'lat' in self.mom6_grid['supergrid']:
            self._fill_in_MOM6_supergrid_metrics_spherical(**kwargs)
        else:
            self._fill_in_MOM6_supergrid_metrics_cartesian(**kwargs)

        self._calculate_MOM6_cell_grid_area()

        return

    # FILE WRITING FUNCTIONS / OUTPUT

    def write_MOM6_topography_file(self, grd, **kwargs):
        """Save the MOM6 ocean topography grid in a separate file.

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        """

        # Define target file
        destinationFile = os.path.join(kwargs['inputDirectory'], kwargs['topographyFilename'])
        if os.path.isfile(destinationFile) and not(kwargs['overwrite']):
            msg = ("WARNING: File (%s) exists, use overwrite=True to allow overwriting." % (destinationFile))
            grd.printMsg(msg, logging.WARNING)
            return

        # This routine allows writing of multiple topography variables if
        # specified.  Otherwise, just write the default topographyGrid.
        # If the topographyVariable argument is not set, use [].
        utils.checkArgument(kwargs, 'topographyVariables', [])

        ds = xr.Dataset()

        #nx = mom6_grid['cell_grid']['nx']
        #ny = mom6_grid['cell_grid']['ny']
        #with netCDF4.Dataset(mom6_grid['filenames']['topography'], 'w', format='NETCDF3_CLASSIC') as topog_ds:
        #    # Dimensions
        #    topog_ds.createDimension('nx', nx)
        #    topog_ds.createDimension('ny', ny)
        #    topog_ds.createDimension('ntiles', 1)

        # xarray=0.19.0 requires unpacking of Dataset variables by using .data

        # Retain old behavior for now
        if len(kwargs['topographyVariables']) == 0:
            ds['depth'] = (('ny', 'nx'), kwargs['topographyGrid'].data)
            ds['depth'].attrs['units'] = 'meters'
            ds['depth'].attrs['standard_name'] = 'topographic depth at Arakawa C h-points'
            ds['depth'].attrs['sha256'] = utils.sha256sum( kwargs['topographyGrid'] )
        else:
            for vrb in kwargs['topographyVariables']:
                if vrb in kwargs['topographyGrid'].variables:
                    ds[vrb] = (('ny', 'nx'), kwargs['topographyGrid'][vrb].data)
                    # Copy attributes and rehash
                    attrList = list(kwargs['topographyGrid'][vrb].attrs.keys())
                    if 'sha256' in attrList:
                        attrList.remove('sha256')
                    for att in attrList:
                        ds[vrb].attrs[att] = kwargs['topographyGrid'][vrb].attrs[att]
                    ds[vrb]['sha256'] = utils.sha256sum( kwargs['topographyGrid'][vrb] )

        #    # Variables & Values
        #    hdepth = topog_ds.createVariable('depth', 'f4', ('ny','nx',))
        #    hdepth.units = 'm'
        #    hdepth[:] = mom6_grid['cell_grid']['depth']

        # Global attributes
        self._add_global_attributes(ds)

        # Perform write
        ds.to_netcdf(destinationFile, encoding=grd.removeFillValueAttributes(data=ds))

        return

    def write_MOM6_solo_mosaic_file(self, grd, **kwargs):
        """Write the "solo mosaic" file, which describes to the FMS infrastructure
         where to find the grid file(s).  Based on tools in version 5 of MOM
         (http://www.mom-ocean.org/).

        **Keyword arguments**:

        * *intType* (``string``) -- The default type to be written out to for the FMS
          coupler tile files.  Default: int32

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        """

        # Define target file
        destinationFile = os.path.join(kwargs['inputDirectory'], kwargs['mosaicFilename'])
        if os.path.isfile(destinationFile) and not(kwargs['overwrite']):
            msg = ("WARNING: File (%s) exists, use overwrite=True to allow overwriting." % (destinationFile))
            grd.printMsg(msg, logging.WARNING)
            return

        ds = xr.Dataset()

        # NOTE: This function is very basic, since we're skipping the
        # finding of "contact regions" between the tiles that the real
        # make_solo_mosaic tool performs.  It's not needed right now,
        # since we only have one (regional) tile, but I think this feature
        # will be needed if we ever use a tripolar grid.

        #with netCDF4.Dataset(mom6_grid['filenames']['mosaic'], 'w', format='NETCDF3_CLASSIC') as mosaic_ds:
        #    # Dimenisons
        #    mosaic_ds.createDimension('ntiles', 1)
        #    mosaic_ds.createDimension('string', mom6_grid['netcdf_info']['string_length'])

        #   # Variables & Values
        #   hmosaic = mosaic_ds.createVariable('mosaic', 'c', ('string',))
        #   hmosaic.standard_name = 'grid_mosaic_spec'
        #   hmosaic.children = 'gridtiles'
        #   hmosaic.contact_regions = 'contacts'
        #   hmosaic.grid_descriptor = ''
        #   dirname,filename = os.path.split(mom6_grid['filenames']['mosaic'])
        #   filename,ext = os.path.splitext(filename)
        #   hmosaic[:len(filename)] = filename
        ds['mosaic'] = kwargs['mosaicFilename']
        ds['mosaic'].attrs['standard_name'] = 'grid_mosaic_spec'
        ds['mosaic'].attrs['children'] = 'gridtiles'
        ds['mosaic'].attrs['contact_regions'] = 'contacts'
        ds['mosaic'].attrs['grid_descriptor'] = ''

        #   hgridlocation = mosaic_ds.createVariable('gridlocation', 'c', ('string',))
        #   hgridlocation.standard_name = 'grid_file_location'
        #   this_dir = mom6_grid['filenames']['directory']
        #   hgridlocation[:len(this_dir)] = this_dir
        ds['gridlocation'] = kwargs['relativeToINPUTDir']
        ds['gridlocation'].attrs['standard_name'] = 'grid_file_location'

        #   hgridfiles = mosaic_ds.createVariable('gridfiles', 'c', ('ntiles', 'string',))
        #   hgridfiles[0, :len(mom6_grid['filenames']['supergrid'])] = mom6_grid['filenames']['supergrid']
        ds['gridfiles'] = (('ntiles',), [kwargs['oceanGridFilename']])

        #   hgridtiles = mosaic_ds.createVariable('gridtiles', 'c', ('ntiles', 'string',))
        #   hgridtiles[0, :len(mom6_grid['netcdf_info']['tile_str'])] = mom6_grid['netcdf_info']['tile_str']
        ds['gridtiles'] = (('ntiles',), [kwargs['tileName']])

        # Global attributes
        self._add_global_attributes(ds)

        ds.to_netcdf(destinationFile, encoding=grd.removeFillValueAttributes(data=ds,\
            stringVars={'mosaic': 255, 'gridlocation': 255, 'gridfiles': 255, 'gridtiles': 255}))

        return

    def write_MOM6_land_mask_file(self, grd, **kwargs):
        """Write the land mask file.  Based on 'make_quick_mosaic' tool in version
        5 of MOM (http://www.mom-ocean.org/).

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        """

        # Define target file
        destinationFile = os.path.join(kwargs['inputDirectory'], kwargs['landmaskFilename'])
        if os.path.isfile(destinationFile) and not(kwargs['overwrite']):
            msg = ("WARNING: File (%s) exists, use overwrite=True to allow overwriting." % (destinationFile))
            grd.printMsg(msg, logging.WARNING)
            return

        ds = xr.Dataset()

        #nx = mom6_grid['cell_grid']['nx']
        #ny = mom6_grid['cell_grid']['ny']
        #with netCDF4.Dataset(mom6_grid['filenames']['land_mask'], 'w', format='NETCDF3_CLASSIC') as land_mask_ds:
        #    # Dimenisons (of grid cells, not supergrid)
        #    land_mask_ds.createDimension('nx', nx)
        #    land_mask_ds.createDimension('ny', ny)

        #    # Variables & Values
        #    hmask = land_mask_ds.createVariable('mask', 'd', ('ny', 'nx'))
        #    hmask.standard_name = 'land fraction at T-cell centers'
        #    hmask.units = 'none'
        #    hmask[:] = mom6_grid['cell_grid']['land_mask']

        # Find land mask points using settings from kwargs
        landMask = self._generate_mask('land', grd, **kwargs)

        # xarray=0.19.0 requires unpacking of Dataset variables by using .data
        ds['mask'] = (('ny', 'nx'), landMask.data)
        ds['mask'].attrs['standard_name'] = 'land fraction at T-cell centers'
        ds['mask'].attrs['units'] = 'none'
        ds['mask'].attrs['sha256'] = utils.sha256sum( ds['mask'] )

        # Supergrid can be ('y','x') or ('lat','lon)
        lonVar = 'x'
        latVar = 'y'
        if 'supergrid' in self.mom6_grid:
            if not('x' in self.mom6_grid['supergrid']):
                if 'lon' in self.mom6_grid['supergrid']:
                    lonVar = 'lon'
                    latVar = 'lat'

        if 'supergrid' in self.mom6_grid:
            # xarray=0.19.0 requires unpacking of Dataset variables by using .data
            ds[lonVar] = (('ny', 'nx'), self.mom6_grid['supergrid'][lonVar][1::2,1::2].data)
        else:
            # xarray=0.19.0 requires unpacking of Dataset variables by using .data
            ds[lonVar] = (('ny', 'nx'), grd.grid[lonVar][1::2,1::2].data)

        ds[lonVar].attrs['sha256'] = utils.sha256sum( ds[lonVar] )
        ds[lonVar].attrs['standard_name'] = 'longitude'
        ds[lonVar].attrs['units'] = 'degrees_east'

        if 'supergrid' in self.mom6_grid:
            # xarray=0.19.0 requires unpacking of Dataset variables by using .data
            ds[latVar] = (('ny', 'nx'), self.mom6_grid['supergrid'][latVar][1::2,1::2].data)
        else:
            # xarray=0.19.0 requires unpacking of Dataset variables by using .data
            ds[latVar] = (('ny', 'nx'), grd.grid[latVar][1::2,1::2].data)

        ds[latVar].attrs['sha256'] = utils.sha256sum( ds[latVar] )
        ds[latVar].attrs['standard_name'] = 'latitude'
        ds[latVar].attrs['units'] = 'degrees_north'

        # Global attributes
        self._add_global_attributes(ds)

        enc = grd.removeFillValueAttributes(data=ds)
        enc['mask'].update({'dtype': 'int32'})
        ds.to_netcdf(destinationFile, encoding=enc)

        return

    def write_MOM6_ocean_mask_file(self, grd, **kwargs):
        """Write the ocean mask file.  Based on 'make_quick_mosaic' tool in version
        5 of MOM (http://www.mom-ocean.org/).

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        """

        # Define target file
        destinationFile = os.path.join(kwargs['inputDirectory'], kwargs['oceanmaskFilename'])
        if os.path.isfile(destinationFile) and not(kwargs['overwrite']):
            msg = ("WARNING: File (%s) exists, use overwrite=True to allow overwriting." % (destinationFile))
            grd.printMsg(msg, logging.WARNING)
            return

        ds = xr.Dataset()

        #nx = mom6_grid['cell_grid']['nx']
        #ny = mom6_grid['cell_grid']['ny']
        #with netCDF4.Dataset(mom6_grid['filenames']['ocean_mask'], 'w', format='NETCDF3_CLASSIC') as ocean_mask_ds:
        #    # Dimenisons (of grid cells, not supergrid)
        #    ocean_mask_ds.createDimension('nx', nx)
        #    ocean_mask_ds.createDimension('ny', ny)

        #    # Variables & Values
        #    hmask = ocean_mask_ds.createVariable('mask', 'd', ('ny', 'nx'))
        #    hmask.standard_name = 'ocean fraction at T-cell centers'
        #    hmask.units = 'none'
        #    hmask[:] = mom6_grid['cell_grid']['ocean_mask']

        # Find land mask points using settings from kwargs
        oceanMask = self._generate_mask('ocean', grd, **kwargs)

        # xarray=0.19.0 requires unpacking of Dataset variables by using .data
        ds['mask'] = (('ny', 'nx'), oceanMask.data)
        ds['mask'].attrs['standard_name'] = 'ocean fraction at T-cell centers'
        ds['mask'].attrs['units'] = 'none'
        ds['mask'].attrs['sha256'] = utils.sha256sum( ds['mask'] )

        # Supergrid can be ('y','x') or ('lat','lon)
        lonVar = 'x'
        latVar = 'y'
        if 'supergrid' in self.mom6_grid:
            if not('x' in self.mom6_grid['supergrid']):
                if 'lon' in self.mom6_grid['supergrid']:
                    lonVar = 'lon'
                    latVar = 'lat'

        if 'supergrid' in self.mom6_grid:
            # xarray=0.19.0 requires unpacking of Dataset variables by using .data
            ds[lonVar] = (('ny', 'nx'), self.mom6_grid['supergrid'][lonVar][1::2,1::2].data)
        else:
            # xarray=0.19.0 requires unpacking of Dataset variables by using .data
            ds[lonVar] = (('ny', 'nx'), grd.grid[lonVar][1::2,1::2].data)

        ds[lonVar].attrs['sha256'] = utils.sha256sum( ds[lonVar] )
        ds[lonVar].attrs['standard_name'] = 'longitude'
        ds[lonVar].attrs['units'] = 'degrees_east'

        if 'supergrid' in self.mom6_grid:
            # xarray=0.19.0 requires unpacking of Dataset variables by using .data
            ds[latVar] = (('ny', 'nx'), self.mom6_grid['supergrid'][latVar][1::2,1::2].data)
        else:
            # xarray=0.19.0 requires unpacking of Dataset variables by using .data
            ds[latVar] = (('ny', 'nx'), grd.grid[latVar][1::2,1::2].data)

        ds[latVar].attrs['sha256'] = utils.sha256sum( ds[latVar] )
        ds[latVar].attrs['standard_name'] = 'latitude'
        ds[latVar].attrs['units'] = 'degrees_north'

        # Global attributes
        self._add_global_attributes(ds)

        enc = grd.removeFillValueAttributes(data=ds)
        enc['mask'].update({'dtype': 'int32'})
        ds.to_netcdf(destinationFile, encoding=enc)

        return

    def write_MOM6_exchange_grid_files(self, grd, **kwargs):
        """Write three exchange grid files.
        Based on 'make_quick_mosaic' tool in version 5 of MOM (http://www.mom-ocean.org/).

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        """

        # Exchange grids to write
        exchangeGrids = [
            ('atmos', 'land'),
            ('atmos', 'ocean'),
            ('land', 'ocean')
        ]

        # Set default values for some keywords
        utils.checkArgument(kwargs, 'noLandMosaic', False)
        utils.checkArgument(kwargs, 'haveLandPoints', True)

        # Calculate cell_grid area (if needed) - this happens if
        # this is called separately from the ROMS to MOM6 conversion tool.
        if not(self.initMOM6):
            self.setup_MOM6_grid(**kwargs)
            # Copy supergrid area to internal variable
            self.mom6_grid['supergrid']['area'] = grd.grid['area']
            self._calculate_MOM6_cell_grid_area()

        # Loop for the three types
        for name1, name2 in exchangeGrids:

            # If no land mosaic is requested, skip writing these files
            if kwargs['noLandMosaic']:
                if name1 == 'land' or name2 == 'land':
                    continue

            # If there are no land grid points, skip atmos/land exchange file
            if not(kwargs['haveLandPoints']):
                if name1 == 'atmos' and name2 == 'land':
                    continue

            ds = xr.Dataset()

            # calculate the exchange grid for name1 X name2

            #mask = mom6_grid['cell_grid'][name2 + '_mask']
            mask = self._generate_mask(name2, grd, **kwargs)

            tile_cells_j, tile_cells_i = np.where(mask == 1)
            tile_cells = np.column_stack((tile_cells_i, tile_cells_j)) + 1 # +1 converts from Python indices to Fortran
            #print(type(self.mom6_grid['cell_grid']['area']), type(mask))

            # In xarray, to pull cell values out for matching mask, the variable and mask have to appear in the same
            # dataset.
            dsCombined = xr.Dataset()
            # xarray=0.19.0 requires unpacking of Dataset variables by using .data
            dsCombined['area'] = (('ny','nx'), self.mom6_grid['cell_grid']['area'].data)
            dsCombined['mask'] = mask
            dsCombined['sha256'] = utils.sha256sum( self.mom6_grid['cell_grid']['area'] )
            idx = np.nonzero(mask==1)

            #breakpoint()
            #xgrid_area = self.mom6_grid['cell_grid']['area'][mask == 1]
            xgrid_area = dsCombined['area'][idx[0], idx[1]]
            ncells = len(xgrid_area)
            tile_dist = np.zeros((ncells,2))

            # write out exchange grid file

            filename_key = '%s_%s_exchange' % (name1, name2)
            filename = self.mom6_grid['filenames'][filename_key]
            # Define target file
            destinationFile = os.path.join(kwargs['inputDirectory'], filename)
            if os.path.isfile(destinationFile) and not(kwargs['overwrite']):
                msg = ("WARNING: File (%s) exists, use overwrite=True to allow overwriting." % (destinationFile))
                grd.printMsg(msg, logging.WARNING)
                continue

            #with netCDF4.Dataset(filename, 'w', format='NETCDF3_CLASSIC') as exchange_ds:
            #   exchange_ds.createDimension('string', mom6_grid['netcdf_info']['string_length'])
            #   exchange_ds.createDimension('ncells', ncells)
            #   exchange_ds.createDimension('two', 2)

            contact_str = '{0}_mosaic:{2}::{1}_mosaic:{2}'.format(name1, name2, kwargs['tileName'])
            #   hcontact = exchange_ds.createVariable('contact', 'c', ('string',))
            #   hcontact.standard_name = 'grid_contact_spec'
            #   hcontact.contact_type = 'exchange'
            #   hcontact.parent1_cell = 'tile1_cell'
            #   hcontact.parent2_cell = 'tile2_cell'
            #   hcontact.xgrid_area_field = 'xgrid_area'
            #   hcontact.distant_to_parent1_centroid = 'tile1_distance'
            #   hcontact.distant_to_parent2_centroid = 'tile2_distance'
            #   hcontact[0:len(contact_str)] = contact_str
            ds['contact'] = contact_str
            ds['contact'].attrs['standard_name'] = 'grid_contact_spec'
            ds['contact'].attrs['contact_type'] = 'exchange'
            ds['contact'].attrs['parent1_cell'] = 'tile1_cell'
            ds['contact'].attrs['parent2_cell'] = 'tile2_cell'
            ds['contact'].attrs['xgrid_area_field'] = 'xgrid_area'
            ds['contact'].attrs['distant_to_parent1_centroid'] = 'tile1_distance'
            ds['contact'].attrs['distant_to_parent2_centroid'] = 'tile2_distance'

            #   htile1_cell = exchange_ds.createVariable('tile1_cell', 'i', ('ncells', 'two'))
            #   htile1_cell.standard_name = 'parent_cell_indices_in_mosaic1'
            #   htile1_cell[:] = tile_cells
            ds['tile1_cell'] = (('ncells', 'two'), tile_cells)
            ds['tile1_cell'].attrs['standard_name'] = 'parent_cell_indices_in_mosaic1'

            #   htile2_cell = exchange_ds.createVariable('tile2_cell', 'i', ('ncells', 'two'))
            #   htile2_cell.standard_name = 'parent_cell_indices_in_mosaic2'
            #   htile2_cell[:] = tile_cells
            ds['tile2_cell'] = (('ncells', 'two'), tile_cells)
            ds['tile2_cell'].attrs['standard_name'] = 'parent_cell_indices_in_mosaic2'

            #   hxgrid_area = exchange_ds.createVariable('xgrid_area', 'd', ('ncells',))
            #   hxgrid_area.standard_name = 'exchange_grid_area'
            #   hxgrid_area.units = 'm2'
            #   hxgrid_area[:] = xgrid_area
            # xarray=0.19.0 requires unpacking of Dataset variables by using .data
            ds['xgrid_area'] = (('ncells'), xgrid_area.data)
            ds['xgrid_area'].attrs['standard_name'] = 'exchange_grid_area'
            ds['xgrid_area'].attrs['units'] = 'm2'

            #   htile1_dist = exchange_ds.createVariable('tile1_distance', 'd', ('ncells', 'two'))
            #   htile1_dist.standard_name = 'distance_from_parent1_cell_centroid'
            #   htile1_dist[:] = tile_dist
            ds['tile1_distance'] = (('ncells', 'two'), tile_dist)
            ds['tile1_distance'].attrs['standard_name'] = 'distance_from_parent1_cell_centroid'

            #   htile2_dist = exchange_ds.createVariable('tile2_distance', 'd', ('ncells', 'two'))
            #   htile2_dist.standard_name = 'distance_from_parent2_cell_centroid'
            #   htile2_dist[:] = tile_dist
            ds['tile2_distance'] = (('ncells', 'two'), tile_dist)
            ds['tile2_distance'].attrs['standard_name'] = 'distance_from_parent2_cell_centroid'

            # Global attributes
            self._add_global_attributes(ds)

            enc = grd.removeFillValueAttributes(data = ds, stringVars = {'contact': 255})
            # For the FMS coupler, *_cell variables must be i4/int32
            intType = 'int32'
            if 'intType' in kwargs.keys():
                intType = kwargs['intType']
            enc['tile1_cell'] = {'dtype': intType}
            enc['tile2_cell'] = {'dtype': intType}
            ds.to_netcdf(destinationFile, encoding = enc)

        return

    def write_MOM6_coupler_mosaic_file(self, grd, **kwargs):
        """Write the compler mosaic file, which references all the rest.
        Based on 'make_quick_mosaic' tool in version 5 of MOM (http://www.mom-ocean.org/).

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        """

        def add_string_var_1d(ds, var_name, standard_name, value, strVarMap):
            """Creates and stores values for a 1-dimensional string variable."""
            #    id_var = fid.createVariable(var_name, 'c', ('string',))
            #    id_var.standard_name = standard_name
            #    id_var[0:len(value)] = value
            strVarMap[var_name] = 255
            ds[var_name] = value
            ds[var_name].attrs['standard_name'] = standard_name

        def add_string_var_2d(ds, var_name, dim_name, standard_name, value, strVarMap):
            """Creates and stores values for a 2-dimensional string variable, for
            which the first dimension has length 1."""
            #    id_var = fid.createVariable(var_name, 'c', (dim_name, 'string'))
            #    id_var.standard_name = standard_name
            #    id_var[0, 0:len(value)] = value
            strVarMap[var_name] = 255
            ds[var_name] = ((dim_name,), [value])
            ds[var_name].attrs['standard_name'] = standard_name

        # Set default values for some keywords
        utils.checkArgument(kwargs, 'noLandMosaic', False)
        utils.checkArgument(kwargs, 'haveLandPoints', True)

        # Accumulate string variables for encoding
        strVarMap = dict()

        # Initialize mom6_grid[] (if needed) - this happens if
        # this is called separately from the ROMS to MOM6 conversion tool.
        if not(self.initMOM6):
            self.setup_MOM6_grid(**kwargs)

        # Define target file
        destinationFile = os.path.join(kwargs['inputDirectory'], kwargs['couplerMosaicFilename'])
        if os.path.isfile(destinationFile) and not(kwargs['overwrite']):
            msg = ("WARNING: File (%s) exists, use overwrite=True to allow overwriting." % (destinationFile))
            grd.printMsg(msg, logging.WARNING)
            return

        ds = xr.Dataset()

        #with netCDF4.Dataset('mosaic.nc', 'w', format='NETCDF3_CLASSIC') as mosaic_ds:
        #    mosaic_ds.createDimension('string', mom6_grid['netcdf_info']['string_length'])
        #    mosaic_ds.createDimension('nfile_aXo', 1)
        #    mosaic_ds.createDimension('nfile_aXl', 1)
        #    mosaic_ds.createDimension('nfile_lXo', 1)

        # same mosaic file for all three -- just like when "make_solo_mosaic" is used

        add_string_var_1d(ds, 'atm_mosaic_dir',  'directory_storing_atmosphere_mosaic', self.mom6_grid['filenames']['directory'], strVarMap)
        add_string_var_1d(ds, 'atm_mosaic_file', 'atmosphere_mosaic_file_name',         self.mom6_grid['filenames']['mosaic']   , strVarMap)
        add_string_var_1d(ds, 'atm_mosaic',      'atmosphere_mosaic_name',              'atmos_mosaic'                     , strVarMap)

        if kwargs['noLandMosaic']:
            add_string_var_1d(ds, 'lnd_mosaic_dir',  'directory_storing_land_mosaic',       self.mom6_grid['filenames']['directory'],  strVarMap)
            add_string_var_1d(ds, 'lnd_mosaic_file', 'land_mosaic_file_name',               self.mom6_grid['filenames']['mosaic']   ,  strVarMap)
            add_string_var_1d(ds, 'lnd_mosaic',      'land_mosaic_name',                    'atmos_mosaic'                      ,  strVarMap)
        else:
            add_string_var_1d(ds, 'lnd_mosaic_dir',  'directory_storing_land_mosaic',       self.mom6_grid['filenames']['directory'],  strVarMap)
            add_string_var_1d(ds, 'lnd_mosaic_file', 'atmospheric_mosaic_file_name',        self.mom6_grid['filenames']['mosaic']   ,  strVarMap)
            add_string_var_1d(ds, 'lnd_mosaic',      'land_mosaic_name',                    'land_mosaic'                      ,  strVarMap)

        add_string_var_1d(ds, 'ocn_mosaic_dir',  'directory_storing_ocean_mosaic',      self.mom6_grid['filenames']['directory'],  strVarMap)
        add_string_var_1d(ds, 'ocn_mosaic_file', 'ocean_mosaic_file_name',              self.mom6_grid['filenames']['mosaic']   ,  strVarMap)
        add_string_var_1d(ds, 'ocn_mosaic',      'ocean_mosaic_name',                   'ocean_mosaic'                     ,  strVarMap)

        add_string_var_1d(ds, 'ocn_topog_dir',   'directory_storing_ocean_topog',       self.mom6_grid['filenames']['directory'],  strVarMap)
        add_string_var_1d(ds, 'ocn_topog_file',  'ocean_topog_file_name',               self.mom6_grid['filenames']['topography'], strVarMap)

        add_string_var_2d(ds, 'aXo_file', 'nfile_aXo', 'atmXocn_exchange_grid_file', self.mom6_grid['filenames']['atmos_ocean_exchange'], strVarMap)
        if not(kwargs['noLandMosaic']):
            # If no land points exist in the ocean grid, do not use atmos to land exchange
            if kwargs['haveLandPoints']:
                add_string_var_2d(ds, 'aXl_file', 'nfile_aXl', 'atmXlnd_exchange_grid_file', self.mom6_grid['filenames']['atmos_land_exchange'] , strVarMap)
            add_string_var_2d(ds, 'lXo_file', 'nfile_lXo', 'lndXocn_exchange_grid_file', self.mom6_grid['filenames']['land_ocean_exchange'] , strVarMap)
        else:
            # If no land mosaic is specified, the atmos mosaic is used instead
            add_string_var_2d(ds, 'lXo_file', 'nfile_lXo', 'lndXocn_exchange_grid_file', self.mom6_grid['filenames']['atmos_ocean_exchange'], strVarMap)

        # Global attributes
        self._add_global_attributes(ds)

        ds.to_netcdf(destinationFile, encoding=grd.removeFillValueAttributes(data=ds,\
            stringVars=strVarMap))

        return

    # PRIVATE FUNCTIONS

    def _add_global_attributes(self, ds):
        '''Helper function to add common metadata to xarray datasets.

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        '''
        ds.attrs['grid_version'] = self.mom6_grid['netcdf_info']['grid_version']
        ds.attrs['code_version'] = self.mom6_grid['netcdf_info']['code_version']
        ds.attrs['history']      = self.mom6_grid['netcdf_info']['history_entry']

        return

    def _calculate_MOM6_cell_grid_area(self):
        """Compute the area for the MOM6 cells (not the sub-cells of the
        supergrid).

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        """

        # Combine areas of smaller supergrid cells into areas of cell-grid cells
        a00 = self.mom6_grid['supergrid']['area'][0::2,0::2]
        a01 = self.mom6_grid['supergrid']['area'][0::2,1::2]
        a10 = self.mom6_grid['supergrid']['area'][1::2,0::2]
        a11 = self.mom6_grid['supergrid']['area'][1::2,1::2]
        self.mom6_grid['cell_grid']['area'] = a00 + a01 + a10 + a11

    def _fill_in_MOM6_supergrid_metrics_spherical(self, **kwargs):
        """Fill in missing MOM6 supergrid metrics by computing best guess
        values based on latitude and longitude coordinates.

        **Keyword arguments**:

        * *angleCalcMethod* (``integer``) -- set the method for calculating angle_dx. Default: 0

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        """

        lat = self.mom6_grid['supergrid']['lat']
        lon = self.mom6_grid['supergrid']['lon']

        # Approximate edge lengths as great arcs
        R = 6370.e3 # Radius of sphere
        self.mom6_grid['supergrid']['dx'][:,:] = R * spherical.angle_through_center( (lat[ :,1:],lon[ :,1:]), (lat[:  ,:-1],lon[:  ,:-1]) )
        self.mom6_grid['supergrid']['dy'][:,:] = R * spherical.angle_through_center( (lat[1:, :],lon[1:, :]), (lat[:-1,:  ],lon[:-1,:  ]) )

        # Approximate angles using centered differences in interior, and side differences on left/right edges
        # TODO: Why do something different at the edges when we have extra ROMS points available?
        # Because we're using a big enough footprint to need to.
        cos_lat = np.cos(np.radians(lat))
        #self.mom6_grid['supergrid']['angle'][:,1:-1] = np.arctan( (lat[:,2:] - lat[:,:-2]) / ((lon[:,2:] - lon[:,:-2]) * cos_lat[:,1:-1]) )
        #self.mom6_grid['supergrid']['angle'][:, 0  ] = np.arctan( (lat[:, 1] - lat[:, 0 ]) / ((lon[:, 1] - lon[:, 0 ]) * cos_lat[:, 0  ]) )
        #self.mom6_grid['supergrid']['angle'][:,-1  ] = np.arctan( (lat[:,-1] - lat[:,-2 ]) / ((lon[:,-1] - lon[:,-2 ]) * cos_lat[:,-1  ]) )

        # Compute it twice to recover from dateline problems, if any
        angle = np.zeros(lat.shape)
        angle2 = np.zeros(lat.shape)

        # A special edge case where angle computation has problems with certain grids.
        # See: https://github.com/ESMG/gridtools/issues/19
        #
        # angle_dx Angle Calculation Method: 1
        if 'angleCalcMethod' in kwargs.keys():
            if kwargs['angleCalcMethod'] == 1:
                angle[:,1:-1] = np.arctan2( (lat[:,2:] - lat[:,:-2]) , ((lon[:,2:] - lon[:,:-2]) * cos_lat[:,1:-1]) )
                angle[:, 0  ] = np.arctan2( (lat[:, 1] - lat[:, 0 ]) , ((lon[:, 1] - lon[:, 0 ]) * cos_lat[:, 0  ]) )
                angle[:,-1  ] = np.arctan2( (lat[:,-1] - lat[:,-2 ]) , ((lon[:,-1] - lon[:,-2 ]) * cos_lat[:,-1  ]) )
        lon = np.where(lon < 0., lon+360, lon)
        angle2[:,1:-1] = np.arctan2( (lat[:,2:] - lat[:,:-2]) , ((lon[:,2:] - lon[:,:-2]) * cos_lat[:,1:-1]) )
        angle2[:, 0  ] = np.arctan2( (lat[:, 1] - lat[:, 0 ]) , ((lon[:, 1] - lon[:, 0 ]) * cos_lat[:, 0  ]) )
        angle2[:,-1  ] = np.arctan2( (lat[:,-1] - lat[:,-2 ]) , ((lon[:,-1] - lon[:,-2 ]) * cos_lat[:,-1  ]) )
        self.mom6_grid['supergrid']['angle'][:,:] = np.maximum(angle, angle2)

        # Approximate cell areas as that of spherical polygon
        self.mom6_grid['supergrid']['area'][:,:] = R * R * spherical.quad_area(lat, lon)

        return

    def _fill_in_MOM6_supergrid_metrics_cartesian(self, **kwargs):
        """Fill in missing MOM6 supergrid metrics by computing best guess
        values based on x and y coordinates.

        **Keyword arguments**:

        * *angleCalcMethod* (``integer``) -- set the method for calculating angle_dx. Default: 0

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        """

        x = self.mom6_grid['supergrid']['x']
        y = self.mom6_grid['supergrid']['y']

        # Compute edge lengths
        self.mom6_grid['supergrid']['dx'][:,:] = np.sqrt( (x[:,1:] - x[:,:-1])**2 + (y[:,1:] - y[:,:-1])**2 )
        self.mom6_grid['supergrid']['dy'][:,:] = np.sqrt( (x[1:,:] - x[:-1,:])**2 + (y[1:,:] - y[:-1,:])**2 )

        # Compute angles using centered differences in interior, and side differences on left/right edges
        # TODO: Why do something different at the edges when we have extra ROMS points available?
        self.mom6_grid['supergrid']['angle'][:,1:-1] = np.arctan2( (y[:,2:] - y[:,:-2]), (x[:,2:] - x[:,:-2]) )
        self.mom6_grid['supergrid']['angle'][:, 0  ] = np.arctan2( (y[:, 1] - y[:, 0 ]), (x[:, 1] - x[:, 0 ]) )
        self.mom6_grid['supergrid']['angle'][:,-1  ] = np.arctan2( (y[:,-1] - y[:,-2 ]), (x[:,-1] - x[:,-2 ]) )

        # Compute cell areas
        self.mom6_grid['supergrid']['area'][:,:] = self.mom6_grid['supergrid']['dx'][:-1, :] * \
            self.mom6_grid['supergrid']['dy'][:, :-1]

        return

    def _generate_mask(self, maskType, grd, **kwargs):
        '''Generate a land or ocean mask based on parameters provided.

        :param maskType: mask type requested ('land' or 'ocean')
        :type maskType: string
        :param grd: object
        :type grd: GridUtils() object
        :return: land or ocean mask
        :rtype: xarray

        Keyword arguments must have a valid depth variable in *topographyGrid* or
        *topographyVariables* and *depthVariable*.
        MOM6 parameters `MINIMUM_DEPTH`, `MASKING_DEPTH` and `MAXIMUM_DEPTH`
        may also be specified.

        **Keyword arguments**:

        * *epsilon* (``float``) -- Depth removed from masking depth to ensure new
          depth is deeper than the applied masking or minimum depth. Default: 1.0e-14
        * *MINIMUM_DEPTH* (``float``) --
          Minimum ocean depth. Default: 0.0
        * *MASKING_DEPTH* (``float``) --
          Ocean depths equal or shallower are set to land mask. Default: undefined
        * *MAXIMUM_DEPTH* (``float``) --
          Maximum depth of the ocean.  Defaults to maximum depth from data source
          if not specified or is negative. Default: undefined

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        '''

        # If the topographyVariables argument is not set, use [].
        utils.checkArgument(kwargs, 'topographyVariables', [])

        # Access depth field
        if len(kwargs['topographyVariables']) == 0:
            depthGrid = kwargs['topographyGrid']
        else:
            if kwargs['depthVariable'] in kwargs['topographyVariables']:
                depthGrid = kwargs['topographyGrid'][kwargs['depthVariable']]

        # Determine values from other possible arguments
        minimum_depth = 0.0
        masking_depth = -99999.0
        maximum_depth = -99999.0
        if 'MINIMUM_DEPTH' in kwargs.keys():
            minimum_depth = kwargs['MINIMUM_DEPTH']
        if 'MAXIMUM_DEPTH' in kwargs.keys():
            maximum_depth = kwargs['MAXIMUM_DEPTH']
        if 'MASKING_DEPTH' in kwargs.keys():
            masking_depth = kwargs['MASKING_DEPTH']

        # As is done in MOM6, if maximum is negative, it is defined by the maximum of
        # the 'depth' field passed.
        if maximum_depth < 0.0:
            maximum_depth = depthGrid.max().values.tolist()
            #msg = ("The (diagnosed) maximum depth of the ocean %f meters." % (maximum_depth))
            #grd.printMsg(msg, level=logging.INFO)

        # MINIMUM_DEPTH must be defined.  If MASKING_DEPTH is not defined, it is set to MINIMUM_DEPTH.
        if masking_depth < -99990.0:
            masking_depth = minimum_depth

        if maskType == 'land':
            return xr.where(depthGrid <= masking_depth, 1, 0)

        if maskType == 'ocean':
            return xr.where(depthGrid > masking_depth, 1, 0)

        msg = ("ERROR: Unknown mask type (%s) passed to mom6._generate_mask()")
        grd.printMsg(msg, logging.ERROR)
