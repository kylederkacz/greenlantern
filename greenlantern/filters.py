'''
Created on Mar 1, 2010

@author: alex
@author: kyleder
'''
import re

from greenlantern.exceptions import FilterNotFoundException


class FilterFactory:
    _filter_dictionary = {}

    def __init__(self):
        # TODO: Auto-load the built-in filters
        self._filter_dictionary = {
            'strip_html': strip_html
        }

    def register_filter(self, name, filter_method):
        self._filter_dictionary[name] = dict[name]

    def getFilter(self, name):
        if name in self._filter_dictionary:
            return self._filter_dictionary[name]
        else:
            raise FilterNotFoundException(name)


###############################################################################
# Built-in filters
###############################################################################

def strip_html(content, name):
    return re.sub(r"(\<.*?\>)", "", content)
