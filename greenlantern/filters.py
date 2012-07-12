'''
Created on Mar 1, 2010

@author: alex
@author: kyleder
'''
from greenlantern.exceptions import FilterNotFoundException, FilterExistsException
import re

class FilterFactory:
    _filterDictionary = {}
    
    def __init__(self):
        # TODO: Auto-load the built-in filters
        self._filterDictionary = {}
        pass
    

    def registerFilter(self, module, methodnames):
        for name in methodnames:
            if self._filterDictionary.has_key(name):
                raise FilterExistsException(name)
            dict = module.__dict__
            self._filterDictionary[name] = dict[name]

    
    def getFilter(self, name):
        if self._filterDictionary.has_key(name):
            return self._filterDictionary[name]
        else:
            raise FilterNotFoundException(name)



###############################################################################
# Built-in filters
###############################################################################

def stripHTML(content, name):
    return re.sub(r"(\<.*?\>)", "", content)
