'''
Generic class and utility functions for handling
ROMS grids.
'''

import warnings

class ROMS:

    def __init__(self):
        self._grid_type = "ROMS"
        self.roms_grid = dict()

    def read_ROMS_grid(self, grd):
        '''Load the ROMS grid previous read by GridUtils().

        This function is based on code from :cite:p:`Ilicak_2020_ROMS_to_MOM6`.
        '''

        subgrids = ['psi', 'rho', 'u', 'v'] # also available: 'vert'
        fields = ['lon', 'lat', 'x', 'y', 'mask']

        # Extract fields named based on which grid they are on
        for subgrid in subgrids:
            roms_grid[subgrid] = dict()
            for field in fields:
                var_name = field + '_' + subgrid
                roms_grid[subgrid][field] = roms_ds.variables[var_name][:]
                if (field == 'x') or (field == 'y'):
                     units = roms_ds.variables[var_name].units.lower()
                     assert units.startswith('meter')
                elif (field == 'lat') or (field == 'lon'):
                     units = roms_ds.variables[var_name].units.lower()
                     assert units.startswith('degree')

        # Extract fields that do not follow the naming pattern
        roms_grid['rho']['h'] = roms_ds.variables['h'][:] # on the rho grid, but not called "h_rho"

        roms_grid['metadata'] = dict()

        spherical = roms_ds.variables['spherical'][:]
        if (spherical == 0) or (spherical == b'F') or (spherical == b'f'):
             roms_grid['metadata']['is_spherical'] = False
        elif (spherical == 1) or (spherical == b'T') or (spherical == b't'):
             roms_grid['metadata']['is_spherical'] = True
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
