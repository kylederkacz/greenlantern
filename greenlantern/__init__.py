'''
Created on Feb 26, 2010

@author: kyleder
'''

import os
import re
from types import ListType, DictType, StringType, NoneType
from greenlantern.exceptions import FilterNotFoundException, \
    VariableOverlapException
from greenlantern.filters import FilterFactory


class Mask(object):

    regex_flags = re.IGNORECASE | re.DOTALL
    used_variable_names = []
    filter_factory = None

    # Regular Expressions
    SPLIT_REGEX = r"(\{\{.*?\}\})"
    FOREACH_REGEX = (
        "(?:"
            "\{\{\s*foreach\s*"
                "(?P<variable>\w*)"
            "\}\}"
            "(?P<content>.*?)"
            "\{\{\s*foreach\s*\}\}"
        ")"
    )
    VARIABLE_REGEX = (
        "(?:"
            "(?:"
                "\{\{\s*?ignore\s*?\}\}"
            ")|(?:"
                "\{\{\s*?"
                    "(?P<variable>\w+)"
                    "(?:[ \|]*)"
                    "(?P<filter>[\w\.]*)"
                "\s*?\}\}"
            ")"
        ")"
    )
    WHITESPACE_REGEX = r"(\>\s*?\\\<)"
    METACHARACTER_REGEX = r"([^\w\s])"

    def __init__(self):
        self.filter_factory = FilterFactory()

    def extract(self, content="", mask=None):
        """
        Parses an HTML document and returns the variables defined by the mask
        file.

        Returns a dictionary object containing the parameters from the
        mask_file populated with their corresponding values from the provided
        content.

        mask_file (string): The absolute or relative path of the mask file
        content (string): The document that contains the data to be extracted
        """

        # Load the mask file or raise a file not found exception
        if mask is not None:
            self.template = mask

        # Compile the template syntax into regular expression syntax
        regex, variables, filters = self._compile_template(self.template)

        # Execute the regular expression search
        variables = self._extract_variables(regex, content, variables)

        # Run any filters against the variables
        variables = self._map_variables(variables, filters)

        return variables

    def load_template(self, mask_file):
        mask_file = os.path.abspath(mask_file)
        # Make sure that the file exists
        if not os.path.exists(mask_file):
            raise Exception("The file '%s' was not found." % mask_file)

        output = ""
        fp = open(mask_file, "r")
        for line in fp:
            output += line
        fp.close()
        self.template = output
        return output

    def _compile_template(self, template):
        # Strip the whitespace
        # TODO: Generalize this so that its not HTML/XML specific
#        condensed_template = re.sub(self.whitespace_regex, ">\s*?<", template)

        # Escape the entire template first
        escaped_template = self._escape_template(template)

        # Compile the FOREACH blocks
        foreach_result = re.sub(self.FOREACH_REGEX,
            self._compile_foreach_template_callback, escaped_template,
            self.regex_flags)

        # Compile the variables and whitespace
        result = re.sub(self.VARIABLE_REGEX,
            self._compile_variable_template_callback, foreach_result,
            self.regex_flags)

        return (result, {}, {})

    def _escape_template(self, template):
        # Split the string
        template_parts = re.split(self.SPLIT_REGEX, template, self.regex_flags)

        # Escape the parts
        def _escape_non_tokens(part):
            if type(part) is not StringType or part.lstrip()[0:2] == "{{":
                return part
            else:
                escaped = re.sub(self.METACHARACTER_REGEX,
                    r"\\\1", part, self.regex_flags)
                nowhitespace = re.sub(self.WHITESPACE_REGEX,
                    ">(?:.*?)\\\<", escaped, self.regex_flags)
                return nowhitespace

        escaped_parts = map(_escape_non_tokens, template_parts)
        return ''.join(escaped_parts)

    def _compile_foreach_template_callback(self, params):
        if params is None:
            return
        reg = params.groupdict()
        print reg

    def _compile_variable_template_callback(self, params):
        reg = params.groupdict()
        # Find the appropriate
        # TODO: Make the functions that can be called extendible
        if reg['variable'] is not None:
            repl = self._variable(reg['variable'], reg['filter'])
        elif reg['variable'] is None:
            repl = self._ignore(reg['variable'])
        else:
            repl = ""
        return repl

    def _extract_variables(self, regex, content, variables={}):
        result = re.search(regex, content, self.regex_flags)
        if type(result) is NoneType:
            return dict(variables.items())
        return dict(variables.items() + result.groupdict().items())

    def _map_variables(self, variables, filters):
        if variables is None \
            or type(variables) is not DictType \
            or len(variables) == 0:
            return {}

        for variable_name in variables:

            # Use recurssion to process any child foreach tags
            if type(variables[variable_name]) is ListType:
                new_children = []
                for child_variables in variables[variable_name]:
                    new_children.append(self._mapVariables(child_variables,
                        filters))

            # Apply the filter to the extracted value if a filter was specified
            else:
                if variable_name in filters:
                    if callable(filters[variable_name]):
                        variables[variable_name] = \
                            filters[variable_name](variables[variable_name],
                                variable_name)
                    else:
                        filter = self.filter_factory\
                            .getFilter(filters[variable_name])
                        variables[variable_name] = \
                            filter(variables[variable_name], variable_name)

        return variables

###############################################################################
# Filter functions
###############################################################################

    def register_filter(self, module=None, method=None):
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
