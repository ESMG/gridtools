# Bathymetric tools
# Implementation of bathometric grid generators and other utilities
#  - https://github.com/nikizadehgfdl/ocean_model_topog_generator
#    - compute_bathymetric_roughness_h2(**opts)

import os, hashlib, logging
import numpy as np
import xarray as xr
import pdb

from . import meshrefinement

# Functions

def applyExistingLandmask(grd, dsData, dsVariable, maskFile, maskVariable, **kwargs):
    '''Modify a given bathymetry using a specified land mask.

    :param grd: class object
    :type grd: GridUtils
    :param dsData: data source data object
    :type dsData: xarray
    :param dsVariable: data source variable name
    :type dsVariable: string
    :param maskFile: filename
    :type maskFile: string
    :param maskVariable: variable name in maskFile
    :type maskVariable: string
    :param \**kwargs:
        See below

    **Keyword arguments**:

        * *epsilon* (``float``) -- When a point is declared an ocean point, if the
          depth is shallower than the masking depth, the depth is set to
          the minimum depth.  If the masking depth is undefined or equal to the
          minimum depth, the new depth is set deeper by epsilon to avoid becoming
          masked as land. Default: 1.0e-14
        * *MINIMUM_DEPTH* (``float``) --
          Minimum ocean depth. Default: 0.0
        * *MASKING_DEPTH* (``float``) --
          Ocean depths equal or shallower than the masking depth are masked as land.
          Default: undefined
        * *MAXIMUM_DEPTH* (``float``) --
          Maximum depth of the ocean.  Defaults to maximum depth from data source if
          not specified.
        * *TOPO_EDITS_FILE* (``string``) --
          Changed mask points in the MOM6 zEdits format will be
          recorded to the specified filename. (Unimplemented)

    .. note::
        For ocean points, if a depth is shallower than the MINIMUM_DEPTH
        but deeper than the MASKING_DEPTH, the depth will be set to
        the MINIMUM_DEPTH.

        Ocean points that are to become land will be set to the
        MASKING_DEPTH.  If MASKING_DEPTH is not defined, MINIMUM_DEPTH
        is used as the masking depth.
    '''

    if not(os.path.isfile(maskFile)):
        msg = ("ERROR: Existing mask file not found (%s)" % (maskFile))
        grd.printMsg(msg, level=logging.ERROR)
        return None

    # Find input land mask variable
    maskData = xr.open_dataset(maskFile)
    try:
        originalLandMask = maskData[maskVariable].copy()
    except:
        msg = ("ERROR: Mask file does not have requested variable (%s)" % (maskVariable))
        grd.printMsg(msg, level=logging.ERROR)
        return
    maskData.close()

    # Check for supplied depth variable
    try:
        depthGrid = dsData[dsVariable]
    except:
        msg = ("ERROR: The depth variable (%s) could not be found in the supplied data source." % (dsVariable))
        grd.printMsg(msg, level=logging.ERROR)
        return

    # Determine values from other possible arguments
    epsilon_depth = 1.0e-14
    minimum_depth = 0.0
    masking_depth = -99999.0
    maximum_depth = -99999.0
    if 'epsilon' in kwargs.keys():
        epsilon_depth = kwargs['epsilon']
    if 'MINIMUM_DEPTH' in kwargs.keys():
        minimum_depth = kwargs['MINIMUM_DEPTH']
    if 'MAXIMUM_DEPTH' in kwargs.keys():
        maximum_depth = kwargs['MAXIMUM_DEPTH']
    if 'MASKING_DEPTH' in kwargs.keys():
        masking_depth = kwargs['MASKING_DEPTH']

    # As is done in MOM6, if maximum is undefined, it is defined by the maximum of
    # the 'depth' grid passed to this function.
    if maximum_depth < -99990.0:
        maximum_depth = depthGrid.max().values.tolist()
        msg = ("The (diagnosed) maximum depth of the ocean is %f meters." % (maximum_depth))
        grd.printMsg(msg, level=logging.INFO)

    # MINIMUM_DEPTH < MASKING_DEPTH or if MASKING_DEPTH is undefined,
    # set MASKING_DEPTH to MINIMUM_DEPTH
    if minimum_depth < masking_depth:
        masking_depth = minimum_depth
    if masking_depth < -99990.0:
        masking_depth = minimum_depth

    # To use xr.where the data and mask have to be in the same Dataset()
    workData = xr.Dataset()
    workData['depth'] = depthGrid
    workData['land_mask'] = originalLandMask
    workData['land_mask'].attrs['masking_depth'] = masking_depth
    workData['land_mask'].attrs['minimum_depth'] = minimum_depth
    workData['land_mask'].attrs['maximum_depth'] = maximum_depth

    msg = ("Beginning application of new land mask (changes noted, if any).")
    grd.printMsg(msg, level=logging.INFO)

    # 1. Test points that should be makred as land.  If they are deeper
    #    than the masking depth, set them to the masking depth.  If
    #    the masking depth is not defined, use the minimum depth.

    # MOM6 RULE: A depth equal or shallower than MASKING_DEPTH is masked as land.
    condExp = (workData['land_mask'] == 1) & (workData['depth'] > masking_depth)
    # This returns the number of matching points
    nPts = condExp.data.ravel().sum()
    if nPts > 0:
        msg = (" * Number of land mask points with new depth of %f: %d" % (masking_depth, nPts))
        grd.printMsg(msg, level=logging.INFO)
    workData['newDepth'] = xr.where(condExp, masking_depth, workData['depth'])

    # 2. Test points that should be marked as ocean.  If they are shallower than
    #    the masking depth, then set them to the minimum depth.  If
    #    masking depth is undefined, set them to the minimum depth + epsilon.

    condExp = (workData['land_mask'] == 0) & (workData['newDepth'] < masking_depth)
    nPts = condExp.data.ravel().sum()
    if nPts > 0:
        if masking_depth == minimum_depth:
            msg = (" * Number of ocean points with new depth of %f: %d" % (minimum_depth + epsilon_depth, nPts))
            workData['newDepth'] = xr.where(condExp, minumum_depth + epsilon_depth, workData['newDepth'])
        else:
            msg = (" * Number of ocean points with new depth of %f: %d" % (minimum_depth, nPts))
            workData['newDepth'] = xr.where(condExp, minimum_depth, workData['newDepth'])
        grd.printMsg(msg, level=logging.INFO)

    # 3. If masking depth is defined, check ocean points that might violate minimum depth.
    if masking_depth < minimum_depth:
        condExp = (workData['land_mask'] == 0) & (workData['newDepth'] < minimum_depth)
        nPts = condExp.data.ravel().sum()
        if nPts > 0:
            msg = (" * Number of ocean points set to minimum depth: %d" % (nPts))
            workData['newDepth'] = xr.where(condExp, minimum_depth, workData['newDepth'])
            grd.printMsg(msg, level=logging.INFO)

    # Update hash for the new grid
    workData['newDepth'].attrs['sha256'] = hashlib.sha256( np.array( workData['newDepth'] ) ).hexdigest()

    return workData['newDepth']

def applyExistingOceanmask(grd, dsData, dsVariable, maskFile, maskVariable, **kwargs):
    '''Modify a given bathymetry using a specified ocean mask.

    :param grd: class object
    :type grd: GridUtils
    :param dsData: data source data object
    :type dsData: xarray
    :param dsVariable: data source variable name
    :type dsVariable: string
    :param maskFile: filename
    :type maskFile: string
    :param maskVariable: variable name in maskFile
    :type maskVariable: string
    :param \**kwargs:
        See below

    **Keyword arguments**:

        * *epsilon* (``float``) -- When a point is declared an ocean point, if the
          depth is shallower than the masking depth, the depth is set to
          the minimum depth.  If the masking depth is undefined or equal to the
          minimum depth, the new depth is set deeper by epsilon to avoid becoming
          masked as land. Default: 1.0e-14
        * *MINIMUM_DEPTH* (``float``) --
          Minimum ocean depth. Default: 0.0
        * *MASKING_DEPTH* (``float``) --
          Ocean depths equal or shallower than the masking depth are masked as land.
          Default: undefined
        * *MAXIMUM_DEPTH* (``float``) --
          Maximum depth of the ocean.  Defaults to maximum depth from data source if
          not specified.
        * *TOPO_EDITS_FILE* (``string``) --
          Changed mask points in the MOM6 zEdits format will be
          recorded to the specified filename. (Unimplemented)

    .. note::
        For ocean points, if a depth is shallower than the MINIMUM_DEPTH
        but deeper than the MASKING_DEPTH, the depth will be set to
        the MINIMUM_DEPTH.

        Ocean points that are to become land will be set to the
        MASKING_DEPTH.  If MASKING_DEPTH is not defined, MINIMUM_DEPTH
        is used as the masking depth.
    '''

    if not(os.path.isfile(maskFile)):
        msg = ("ERROR: Existing mask file not found (%s)" % (maskFile))
        grd.printMsg(msg, level=logging.ERROR)
        return None

    # Find input land mask variable
    maskData = xr.open_dataset(maskFile)
    try:
        originalOceanMask = maskData[maskVariable].copy()
    except:
        msg = ("ERROR: Mask file does not have requested variable (%s)" % (maskVariable))
        grd.printMsg(msg, level=logging.ERROR)
        return
    maskData.close()

    # Check for supplied depth variable
    try:
        depthGrid = dsData[dsVariable]
    except:
        msg = ("ERROR: The depth variable (%s) could not be found in the supplied data source." % (dsVariable))
        grd.printMsg(msg, level=logging.ERROR)
        return

    # Determine values from other possible arguments
    epsilon_depth = 1.0e-14
    minimum_depth = 0.0
    masking_depth = -99999.0
    maximum_depth = -99999.0
    if 'epsilon' in kwargs.keys():
        epsilon_depth = kwargs['epsilon']
    if 'MINIMUM_DEPTH' in kwargs.keys():
        minimum_depth = kwargs['MINIMUM_DEPTH']
    if 'MAXIMUM_DEPTH' in kwargs.keys():
        maximum_depth = kwargs['MAXIMUM_DEPTH']
    if 'MASKING_DEPTH' in kwargs.keys():
        masking_depth = kwargs['MASKING_DEPTH']

    # As is done in MOM6, if maximum is undefined, it is defined by the maximum of
    # the 'depth' grid passed to this function.
    if maximum_depth < -99990.0:
        maximum_depth = depthGrid.max().values.tolist()
        msg = ("The (diagnosed) maximum depth of the ocean is %f meters." % (maximum_depth))
        grd.printMsg(msg, level=logging.INFO)

    # MINIMUM_DEPTH < MASKING_DEPTH or if MASKING_DEPTH is undefined,
    # set MASKING_DEPTH to MINIMUM_DEPTH
    if minimum_depth < masking_depth:
        masking_depth = minimum_depth
    if masking_depth < -99990.0:
        masking_depth = minimum_depth

    # To use xr.where the data and mask have to be in the same Dataset()
    workData = xr.Dataset()
    workData['depth'] = depthGrid
    workData['ocean_mask'] = originalOceanMask
    workData['ocean_mask'].attrs['masking_depth'] = masking_depth
    workData['ocean_mask'].attrs['minimum_depth'] = minimum_depth
    workData['ocean_mask'].attrs['maximum_depth'] = maximum_depth

    msg = ("Beginning application of new ocean mask (changes noted, if any).")
    grd.printMsg(msg, level=logging.INFO)

    # With the given ocean mask, we now test points that need to change
    # based on given depths and given parameters.

    # 1. Test points that should be marked as land.  If they are deeper
    #    than the masking depth, set them to the masking depth.  If
    #    masking depth is undefined, use minimum depth.

    # MOM6 RULES: A depth equal or shallower than MASKING_DEPTH is masked as land.
    #             If MASKING_DEPTH is undefined, use MINIMUM_DEPTH for MASKING_DEPTH.
    condExp = (workData['ocean_mask'] == 0) & (workData['depth'] > masking_depth)
    # This returns the number of matching points
    nPts = condExp.data.ravel().sum()
    if nPts > 0:
        msg = (" * Number of land mask points with new depth of %f: %d" % (masking_depth, nPts))
        grd.printMsg(msg, level=logging.INFO)

    workData['newDepth'] = xr.where(condExp, masking_depth, workData['depth'])

    # 2. Test points that should be marked as ocean.  If they are shallower than
    #    the masking depth, then set them to the minimum depth.  If
    #    masking depth is undefined, set them to the minimum depth + epsilon.

    condExp = (workData['ocean_mask'] == 1) & (workData['newDepth'] < masking_depth)
    nPts = condExp.data.ravel().sum()
    if nPts > 0:
        if masking_depth == minimum_depth:
            msg = (" * Number of ocean points with new depth of %f: %d" % (minimum_depth + epsilon_depth, nPts))
            workData['newDepth'] = xr.where(condExp, minimum_depth + epsilon_depth, workData['newDepth'])
        else:
            msg = (" * Number of ocean points with new depth of %f: %d" % (minimum_depth, nPts))
            workData['newDepth'] = xr.where(condExp, minimum_depth, workData['newDepth'])
        grd.printMsg(msg, level=logging.INFO)

    # 3. If masking depth is defined, check ocean points that might violate minimum depth.
    if masking_depth < minimum_depth:
        condExp = (workData['ocean_mask'] == 1) & (workData['newDepth'] < minimum_depth)
        nPts = condExp.data.ravel().sum()
        if nPts > 0:
            msg = (" * Number of ocean points set to minimum depth: %d" % (nPts))
            workData['newDepth'] = xr.where(condExp, minimum_depth, workData['newDepth'])
            grd.printMsg(msg, level=logging.INFO)

    # Update hash for the new grid
    workData['newDepth'].attrs['sha256'] = hashlib.sha256( np.array( workData['newDepth'] ) ).hexdigest()

    return workData['newDepth']

def ice9(grd, **kwargs):
    '''
    This is a implementation of the ice-9 algorithm for filling in disconnected ocean
    bodies (lakes) for a given ocean grid.  Be sure to specify anticipated
    MINIMUM_DEPTH, MASKING_DEPTH and MAXIMUM_DEPTH that will be used for the
    model run.

    :param grd: class object
    :type grd: GridUtils
    :param \**kwargs:
        See below

    **Keyword arguments**:

        * *ocean_seeds* (``[(int, int)]``) --
          Provide ice-9 algorithm with one or more (j,i) ocean body grid points to designate
          as areas that should be treated as areas of continuous ocean points.  
          If more than one seed is given, all the discovered wet points will be
          merged together to form the final grid minus any detached ocean points (lakes).
          NOTE: Only the first seed is used! Future releases will allow multiple seeds.
        * *depth* (``grid``) --
          The depth grid to use for ice-9 algorithm.  This should be the same size as
          the provided latitude and logitude points defining the grid.  Values are
          positive for depth (water) and negative for height (land).
        * *periodic* (``boolean``) --
          Tells the algorithm that the grid is periodic and should
          check wrap points.  Default: False
          NOTE: Not implemented!
        * *returnFields* (``list``) --
          List of fields to be returned in the grd object.  Default: ['wetMask']
        * *MINIMUM_DEPTH* (``float``) -- minimum depth of ocean in meters. Default: 0.0
        * *MASKING_DEPTH* (``float``) -- masking depth of ocean in meters. Default: 0.0
        * *MAXIMUM_DEPTH* (``float``) -- maximum depth of ocean in meters. Default: -99999.0
        * *zEdits* (``boolean``) --
          Utilize zEdits for the provided depth field.  Store any updates to the depth field
          in zEdits as well.  Default: False
          NOTE: Not implemented!

    The ice-9 algorithm was first mentioned in a program written by Niki Zadeh in the
    `ocean_model_topog_generator` repository.  :cite:p:`Zadeh_2020_ocean_model_topog_generator`

    Another reference to the ice-9 algorithm is metioned in the
    repository `regrid_runoff` by  Alistair Adcroft.  :cite:p:`Adcroft_2020_regrid_runoff`.
    '''

    # Run through each ocean_seed provided
    # TODO: This only runs through the first seed
    for oceanSeed in kwargs['ocean_seeds']:
        depth = kwargs['depth']
        (nj, ni) = depth.shape
        wetMask = xr.DataArray(data = np.zeros((nj, ni)), dims = ("ny", "nx"))
        stack = set()
        stack.add( oceanSeed )
        while stack:
            (j,i) = stack.pop()
            # If we are already marked wet or see a land point
            # skip to the next point.
            if wetMask[j,i] or depth[j,i] <= kwargs['MASKING_DEPTH']: continue
            wetMask[j,i] = 1

            # Check surrounding points
            # For periodic boundaries, check wrap points
            if i>0: stack.add( (j,i-1) )
            #else: stack.add( (j,ni-1) )
            if i<ni-1: stack.add( (j,i+1) )
            #else: stack.add( (j,0) )
            if j>0: stack.add( (j-1,i) )
            if j<nj-1: stack.add( (j+1,i) )
            #else: stack.add( (j,ni-1-i) )

        # Only run the first seed for now
        break

    return wetMask

# Original functions from create_topog_refinedSampling.py

def break_array_to_blocks(a, xb=4, yb=1, useOverlap=False, useSupergrid=False):
    a_win = []
    # TODO: xb==8 or other values are not completely supported
    if ((xb == 4 or xb == 8) and yb == 1):
        i1 = a.shape[1]//xb
        i2 = 2*i1
        i3 = 3*i1
        i4 = a.shape[1]

        j1 = a.shape[0]//yb

        # If we are using the overlap, add points in the
        # j-direction which we dispose of to get rid of the
        # zero bands.
        if useOverlap:
            a_win.append(a[0:j1,0:i1+1])
            a_win.append(a[0:j1,i1:i2+1])
            a_win.append(a[0:j1,i2:i3+1])
            a_win.append(a[0:j1,i3:i4])
        else:
            a_win.append(a[0:j1,0:i1])
            a_win.append(a[0:j1,i1:i2])
            a_win.append(a[0:j1,i2:i3])
            a_win.append(a[0:j1,i3:i4])

        return a_win
    else:
        raise Exception('This routine can only make 2x2 blocks!')
        ##Niki: Implement a better algo and lift this restriction

def undo_break_array_to_blocks(a, xb=4, yb=1, useOverlap=False, extendedGrid=False,
        useSupergrid=False, useQHGridShift=False):
    if (xb == 4 and yb == 1):
        if useOverlap:
            ao = np.append(a[0][:,:-1], a[1], axis=1)
            ao = np.append(ao[:,:-1]  , a[2], axis=1)
            ao = np.append(ao[:,:-1]  , a[3], axis=1)
            # If we are using the QHGridShift,
            # trim y+1,x and y,x+1, otherwise send
            # the grid back untrimmed.
            if useQHGridShift:
                ao = ao[:-1,:-1]
        else:
            ao = np.append(a[0], a[1], axis=1)
            ao = np.append(ao  , a[2], axis=1)
            ao = np.append(ao  , a[3], axis=1)
        return ao
    elif (xb == 8 and yb == 1):
        ao = np.append(a[0], a[1], axis=1)
        ao = np.append(ao  , a[2], axis=1)
        ao = np.append(ao  , a[3], axis=1)
        ao = np.append(ao  , a[4], axis=1)
        ao = np.append(ao  , a[5], axis=1)
        ao = np.append(ao  , a[6], axis=1)
        ao = np.append(ao  , a[7], axis=1)
        return ao
    else:
        raise Exception('This routine can only make 2x2 blocks!')
        ##TODO: Implement a better algorithm and lift this restriction

def get_indices1D_old(lon_grid, lat_grid, x, y):
    """This function returns the j,i indices for the grid point closest to the input lon,lat coordinates."""
    """It returns the j,i indices."""
    lons=np.fabs(lon_grid-x)
    lonm=np.where(lons==lons.min())
    lats=np.fabs(lat_grid-y)
    latm=np.where(lats==lats.min())
    j0=latm[0][0]
    i0=lonm[0][0]
#    print("wanted: ",x,y)
#    print("got:    ",lon_grid[i0] , lat_grid[j0])
#    print(j0,i0)
    return j0,i0

def mdist(x1, x2):
    """Returns positive distance modulo 360."""
    return np.minimum(np.mod(x1-x2,360.), np.mod(x2-x1,360.) )

def get_indices1D(lon_grid,lat_grid,x,y):
    """This function returns the j,i indices for the grid point closest to the input lon,lat coordinates."""
    """It returns the j,i indices."""
#    lons=np.fabs(lon_grid-x)
    lons=np.fabs(mdist(lon_grid,x))
    lonm=np.where(lons==lons.min())
    lats=np.fabs(lat_grid-y)
    latm=np.where(lats==lats.min())
    j0=latm[0][0]
    i0=lonm[0][0]
    print(" wanted: %f %f" % (x,y))
    print(" got:    %f %f" % (lon_grid[i0] , lat_grid[j0]))
    good = False
    if(abs(x-lon_grid[i0]) < abs(lon_grid[1]-lon_grid[0])):
        good = True
        print("  good")
    else:
        print("  bad")
    print(" j,i=",j0,i0)
    return j0,i0,good

def get_indices2D(lon_grid, lat_grid, x, y):
    """This function returns the j,i indices for the grid point closest to the input lon,lat coordinates."""
    """It returns the j,i indices."""
    lons=np.fabs(lon_grid-x)
    lonm=np.where(lons==lons.min())
    lats=np.fabs(lat_grid-y)
    latm=np.where(lats==lats.min())
    j0=latm[0][0]
    i0=lonm[1][0]
#    print("wanted: ",x,y)
#    print("got:    ",lon_grid[j0,i0] , lat_grid[j0,i0])
#    print(j0,i0)
    return j0,i0
#Gibraltar
#wanted:  32.0 -12.5
#got:     31.9958333333 -12.5041666667
#9299 25439
#Gibraltar
#wanted:  40.7 4.7
#got:     40.6958333333 4.69583333333
#11363 26483
#Black sea
#wanted:  44.0 36
#got:     43.9958333333 36.0041666667
#15120 26879

def refine_by_repeat(x, rf):
    xrf=np.repeat(np.repeat(x[:,:],rf,axis=0),rf,axis=1) #refine by repeating values
    return xrf

def extend_by_zeros(x, shape):
    ext=np.zeros(shape)
    ext[:x.shape[0],:x.shape[1]] = x
    return ext

# Copied with slight modifications
def do_block(grd, part, lon, lat, topo_lons, topo_lats, topo_elvs, max_mb=500):
    msg = ("Doing block number %d" % (part))
    grd.printMsg(msg, level=logging.INFO)
    msg = ("Target sub mesh shape: %s" % (str(lon.shape)))
    grd.printMsg(msg, level=logging.INFO)

    #target_mesh = GMesh.GMesh( lon=lon, lat=lat )
    #target_mesh = GMesh.GMesh(lon=lon, lat=lat)
    target_mesh = meshrefinement.MeshRefinement(lon=lon, lat=lat)
    #target_mesh.shape = lon.shape
    #target_mesh.ni = target_mesh.shape[0]
    #target_mesh.nj = target_mesh.shape[1]
    #print("  D:target_mesh.shape", target_mesh.shape)
    #pdb.set_trace()

    #plot()

    # Indices in topographic data
    ti,tj = target_mesh.find_nn_uniform_source(topo_lons, topo_lats)

    #Sample every other source points
    ##Niki: This is only for efficeincy and we want to remove the constraint for the final product.
    ##Niki: But in some cases it may not work!
    #tis,tjs = slice(ti.min(), ti.max()+1,2), slice(tj.min(), tj.max()+1,2)
    #tis,tjs = slice(ti.min(), ti.max()+1,1), slice(tj.min(), tj.max()+1,1)
    tis,tjs = slice(ti.min().data.tolist(), ti.max().data.tolist()+1,1),\
        slice(tj.min().data.tolist(), tj.max().data.tolist()+1,1)
    #print('  Slices j,i:', tjs, tis )
    msg = ('Topographic grid slice: %s %s' % (str(tjs), str(tis)))
    grd.printMsg(msg, level=logging.INFO)

    # Read elevation data
    topo_elv = topo_elvs[tjs,tis]
    # Extract appropriate coordinates
    topo_lon = topo_lons[tis]
    topo_lat = topo_lats[tjs]

    msg = ('Topo shape: %s' % (str(topo_elv.shape)))
    grd.printMsg(msg, level=logging.INFO)
    #print('  topography longitude range:', topo_lon.min(), topo_lon.max())
    #print('  topography latitude  range:', topo_lat.min(), topo_lat.max())
    msg = ('Topography longitude range: %f %f' % (topo_lon.min(), topo_lon.max()))
    grd.printMsg(msg, level=logging.INFO)
    msg = ('Topography latitude  range: %f %f' % (topo_lat.min(), topo_lat.max()))
    grd.printMsg(msg, level=logging.INFO)

    #print("  Target     longitude range:", lon.min(), lon.max())
    #print("  Target     latitude  range:", lat.min(), lat.max())
    msg = ("Target     longitude range: %f %f" % (lon.min(), lon.max()))
    grd.printMsg(msg, level=logging.INFO)
    msg = ("Target     latitude  range: %f %f" % (lat.min(), lat.max()))
    grd.printMsg(msg, level=logging.INFO)

    # Refine grid by 2 till all source points are hit
    msg = ("Refining the target to hit all source points ...")
    grd.printMsg(msg, level=logging.INFO)
    #pdb.set_trace()
    Glist = target_mesh.refine_loop(topo_lon, topo_lat, max_mb=max_mb);
    hits = Glist[-1].source_hits(topo_lon, topo_lat)
    msg = ("Non-hit ratio: %d%s%d" % (hits.size-hits.sum().astype(int)," / ",hits.size))
    grd.printMsg(msg, level=logging.INFO)

    # Sample the topography on the refined grid
    msg = ("Sampling the source points on target mesh ...")
    grd.printMsg(msg, level=logging.INFO)
    Glist[-1].sample_source_data_on_target_mesh(topo_lon, topo_lat, topo_elv)
    msg = ("Sampling finished ...")
    grd.printMsg(msg, level=logging.INFO)

    # Coarsen back to the original taget grid
    msg = ("Coarsening back to the original target grid ...")
    grd.printMsg(msg, level=logging.INFO)
    for i in reversed(range(1,len(Glist))):   # 1, makes it stop at element 1 rather than 0
        Glist[i].coarsenby2(Glist[i-1])

    #pdb.set_trace()

    msg = ("Roughness calculation via plane fit")
    grd.printMsg(msg, level=logging.INFO)
    #Roughness calculation by plane fitting
    #Calculate the slopes of the planes on the coarsest (model) grid cells
    G = Glist[0]
    denom = (G.xxm-G.xm*G.xm)*(G.yym-G.ym*G.ym)-(G.xym-G.xm*G.ym)*(G.xym-G.xm*G.ym)
    alphd = (G.xzm-G.xm*G.zm)*(G.yym-G.ym*G.ym)-(G.yzm-G.ym*G.zm)*(G.xym-G.xm*G.ym)
    betad = (G.yzm-G.ym*G.zm)*(G.xxm-G.xm*G.xm)-(G.xzm-G.xm*G.zm)*(G.xym-G.xm*G.ym)
    #alph = alphd/denom
    #beta = betad/denom

    rf = 2**(len(Glist)-1) #refinement factor
    #Generate the refined arrays from coarse arrays by repeating the coarse elements rf times
    #These arrays have the same values on finest mesh points inside each coarse cell by construction.
    #They are being used to calculate the (least-square) distance of data points
    #inside that cell from the fitted plane in that cell.
    xmrf = refine_by_repeat(G.xm, rf)
    ymrf = refine_by_repeat(G.ym, rf)
    zmrf = refine_by_repeat(G.zm, rf)
    alphdrf = refine_by_repeat(alphd, rf)
    betadrf = refine_by_repeat(betad, rf)
    denomrf = refine_by_repeat(denom, rf)
    #The refined mesh has a shape of (2*nj-1,2*ni-1) rather than (2*nj,2*ni) and hence
    #is missing the last row/column by construction!
    #So, the finest mesh does not have (rf*nj,rf*ni) points but is smaller by ...
    #Bring it to the same shape as (rf*nj,rf*ni) by padding with zeros.
    #This is for algorithm convenience and we remove the contribution of them later.
    xs = extend_by_zeros(Glist[-1].xm, zmrf.shape)
    ys = extend_by_zeros(Glist[-1].ym, zmrf.shape)
    zs = extend_by_zeros(Glist[-1].zm, zmrf.shape)
    #Calculate the vertical distance D of each source point from the least-square plane
    #Note that the least-square plane passes through the mean data point.
    #The last rf rows and columns are for padding and denom is not zero on them.
    #To avoid division by zero calculate denom*D instead
    D_times_denom = denomrf*(zs-zmrf) - alphdrf*(xs-xmrf) - betadrf*(ys-ymrf)
    #Calculate topography roughness as the standard deviation of D on each coarse (model) grid cell
    #This is why we wanted to have a (nj*rf,ni*rf) shape arrays and padded with zeros above.
    D_times_denom_coarse = np.reshape(D_times_denom,(G.xm.shape[0],rf,G.xm.shape[1],rf))
    D_times_denom_coarse_std = D_times_denom_coarse.std(axis=(1,3))
    D_std = np.zeros(G.zm.shape)
    epsilon = 1.0e-20 #To avoid negative underflow
    D_std[:,:] = D_times_denom_coarse_std[:,:]/(denom[:,:]+epsilon)
    # Don't forget to chop off the zeros added before
    #D_std = D_std[:-1,:-1]
    #pdb.set_trace()

    #print("")
    #print("Writing ...")
    #filename = 'topog_refsamp_BP.nc'+str(b)
    #write_topog(Glist[0].height,fnam=filename,no_changing_meta=True)
    #print("heights shape:", lons[b].shape,Hlist[b].shape)
    return Glist[0].height, D_std, Glist[0].h_min, Glist[0].h_max, hits

# Rebuilt from main() function
def computeBathymetricRoughness(grd, dsName, **kwargs):
    '''This generates h2 and other variables and returns an xarray DataSet.

    :param grd: class object
    :type grd: GridUtils
    :param dsName: data source name
    :type dsName: string
    :param \**kwargs:
        See below

    **Keyword arguments**:

        * *maxMb* (``int``) --
          Memory limit for grid refinements. Default: 8000.0
        * *h2Name* (``string``) --
          The computed bathymetric roughness grid name. Default: h2
        * *depthName* (``string``) --
          The bathymetry grid name to use from data source. Default: depth
        * *gridPoint* (``string``) --
          Grid placement of bathymetric roughness values. See below. Default: h
        * *auxVariables* (``list``) --
          Specify additional variables to include with bathymetric roughness. See below. Default: []
        * *superGrid* (``boolean``) --
          If ``True``, the bathymetric roughness grid returned is a supergrid.
          Otherwise, the ocean roughness is the same size as the current grid. Default: False
        * *useClipping* (``boolean``) --
          Use ``True`` if the current grid is periodic and should be
          clipped prior to computing the bathymetric roughness. Defualt: False
        * *useFixByOverlapQHGridShift* (``boolean``) --
          When using a regular grid, use overlapping grid technique to fill in partition boundaries.
          See IMPLEMENTATION NOTES below. Default: False [DEPRICATED]
        * *useQHGridShift* (``boolean``) --
          For a regular grid, use the Q point values as the H values to fill missing points.
          Default: False
        * *useOverlap* (``boolean``) --
          Use overlapping grid technique to fill in partition boundaries.  The outer column and
          row will still be missing.
        * *extendedGrid* (``boolean``) --
          If True, the grid provided by this routine has been extended and should use the overlap
          technique on h-points only and not q-points which are then shifted back to h-points.
          See IMPLEMENTATION NOTES below. Default: False

    This routine is based on a paper by Adcroft :cite:p:`Adcroft_2013` and python code from
    `OMtopogen/create_topog_refinedSampling.py` :cite:p:`Zadeh_2020_ocean_model_topog_generator`.

    .. note::

      :maxMB:
          The memory limit for successive grid refinements.  This should be maximized for the
          memory footprint of the compute node.  If the program crashes, use lower amounts of
          memory.

      :auxVariables:
          h_std, h_min, h_max, and height variables. Ask for one or more
          additional variables by python list [] to auxVariables.
          Default is an empty list: []

      :gridPoint:
          By default, this generates bathymetric roughness grids on Arakawa C h-points
          but may be specified via gridPoint.

          For gridPoint, a diagram of a grid cells is::

              q-----v-----q
              |           |
              u     h     u
              |           |
              q-----v-----q

          Valid values for gridPoint are:
              * 'h' h-point; grid center
              * 'q' q-point; grid corners
              * 'uv' u- and v-point; grid faces

      :superGrid:
          If you want all supergrid points, set superGrid=True.  Setting
          tells this routine to use the supergrid when calculating
          the bathymetric roughness.  This will require more RAM. Default: False

    IMPLEMENTATION NOTES:
      * If a supergrid is used, four zero bands along longitude are returned
        representing the four grid partitions.  This needs to be fixed
        in the future.
      * **useQHGridShift** by default is False.  Roughness (h2) is
        diagnosed on the q-points and shifted by 1/2 a grid cell back to the
        h-points.  Accuracy of the roughness and other resultant variables are
        off by a 1/2 grid cell.  This only works for the regular grid, not the
        supergrid (superGrid=False).
      * **extendedGrid**: If the grid is extended, setting **extendedGrid** to True,
        tells this routine to attempt to diagnose h2 on the h-points without
        shifting the grid.  The extended grid should be extended by two grid
        points when working with the supergrid.  Use of the **extendedGrid**
        option is recommended for best results.
      * Support for 'q' and 'uv' grid points are not supported.
      * If the program is running out of memory, reduce the maxMb value.
        This reduces the available memory footprint available to
        this routine.  This will also reduce the number of available
        refinements against the bathymetry data source.
    '''
    # Provide defaults if a kwarg is not set
    if not('depthName' in kwargs.keys()):
        kwargs['depthName'] = 'depth'
    depthName = kwargs['depthName']

    if not('superGrid' in kwargs.keys()):
        kwargs['superGrid'] = False
    useSupergrid = kwargs['superGrid']

    if not('useClipping' in kwargs.keys()):
        kwargs['useClipping'] = False

    if not('h2Name' in kwargs.keys()):
        kwargs['h2Name'] = 'h2'

    if not('maxMb' in kwargs.keys()):
        kwargs['maxMb'] = 8000
    max_mb = kwargs['maxMb']

    if not('useOverlap' in kwargs.keys()):
        kwargs['useOverlap'] = False
    useOverlap = kwargs['useOverlap']

    if not('useQHGridShift' in kwargs.keys()):
        kwargs['useQHGridShift'] = False
    useQHGridShift = kwargs['useQHGridShift']

    if not('extendedGrid' in kwargs.keys()):
        kwargs['extendedGrid'] = False
    extendedGrid = kwargs['extendedGrid']

    # useFixByOverlapQHGridShift = True implies superGrid = False
    # this method uses q-points and shifts back to h-points.
    #useOverlap = False
    #if not('useFixByOverlapQHGridShift' in kwargs.keys()):
    #    kwargs['useFixByOverlapQHGridShift'] = True
    #    if useSupergrid:
    #        grd.printMsg("ERROR: Use of the superGrid is not permitted when useFixByOverlapQHGridShift is True.",\
    #            level=logging.ERROR)
    #if kwargs['useFixByOverlapQHGridShift']:
    #    useOverlap = True

    # extendedGrid
    # This tells the FixByOverlap routine to use the h-points instead
    # of q-points but still use the overlap method to produce a full
    # set of h-points for roughness.  The grid passed should have been
    # extended to overcome the problem of this routine at the edges.
    #extendedGrid = False
    #if not('extendedGrid' in kwargs.keys()):
    #    kwargs['extendedGrid'] = False
    #else:
    #    if kwargs['extendedGrid']:
    #        extendedGrid = kwargs['extendedGrid']
    #        useOverlap = True

    #if not(useSupergrid):
    #    useOverlap = True

    # Unimplemented or not fully implemented kwargs
    if not('open_channels' in kwargs.keys()):
        kwargs['open_channels'] = False

    if not('gridPoint' in kwargs.keys()):
        kwargs['gridPoint'] = 'h'

    # Attempt to open the selected dataset
    bathyData = grd.openDataset(dsName)
    if not(bathyData):
        grd.printMsg("ERROR: The datasource (%s) did not return a usable variable." %\
                (dsName), level=logging.ERROR)
        return None

    # Variables to use
    variablesToUse = ['lat', 'lon', depthName]

    if not(grd.checkAvailableVariables(bathyData, variablesToUse)):
        grd.printMsg("ERROR: The datasource (%s) did not have required variables: %s" %\
                (dsName, variablesToUse), level=logging.ERROR)
        return None

    # Collect data source data
    # topo_ name is unfortunate, input data source could be bathymetric with depths
    topo_lons = bathyData['lon']
    topo_lats = bathyData['lat']
    topo_elvs = bathyData[depthName]

    # Fix the topography to open some channels
    # Not fully integrated
    if(kwargs['open_channels']):
        #Bosporus mouth at Marmara Sea (29.03,41.04)
        j0,i0=15724,39483 #get_indices1D(topo_lons, topo_lats ,29.03, 41.04)
        #One grid cell thick (not survived ice9)
        #topo_elvs[j0,i0]=topo_elvs[j0,i0-1]
        #topo_elvs[j0+1,i0+2]=topo_elvs[j0+1,i0+1]
        #topo_elvs[j0+3,i0+3]=topo_elvs[j0+3,i0+2]
        #wide channel
        j2,i2=15756, 39492 #get_indices1D(topo_lons, topo_lats ,29.1, 41.3)
        topo_elvs[j0-10:j2,i0-10:i2+10]=topo_elvs[j0,i0-1]

        #Dardanells' constrict
        j1,i1=15616, 39166 #get_indices1D(topo_lons, topo_lats ,26.39, 40.14)
        topo_elvs[j1+1,i1]=topo_elvs[j1,i1]

    # Set the target grid
    target_grid = grd.grid
    target_lon = grd.grid['x']
    target_lat = grd.grid['y']
    grid_lon = target_grid['x']
    grid_lat = target_grid['y']

    # Optionally, subset to just the grid instead of the supergrid
    if not(kwargs['superGrid']):
        # Subset to MOM6 regular grid
        msg = ("Using regular grid instead of the supergrid.")
        grd.printMsg(msg, level=logging.INFO)
        grid_lon = target_grid['x'][1::2,1::2]
        grid_lat = target_grid['y'][1::2,1::2]
        target_lon = target_grid['x'][1::2,1::2]
        target_lat = target_grid['y'][1::2,1::2]
        if kwargs['useQHGridShift']:
            # We use the q-points of the supergrid to provide an extra column
            # to fill the grid without extending the grid.  This introduces an
            # error of 1/2 grid point in the data.
            target_lon = target_grid['x'][::2,::2]
            target_lat = target_grid['y'][::2,::2]
            msg = ("Using diagnosed q-points for h-points on regular grid.")
            grd.printMsg(msg, level=logging.INFO)

    if kwargs['useOverlap']:
        # This uses the grid overlap technique.
        msg = ("Using grid overlap technique.")
        grd.printMsg(msg, level=logging.INFO)

    # x and y have shape (nyp,nxp). Topog does not need the last col for global grids (period in x).
    # Useful for GLOBAL GRIDS!
    if kwargs['useClipping']:
        target_lon = target_lon[:,:-1]
        target_lat = target_lat[:,:-1]

    msg = ("Target mesh shape: %s" % (str(target_lon.shape)))
    grd.printMsg(msg, level=logging.INFO)

    # Not fully understood
    #   Allows interpolation to work on the grid center say if grid center is near 0 latitude (prime
    #   meridian) or 180 latitude (dateline)
    # Translate topo data to start at target_mesh.lon_m[0]
    # Why/When? TODO: Investigate get_indices1D() function
    jllc, illc, status1 = get_indices1D(topo_lons, topo_lats ,target_lon[0,0] ,target_lat[0,0])
    jurc, iurc, status2 = get_indices1D(topo_lons, topo_lats ,target_lon[0,-1],target_lat[-1,0])
    if(not status1 or not status2):
        msg = ('Shifting topo data to start at target lon.')
        grd.printMsg(msg, level=logging.INFO)
        topo_lons = np.roll(topo_lons,-illc,axis=0) #Roll data longitude to right
        topo_lons = np.where(topo_lons>=topo_lons[0] , topo_lons-360, topo_lons) #Rename (0,60) as (-300,-180)
        topo_elvs = np.roll(topo_elvs,-illc,axis=1) #Roll data depth to the right by the same amount.

    # TODO: This section needs to be reworked
    msg = ('Topography grid array shapes: lon:%s lat:%s' % (str(topo_lons.shape),str(topo_lats.shape)))
    grd.printMsg(msg, level=logging.INFO)
    msg = ('Topography longitude range: %f %f' % (topo_lons.min(),topo_lons.max()))
    grd.printMsg(msg, level=logging.INFO)
    msg = ('Topography longitude range: %f %f' % (topo_lons[0],topo_lons[-1000]))
    grd.printMsg(msg, level=logging.INFO)
    msg = ('Topography latitude range:  %f %f' % (topo_lats.min(),topo_lats.max()))
    grd.printMsg(msg, level=logging.INFO)
    #print(' Is mesh uniform?', GMesh.is_mesh_uniform( topo_lons, topo_lats ) )
    #print(' Is mesh uniform?', GMesh.is_mesh_uniform( topo_lons, topo_lats ).data.tolist() )
    msg = ('Is mesh uniform?', meshrefinement.is_mesh_uniform( topo_lons, topo_lats ).data.tolist() )
    ### Partition the Target grid into non-intersecting blocks
    #This works only if the target mesh is "regular"! Niki: Find the mathematical buzzword for "regular"!!
    #Is this a regular mesh?
    # if( .NOT. is_mesh_regular() ) throw
    msg = ('RAM allocation to refinements (Mb): %f' % (max_mb))
    grd.printMsg(msg, level=logging.INFO)
    msg = ("Flag useSuperGrid   : %s" % (useSupergrid))
    grd.printMsg(msg, level=logging.INFO)
    msg = ("Flag useOverlap     : %s" % (useOverlap))
    grd.printMsg(msg, level=logging.INFO)
    msg = ("Flag useQHGridShift : %s" % (useQHGridShift))
    grd.printMsg(msg, level=logging.INFO)
    msg = ("Flag extendedGrid   : %s" % (extendedGrid))
    grd.printMsg(msg, level=logging.INFO)

    # Rework partitioning (dask opportunity)
    # Niki: Why 4,1 partition?
    xb = 4
    yb = 1
    lons = break_array_to_blocks(target_lon, xb, yb, useOverlap=useOverlap, useSupergrid=useSupergrid)
    lats = break_array_to_blocks(target_lat, xb, yb, useOverlap=useOverlap, useSupergrid=useSupergrid)

    # We must loop over the 4 partitions
    # TODO: The number of points being collected and the number of hits algorithm does not
    # compute things correctly due to issues with different bounding boxes.  This issue
    # should be addressed with previous section.
    Hlist=[]
    Hstdlist=[]
    Hminlist=[]
    Hmaxlist=[]
    for part in range(0,xb):
        lon = lons[part]
        lat = lats[part]
        h, hstd, hmin, hmax, hits = do_block(grd, part, lon, lat, topo_lons, topo_lats, topo_elvs, max_mb=max_mb)
        Hlist.append(h)
        Hstdlist.append(hstd)
        Hminlist.append(hmin)
        Hmaxlist.append(hmax)

    msg = ("Merging the blocks ...")
    grd.printMsg(msg, level=logging.INFO)
    height_refsamp = undo_break_array_to_blocks(Hlist, xb, yb, useOverlap=useOverlap,
            extendedGrid=extendedGrid, useSupergrid=useSupergrid, useQHGridShift=useQHGridShift)
    hstd_refsamp = undo_break_array_to_blocks(Hstdlist, xb, yb, useOverlap=useOverlap,
            extendedGrid=extendedGrid, useSupergrid=useSupergrid, useQHGridShift=useQHGridShift)
    hmin_refsamp = undo_break_array_to_blocks(Hminlist, xb, yb, useOverlap=useOverlap,
            extendedGrid=extendedGrid, useSupergrid=useSupergrid, useQHGridShift=useQHGridShift)
    hmax_refsamp = undo_break_array_to_blocks(Hmaxlist, xb, yb, useOverlap=useOverlap,
            extendedGrid=extendedGrid, useSupergrid=useSupergrid, useQHGridShift=useQHGridShift)

    #Niki: Why isn't h periodic in x?  I.e., height_refsamp[:,0] != height_refsamp[:,-1]
    # ANS?: The overlapping grid row was clipped?
    # TODO: check periodic grids without clipping
    # TODO: no need to display these messages if the grid is not periodic
    msg = ("Periodicity test  : %f %f" % (height_refsamp[0,0], height_refsamp[0,-1]))
    grd.printMsg(msg, level=logging.INFO)
    msg = ("Periodicity break : %f" % ((np.abs(height_refsamp[:,0] - height_refsamp[:,-1])).max()))
    grd.printMsg(msg, level=logging.INFO)

    # For non-supergrids, we use the h-point lon lats for
    # both for the shifted and the unshifted versions of
    # the grid.
    if not(kwargs['superGrid']):
        # Subset to MOM6 regular grid
        target_lon = target_grid['x'][1::2,1::2]
        target_lat = target_grid['y'][1::2,1::2]

    #breakpoint()
    # Assemble grids
    bathymetricRoughness = xr.Dataset()

    h2Name = kwargs['h2Name']
    bathymetricRoughness[h2Name] = (('ny','nx'), hstd_refsamp * hstd_refsamp)
    bathymetricRoughness[h2Name].attrs['units'] = 'meters^2'
    bathymetricRoughness[h2Name].attrs['standard_name'] =\
            'Subgrid scale topography height variance at Arakawa C %s-points' % (kwargs['gridPoint'])
    bathymetricRoughness[h2Name].attrs['sha256'] = hashlib.sha256( np.array( hstd_refsamp * hstd_refsamp ) ).hexdigest()

    if 'hStd' in kwargs['auxVariables']:
        bathymetricRoughness['hStd'] = (('ny','nx'), hstd_refsamp)
        bathymetricRoughness['hStd'].attrs['units'] = 'meters'
        bathymetricRoughness['hStd'].attrs['standard_name'] =\
                'Subgrid scale topography height standard deviation at Arakawa C %s-points' % (kwargs['gridPoint'])
        bathymetricRoughness['hStd'].attrs['sha256'] = hashlib.sha256( np.array( hstd_refsamp ) ).hexdigest()

    if 'hMin' in kwargs['auxVariables']:
        bathymetricRoughness['hMin'] = (('ny','nx'), hmin_refsamp)
        bathymetricRoughness['hMin'].attrs['units'] = 'meters'
        bathymetricRoughness['hMin'].attrs['standard_name'] =\
                'Subgrid scale topography height standard deviation minimum at Arakawa C %s-points' % (kwargs['gridPoint'])
        bathymetricRoughness['hMin'].attrs['sha256'] = hashlib.sha256( np.array( hmin_refsamp ) ).hexdigest()

    if 'hMax' in kwargs['auxVariables']:
        bathymetricRoughness['hMax'] = (('ny','nx'), hmax_refsamp)
        bathymetricRoughness['hMax'].attrs['units'] = 'meters'
        bathymetricRoughness['hMax'].attrs['standard_name'] =\
                'Subgrid scale topography height standard deviation maximum at Arakawa C %s-points' % (kwargs['gridPoint'])
        bathymetricRoughness['hMax'].attrs['sha256'] = hashlib.sha256( np.array( hmax_refsamp ) ).hexdigest()

    if 'depth' in kwargs['auxVariables']:
        # Do not invert the value here, it is done later!
        bathymetricRoughness['depth'] = (('ny','nx'), height_refsamp)
        bathymetricRoughness['depth'].attrs['units'] = 'meters'
        bathymetricRoughness['depth'].attrs['standard_name'] = 'topographic depth at Arakawa C %s-points' % (kwargs['gridPoint'])
        bathymetricRoughness['depth'].attrs['sha256'] = hashlib.sha256( np.array( height_refsamp ) ).hexdigest()

    try:
        # xarray=0.19.0 requires unpacking of Dataset variables by using .data
        bathymetricRoughness['x'] = (('ny','nx'), grid_lon.data)
        bathymetricRoughness['x'].attrs['units'] = 'degrees_east'
        bathymetricRoughness['x'].attrs['standard_name'] = 'longitude'
        bathymetricRoughness['x'].attrs['sha256'] = hashlib.sha256( np.array( grid_lon ) ).hexdigest()

        # xarray=0.19.0 requires unpacking of Dataset variables by using .data
        bathymetricRoughness['y'] = (('ny','nx'), grid_lat.data)
        bathymetricRoughness['y'].attrs['units'] = 'degrees_north'
        bathymetricRoughness['y'].attrs['standard_name'] = 'latitude'
        bathymetricRoughness['y'].attrs['sha256'] = hashlib.sha256( np.array( grid_lat ) ).hexdigest()
    except:
        #print('hstd:',hstd_refsamp.shape)
        #print('grid_lon:',grid_lon.shape)
        #breakpoint()
        raise

    # Add metadata to dataset


    # Return finished dataset
    return bathymetricRoughness
