# Generic mesh or field manipulation routines

import xarray as xr
from . import utils

def writeLandmask(grd, dsData, dsVariable, outVariable, outFile, **kwargs):
    '''Write a land mask based on provided information.  This routine
    assumes a depth field is being passed as an argument to create the
    mask.

    MOM6 h-points are masked at and above the MASKING_DEPTH.  A depth
    equal to the MASKING_DEPTH is masked as land.  MASKING_DEPTH is
    ignored if negative.  The default depth is zero (0.0).'''
    
    masking_depth = 0.0
    if 'MASKING_DEPTH' in kwargs.keys():
        masking_depth = kwargs['MASKING_DEPTH']
        if masking_depth < 0:
            masking_depth = 0.0

    dsDataset = xr.Dataset()
    dsDataset[outVariable] = xr.where(dsData[dsVariable] <= masking_depth, 1.0, 0.0)
    dsDataset[outVariable].attrs['sha256'] = utils.sha256sum(dsDataset[outVariable])
    # Try to copy coordinates from the supplied variable otherwise, try
    # the supplied grid.
    copyCoords = ['x', 'y']
    for varCoord in copyCoords:
        if hasattr(dsData, varCoord):
            dsDataset[varCoord] = dsData[varCoord]
        else:
            if hasattr(grd, varCoord):
                dsDataset[varCoord] = grd[varCoord]

    dsDataset.to_netcdf(outFile, encoding=grd.removeFillValueAttributes(data=dsDataset))

    return

def writeOceanmask(grd, dsData, dsVariable, outVariable, outFile, **kwargs):
    '''Write a ocean mask based on provided information.  This routine
    assumes a depth field is being passed as an argument to create the
    mask.

    MOM6 h-points are masked at and above the MASKING_DEPTH.  A depth
    equal to the MASKING_DEPTH is masked as land.  MASKING_DEPTH is
    ignored if negative.  The default depth is zero (0.0).'''
    
    masking_depth = 0.0
    if 'MASKING_DEPTH' in kwargs.keys():
        masking_depth = kwargs['MASKING_DEPTH']
        if masking_depth < 0:
            masking_depth = 0.0

    dsDataset = xr.Dataset()
    dsDataset[outVariable] = xr.where(dsData[dsVariable] > masking_depth, 1.0, 0.0)
    dsDataset[outVariable].attrs['sha256'] = utils.sha256sum(dsDataset[outVariable])
    # Try to copy coordinates from the supplied variable otherwise, try
    # the supplied grid.
    copyCoords = ['x', 'y']
    for varCoord in copyCoords:
        if hasattr(dsData, varCoord):
            dsDataset[varCoord] = dsData[varCoord]
        else:
            if hasattr(grd, varCoord):
                dsDataset[varCoord] = grd[varCoord]

    dsDataset.to_netcdf(outFile, encoding=grd.removeFillValueAttributes(data=dsDataset))
