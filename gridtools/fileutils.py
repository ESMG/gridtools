# file functions file operations
# File Functions File Operations

# This library contains common file operations used by
# the gridtools library.

import urllib.parse

def resolveDataSource(grd, dsName):
    '''This returns a final filename to gridtools to handle cases where
       the user may or may not provide a file:// prefix to filenames.

       This routine does not check if the resolved filename exists.

       This may also be a data source via ds:// in which we translate to
       a file:// spec.

       http://, https:// and gql:// are not supported at this time.
    '''

    dsUrl = urllib.parse.urlparse(dsName)
    # At this point, we assume this is a local filename
    urlToOpen = dsName

    # Gridtools catalog entry
    if dsUrl.scheme == 'ds':
        dsObj = dsUrl.path
        if dsObj in self.dataSourcesObj.catalog.keys():
            dsObj = self.dataSourcesObj.catalog[dsName]
            if 'url' in dsObj.keys():
                dsUrl = urllib.parse.urlparse(dsObj['url'])
                # At this point, we assume this is a local filename
                urlToOpen = dsObj['url']

    # Remote file specs
    if dsUrl.scheme in ['http', 'https', 'gql']:
        # SEE IF WE CAN GET A CALLING ROUTINE TO TRACK DOWN SOURCE
        msg = ("ERROR: Local filenames can not be determined for for http, https and gql at present.\ndsName = %s\nURL = %s\n")
        grd.printMsg(msg, logging.ERROR)
        return None

    # Local file spec
    if dsUrl.scheme == 'file':
        urlToOpen = dsUrl.path

    return urlToOpen
