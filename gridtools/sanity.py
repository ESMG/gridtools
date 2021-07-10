'''
Generic sanity check routines.
'''

def saneDepthOptions(**kwargs):
    '''Sanity check `*_DEPTH` options for MOM6.

    The following equation must be true for this routine to
    return **True**:

    ``MAXIMUM_DEPTH >= MINIMUM_DEPTH >= MASKING_DEPTH``

    A land mask is applied if a depth is equal to or shallower than
    the ``MASKING_DEPTH``.  If ``MASKING_DEPTH`` is undefined or
    deeper than ``MINIMUM_DEPTH``, the land mask will use the
    ``MINIMUM_DEPTH`` to apply the land mask.

    :return: True of depth options are sane, False otherwise.
    :rtype: boolean

    As the model is initialized, if this parameter is undefined, it is
    set to the maximum as seen from the supplied topography grid.

    **References**

        * `MOM_shared_initialization.F90 <https://github.com/NOAA-GFDL/MOM6/blob/dev/gfdl/src/initialization/MOM_shared_initialization.F90>`_
            * *MINIMUM_DEPTH*, *MASKING_DEPTH*
        * `MOM_fixed_initialization.F90 <https://github.com/NOAA-GFDL/MOM6/blob/dev/gfdl/src/initialization/MOM_fixed_initialization.F90>`_
            * *MAXIMUM_DEPTH*
        * `diagnoseMaximumDepth <https://mom6.readthedocs.io/en/dev-gfdl/api/generated/modules/mom_shared_initialization.html?#f/mom_shared_initialization/diagnosemaximumdepth>`_
    '''

    # Negative MAXIMUM_DEPTH is permitted but ignored for this test
    if kwargs['MAXIMUM_DEPTH'] < 0.0:
        if kwargs['MINIMUM_DEPTH'] >= kwargs['MASKING_DEPTH']:
            return True

    if kwargs['MAXIMUM_DEPTH'] >= kwargs['MINIMUM_DEPTH']:
        if kwargs['MINIMUM_DEPTH'] >= kwargs['MASKING_DEPTH']:
            return True

    return False

