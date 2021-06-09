# This package will manage data sources

import os, json, yaml
import pdb

class DataSource:

    def __init__(self):

        # Catalog:
        #   {'tag': {
        #       'url': '',
        #       'varMap': {},
        #       'dimMap': {}
        #       'xRef': None,
        #       'xArgs': None,
        #     }
        self.catalog = {}
        self._default_catalogEntry = {
                'url': None,
                'variableMap': None,
                'dimensionMap': None,
                'xRef': None,
                'xArgs': None
            }

    def addDataSource(self, newDataSource, delete=False):
        '''Add a new dataset to the catalog.  This will not delete an
        exisiting dataset unless the delete flag is True.  A complete
        description must be provided as the named dataset will completely
        replace any existing map if the delete flag is True.
        '''

        for dsKey in newDataSource.keys():
            #print("New dataset:", dsKey)
            if dsKey in self.catalog.keys() and not(delete):
                # Skip existing keys when delete is False
                continue
            dsMap = newDataSource[dsKey]
            self.catalog[dsKey] = self._default_catalogEntry
            for mapKey in dsMap.keys():
                self.catalog[dsKey][mapKey] = dsMap[mapKey]

    def cleanCatalog(self, catalog):
        '''This removes any empty/null values from the catalog prior to
        saving or printing the values.
        '''
        cleanCat = {}
        for catKey in catalog.keys():
            cleanCat[catKey] = {}
            for refKey in catalog[catKey].keys():
                if catalog[catKey][refKey]:
                    cleanCat[catKey][refKey] = catalog[catKey][refKey]

        return cleanCat

    def clearCatalog(self):
        '''This clears the current catalog.'''
        self.catalog = {}
        return

    def loadCatalog(self, inFile, append=True, overwrite=False):
        '''Loads catalog entries from a json or yaml file.  Default
        behavior is only append entries (append=True).  Any duplicate
        entries are ignored (overwrite=False).  If you wish to only
        overwrite existing entries use append=False and overwrite=True.
        Using append=False and overwrite=False will do nothing.  To
        append and/or replace entries use append=True and overwrite=True.
        '''

        if not(os.path.isfile(inFile)):
            self.grdObj.printMsg("ERROR: The catalog file was not found (%s)." % (inFile), level=logging.ERROR)
            return

        if len(inFile) < 5:
            self.grdObj.printMsg("ERROR: The catalog file is too short (%s).  Be sure to add the json or yaml extension to the filename." % (inFile), level=logging.ERROR)
            return
        extType = inFile[-4:]

        infd = open(inFile, 'r')
        entriesCount = 0
        entriesAdded = 0
        entriesOverwritten = 0
        if extType == 'json':
            newCatalogEntries = json.load(infd)
        if extType == 'yaml':
            newCatalogEntries = yaml.load(infd, Loader=yaml.SafeLoader)
        infd.close()

        for catKeyNew in newCatalogEntries.keys():
            entriesCount = entriesCount + 1
            updateKey = False
            if catKeyNew in self.catalog.keys():
                if overwrite:
                    updateKey = True
                    entriesOverwritten = entriesOverwritten + 1
            else:
                if append:
                    updateKey = True
                    entriesAdded = entriesAdded + 1

            if updateKey:
                self.catalog[catKeyNew] = self._default_catalogEntry
                for refKey in newCatalogEntries[catKeyNew].keys():
                    self.catalog[catKeyNew][refKey] = newCatalogEntries[catKeyNew][refKey]

        self.grdObj.printMsg("Read %d catalog entries (%d added; %d overwritten) from %s" % (entriesCount, entriesAdded, entriesOverwritten, inFile))

        return

    def saveCatalog(self, outFile):
        '''Save currently stored catalog to a file in the chosen format by
        the extension.  Supported extensions are: json, yaml
        '''

        if len(outFile) < 5:
            self.grdObj.printMsg("ERROR: The catalog save file is too short (%s).  Be sure to add the json or yaml extension to the filename." % (outFile), level=logging.ERROR)
            return
        extType = outFile[-4:]

        outfd = open(outFile, 'w')
        if extType == 'json':
            json.dump(self.cleanCatalog(self.catalog), outfd, indent=2)
        if extType == 'yaml':
            yaml.dump(self.cleanCatalog(self.catalog), outfd)
        outfd.close()
