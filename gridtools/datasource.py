# This package will manage data sources

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

    def addDataset(self, newDataset, delete=False):
        '''Add a new dataset to the catalog.  This will not delete an
        exisiting dataset unless the delete flag is True.'''

        dsKey = list(newDataset.keys())[0]
        print("New dataset:", dsKey)

