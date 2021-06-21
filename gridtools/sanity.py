'''
Generic sanity check routines.
'''

def saneDepthOptions(**kwargs):
    '''Sanity check `*_DEPTH` options for MOM6.

    For MOM6, a depth equal to or shallower is masked.  The following
    equation must be true for this routine to return **True**:

    ``MAXIMUM_DEPTH <= MINIMUM_DEPTH <= MASKING_DEPTH``

    :return: True of depth options are sane, False otherwise.
    :rtype: boolean

    A negative `MAXIMUM_DEPTH` is ignored.  As the model is initialized, if
    this parameter is still negative, it is set to the maximum as seen from
    a supplied topography grid.

    **References**

        * `MOM_shared_initialization.F90 <https://github.com/NOAA-GFDL/MOM6/blob/dev/gfdl/src/initialization/MOM_shared_initialization.F90>`_
            * *MINIMUM_DEPTH*, *MASKING_DEPTH*
        * `MOM_fixed_initialization.F90 <https://github.com/NOAA-GFDL/MOM6/blob/dev/gfdl/src/initialization/MOM_fixed_initialization.F90>`_
            * *MAXIMUM_DEPTH*
        * `diagnoseMaximumDepth <https://mom6.readthedocs.io/en/dev-gfdl/api/generated/modules/mom_shared_initialization.html?#f/mom_shared_initialization/diagnosemaximumdepth>`_
    '''

    # Negative MAXIMUM_DEPTH is permitted but ignored for this test
    if kwargs['MAXIMUM_DEPTH'] < 0.0:
        if kwargs['MINIMUM_DEPTH'] <= kwargs['MASKING_DEPTH']:
            return True

    if kwargs['MAXIMUM_DEPTH'] <= kwargs['MINIMUM_DEPTH']:
        if kwargs['MINIMUM_DEPTH'] <= kwargs['MASKING_DEPTH']:
            return True

    return False

