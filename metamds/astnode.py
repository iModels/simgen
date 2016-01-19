import os
import re

from dict_merge import data_merge
from searchpath import find_file
from marked_yaml import marked_load as safe_load

class NodeTypeSyntaxError(Exception):
    """Raised to tell the user that there is a problem with the node type."""

    def __init__(self, message, lineno=None, name=None, filename=None):
        self.message = message
        self.lineno = lineno
        self.name = name
        self.filename = filename
        self.source = None

        super(Exception, self).__init__(message)

    def __str__(self):

        # if the source is set, add the line to the output
        if self.source is not None:
            location = 'line %d' % self.lineno
            name = self.filename or self.name
            if name:
                location = 'File "%s", %s' % (name, location)
            lines = [self.message, '  ' + location]

            try:
                line = self.source.splitlines()[self.lineno - 1]
            except IndexError:
                line = None
            if line:
                lines.append('    ' + line.strip())

            return u'\n'.join(lines)
        else:
            return self.message

class AstSyntaxError(Exception):
    """Raised to tell the user that there is a problem with the ast."""

    def __init__(self, message, lineno=None, name=None, filename=None):
        self.message = message
        self.lineno = lineno
        self.name = name
        self.filename = filename
        self.source = None

        super(Exception, self).__init__(message)

    def __str__(self):

        # if the source is set, add the line to the output
        if self.source is not None:
            location = 'line %d' % self.lineno
            name = self.filename or self.name
            if name:
                location = 'File "%s", %s' % (name, location)
            lines = [self.message, '  ' + location]

            try:
                line = self.source.splitlines()[self.lineno - 1]
            except IndexError:
                line = None
            if line:
                lines.append('    ' + line.strip())

            return u'\n'.join(lines)
        else:
            return self.message


class NodeType(object):
    def __init__(self, mapping_or_filename, search_path=''):
        if isinstance(mapping_or_filename, basestring):

            extensions = ['','.yml','.yaml']
            fn = find_file(mapping_or_filename, search_path, extensions)

            if not fn:
                raise IOError('Cannot find file {} in path {}'.format("{}[{}]".format(mapping_or_filename, '|'.join(extensions)), search_path))

            nodetype_name = os.path.basename(fn)
            nodetype_name = nodetype_name.split('.')[0]

            with file(fn, 'r') as f:
                self.mapping = safe_load(f)

                self.mapping['name'] = nodetype_name
                self.mapping['file_name'] = fn
        else:
            self.mapping = mapping_or_filename

        # sanity/syntax check
        if 'name' not in self.mapping:
            raise NodeTypeSyntaxError("Missing 'name' field", filename=self.mapping['file_name'])

        if 'properties' not in self.mapping:
            raise NodeTypeSyntaxError("Missing 'properties' field", filename=self.mapping['file_name'])

    @property
    def name(self):
        return self.mapping['name']

    @property
    def properties(self):
        return self.mapping['properties'].keys()

    @property
    def required_properties(self):
        if 'required' not in self.mapping:
            return []
        else:
            return self.mapping['required']

    def default(self, p):
        """Get the default value for property p"""
        return self.mapping['properties'][p]['default']

    def get_property_type(self, p):
        """Get the type of property p"""
        return self.mapping['properties'][p]['type']


class AstNode(object):
    def __init__(self, mapping_or_filename, search_path=''):
        self.search_path = search_path
        if isinstance(mapping_or_filename, basestring):

            extensions = ['', '.yml', '.yaml']
            fn = find_file(mapping_or_filename, search_path, extensions)

            if not fn:
                raise IOError('Cannot find file {} in path {}'.format("{}[{}]".format(mapping_or_filename, '|'.join(extensions)), search_path))

            with file(fn, 'r') as f:
                mapping_or_filename = safe_load(f)
                # mapping_or_filename['file_name'] = fn

        self.mapping = mapping_or_filename

    @property
    def nodetype_name(self):
        return self.mapping.keys().pop(0)

    @property
    def properties(self):
        return self.mapping[self.nodetype_name].keys()

    def set_property(self, n, v):
        self.mapping[self.nodetype_name][n]=v

    def get_property(self, n):
        return self.mapping[self.nodetype_name][n]

    def merge(self, dict_to_merge):
        self.mapping = data_merge(self.mapping, dict_to_merge)

    def type_check(self, param_name, nodetype):
        param_value = self.get_property(param_name)

        param_type = nodetype.get_property_type(param_name)

        param_is_paceholder =  (isinstance(param_value, basestring) and re.match(r'^\s*\{\{\s*\w+\s*\}\}\s*$', param_value, 0))

        if param_type != 'object' and not param_is_paceholder:
            if param_type == 'integer':
                if not isinstance(param_value, (int,long)):
                    raise AstSyntaxError('Parameter {} is not an integer'.format(param_name), filename=filename, lineno=param_name.start_mark.line)
            if param_type == 'bool' or param_type == 'boolean':
                if not isinstance(param_value, (bool)):
                    raise AstSyntaxError('Parameter {} is not a boolean value'.format(param_name), filename=filename, lineno=param_name.start_mark.line)
            if param_type == 'number':
                if not isinstance(param_value, (float, int, long)):
                    raise AstSyntaxError('Parameter {} is not a number'.format(param_name), filename=filename, lineno=param_name.start_mark.line)
            elif param_type == 'string':
                if not isinstance(param_value, basestring):
                    raise AstSyntaxError('Parameter {} is not a string'.format(param_name), filename=filename, lineno=param_name.start_mark.line)
            elif param_type == 'list':
                if not isinstance(param_value, list):
                    raise AstSyntaxError('Parameter {} is not a list'.format(param_name), filename=filename, lineno=param_name.start_mark.line)
                param_items = nodetype.get_property_items_type(param_name)
                if param_items:
                    for item in param_value:
                        if not self._isinstance(param_value, param_items):
                            raise AstSyntaxError('Parameter {} is not a list of items {}'.format(param_name, param_items.join(' or ')), filename=filename, lineno=param_name.start_mark.line)
            else:
                raise AstSyntaxError('Unknown parameter type: {}'.format(param_type), filename=filename, lineno=param_name.start_mark.line)
        return True

    def validate(self):

        if sum(1 for _ in self.mapping.keys()) != 1:
            raise AstSyntaxError('Ast node must have exactly one root element', filename=filename, lineno=1)

        nodetype = NodeType(self.nodetype_name, self.search_path)

        # check existence of required attrs
        for req_attr in nodetype.required_properties:
            if req_attr not in self.properties:
                raise AstSyntaxError("Ast node does not have required attribute {}".format(req_attr), filename=filename, lineno=1)

        # inject defaults
        for attr in nodetype.properties:
            if attr not in self.properties:
                self.set_property(attr, nodetype.default(attr))

        # type check
        for attr in self.properties:
            # print("attr={}, type={}".format(attr, type(attr)))
            if not self.type_check(attr, nodetype):
                print("Type check failed for attribute {}".format(attr))
                return False

        # recurse
        for attr in self.properties:
            if isinstance(self.get_property(attr), dict):
                ast = AstNode(self.get_property(attr))
                ast.validate()
        return True

if __name__ == '__main__':

    # nt = NodeType('binary_lj_sim', search_path='../concepts')
    # print(nt.name)

    node = AstNode('binary_lj_sim_prg', search_path=['../code', '../concepts'])
    # # ast.validate()
    print(node.nodetype_name)

    for a in node.properties:
        print(a)

    node.validate()