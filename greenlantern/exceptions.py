'''
Created on Feb 26, 2010

@author: kyleder
'''
    

class VariableOverlapException(Exception):
    def __init__(self, variable_name):
        self.value = "The variable named %s was previously defined in the template. Please choose a unique variable name and try again." % variable_name


class FilterExistsException(Exception):
    def __init__(self, filter_name):
        self.value = "The filter %s has already been registered." % filter_name


class FilterNotFoundException(Exception):
    def __init__(self, filter_name):
        self.value = "The filter function %s could not be found." % filter_name
        
