'''
Created on Feb 26, 2010

@author: kyleder
'''

import os, re
from types import ListType, DictType, StringType, NoneType
from greenlantern.exceptions import * 
from greenlantern.filters import FilterFactory

class Mask(object):
    
    regex_flags = re.IGNORECASE | re.DOTALL
    used_variable_names = []
    filter_factory = None
    
    # Regular Expressions
    split_regex = r"(\{\{.*?\}\})"
    foreach_regex = r"(?:\{\{\s*foreach\s*(?P<variable>\w*)\s*\}\}(?P<content>.*?)\{\{\s*foreach\s*\}\})"
    variable_regex = r"(?:(?:\{\{\s*?ignore\s*?\}\})|(?:\{\{\s*?(?P<variable>\w+)(?:[ \|]*)(?P<filter>[\w\.]*)\s*?\}\}))"
    whitespace_regex = r"(\>\s*?\\\<)"
    metacharacter_regex = r"([^\w\s])"

    
    def __init__(self):
        self.filter_factory = FilterFactory()


    def extract(self, mask_file = "", content = ""):
        """
        Parses an HTML document and returns the variables defined by the mask file.
        
        @type  mask_file: string
        @param mask_file: The absolute or relative path of the mask file
        @type  content: string
        @param content: The document that contains the data to be extracted
        
        @rtype: dict
        @return: A dictionary object containing the parameters from the mask_file populated with 
                 their corresponding values from the provided content.
        """
        
        # Load the mask file or raise a file not found exception
        template = self._loadTemplate(mask_file)
        
        # Compile the template syntax into regular expression syntax
        regex, variables, filters = self._compileTemplate(template)
        
        # Execute the regular expression search
        variables = self._extractVariables(regex, content, variables)
        
        # Run any filters against the variables
        variables = self._mapVariables(variables, filters)
        
        return variables
        
        
    def _loadTemplate(self, mask_file):
        mask_file = os.path.abspath(mask_file)
        # Make sure that the file exists
        if os.path.exists(mask_file) is not True:
            raise Exception("The file '%s' was not found." % mask_file)
        
        output = ""
        fp = open(mask_file, "r")
        for line in fp:
            output += line
        fp.close()
        return output
    
    
    def _compileTemplate(self, template):
        """
        Converts template file syntax into regular expression syntax
        
        @type  template: string
        @param template: The template string that contains template syntax needing
                         to be compiled into regular expression syntax
                         
        @rtype: string, dict, dict
        @return: The compiled regular expression string.
        @return: A dictionary object with unpopulated variables
        @return: A dictionary object that reflects the variable dictionary object, but
                 is a list of the functions that should be applied to each of those variables
        """
        # Strip the whitespace
        # TODO: Generalize this so that its not HTML/XML specific
#        condensed_template = re.sub(self.whitespace_regex, ">\s*?<", template)
        
        # Escape the entire template first
        escaped_template = self._escapeTemplate(template)
        
        # Compile the FOREACH blocks
        foreach_result = re.sub(self.foreach_regex, self._compileForeachTemplateCallback, escaped_template, self.regex_flags)
        
        # Compile the variables and whitespace
        result = re.sub(self.variable_regex, self._compileVariableTemplateCallback, foreach_result, self.regex_flags)
        return (result, {}, {}) 


    def _escapeTemplate(self, template):
        '''
        Returns string that represents a regex escaped version of the provided template, but
        with the {{ token }} items ignored
        
        @param template: The original string to be escaped
        
        @rtype: string
        @return: The escaped string
        '''
        # Split the string
        template_parts = re.split(self.split_regex, template, self.regex_flags)

        # Escape the parts
        def _escapeNonTokens(part):
            if type(part) is not StringType or part.lstrip()[0:2] == "{{":
                return part
            else:
                escaped = re.sub(self.metacharacter_regex, r"\\\1", part, self.regex_flags)
                nowhitespace = re.sub(self.whitespace_regex, ">(?:.*?)\\\<", escaped, self.regex_flags)
                return nowhitespace
        
        escaped_parts = map(_escapeNonTokens, template_parts)
        return ''.join(escaped_parts)
    

    def _compileForeachTemplateCallback(self, params):
        if params is None:
            return
        reg = params.groupdict()
        print reg
        

    def _compileVariableTemplateCallback(self, params):
        '''
        Return the appropriate replacement string
        @param params: the tuple of matches from the regular expression
        '''
        reg = params.groupdict()
        # Find the appropriate
        # TODO: Make the functions that can be called extendible 
        if reg['variable'] is not None: repl = self._variable(reg['variable'], reg['filter'])
        elif reg['variable'] is None: repl = self._ignore(reg['variable'])
        else: repl = ""
        return repl
            

    def _extractVariables(self, regex, content, variables = {}):
        """
        Perform a regular expression match on the content to extract all of the variables
        
        @type  regex: string
        @param regex: The compiled regular expression syntax to be matched against the content
        @type  content: string
        @param content: The string that should be searched within for the variables
        @type  variables: dict
        @param variables: The dictionary of variables to be populated
        
        @rtype: dict
        @return: The dictionary object that has been populated from the regular expression search
        """
        result = re.search(regex, content, self.regex_flags)
        if type(result) is NoneType:
            return dict(variables.items())
        return dict(variables.items() + result.groupdict().items())
    
    
    def _mapVariables(self, variables, filters):
        """
        Loop through the variables and apply any matching filters to them
        
        @type  variables: dict
        @param variables: The dictionary of variables to be processed
        @type  filters: dict
        @param filters: The dictionary of filters to apply to their corresponding variable 
        """
        if variables is None or type(variables) is not DictType or len(variables) == 0:
            return {}

        for variable_name in variables:
            
            # Use recurssion to process any child foreach tags
            if type(variables[variable_name]) is ListType:
                new_children = []
                for child_variables in variables[variable_name]:
                    new_children.append(self._mapVariables(child_variables, filters))

            # Apply the filter to the extracted value if a filter was specified   
            else:
                if variable_name in filters:
                    if callable(filters[variable_name]):
                        variables[variable_name] = filters[variable_name](variables[variable_name], variable_name)
                    else:
                        filter = self.filter_factory.getFilter(filters[variable_name])
                        variables[variable_name] = filter(variables[variable_name], variable_name)

        return variables




###############################################################################
# Filter functions
###############################################################################

    def registerFilter(self, module = None, method = None):
        if method is None:
            raise FilterNotFoundException()
        elif type(method) is ListType:
            self.filter_factory.registerFilter(module, method)
        else:
            self.filter_factory.registerFilter(module, [method])
        
        return True


###############################################################################
# Built-in functions
###############################################################################


    def _foreach(self, name, inner_content):
        if name in self.used_variable_names:
            raise VariableOverlapException(name)
        self.used_variable_names.append(name)
        print inner_content
        
    
    def _ignore(self, name):
        return "(?:.*?)"
    
    
    def _variable(self, name, filter):
        self.used_variable_names.append(name)
        return "(?P<%s>.*?)" % name

