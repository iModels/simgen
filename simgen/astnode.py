import collections
import os
import re
from pprint import pformat

from simgen.utils.dict_merge import data_merge
from simgen.utils.marked_yaml import marked_load as safe_load, marked_load

#PLACEHOLDER_PATTERN = r'^\s*\{\{\s*\(?P<name>w+)\s*\}\}\s*$'
PLACEHOLDER_PATTERN = r'^\s*\{\{\s*(?P<name>\w+)\s*\}\}\s*$'
_PATTERN = re.compile(PLACEHOLDER_PATTERN)


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
    def __init__(self, mapping=None, file_name=None, loader=None, search_path=[]):
        assert loader is not None
        self.loader = loader

        self.search_path = search_path
        if mapping:
            self.file_name = file_name
            self.mapping = mapping
        else:
            assert isinstance(file_name, basestring)

            extensions = ['', '.yml', '.yaml']
            fn = self.loader.find_file(file_name, search_path, extensions)

            if not fn:
                raise IOError('Cannot find file {} in path {} (local path:{})'.format("{}[{}]".format(file_name, '|'.join(extensions)), search_path, self.loader.mixed_to_local_path(search_path)))

            with file(fn, 'r') as f:
                mapping = marked_load(f)
                nodetype_name = os.path.basename(fn)
                nodetype_name = nodetype_name.split('.')[0]
                if mapping.has_key('name'):
                    if mapping['name'] != nodetype_name:
                        raise NodeTypeSyntaxError("Name attribute does not match file name: {} != {}".format(mapping['name'], nodetype_name), filename=fn)
                else:
                    mapping['name'] = nodetype_name

            self.file_name = fn
            self.mapping = mapping

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

    def get_property_items_type(self, p):
        """Get the type of property p"""
        if self.mapping['properties'][p].has_key('items'):
            return self.mapping['properties'][p]['items']
        else:
            return None

class AstNode(object):
    def __init__(self, mapping=None, file_name=None, loader=None, search_path=[]):
        assert loader is not None
        self.loader = loader

        self.search_path = search_path
        if mapping:
            self.file_name = file_name
            self.mapping = mapping
        else:
            assert isinstance(file_name, basestring)

            extensions = ['', '.yml', '.yaml']
            fn = self.loader.find_file(file_name, search_path, extensions)

            if not fn:
                raise IOError('Cannot find file {} in path {} (local path:{})'.format("{}[{}]".format(file_name, '|'.join(extensions)), search_path, self.loader.mixed_to_local_path(search_path)))

            with file(fn, 'r') as f:
                mapping = safe_load(f)

            self.file_name = fn
            self.mapping = mapping

        if sum(1 for _ in self.mapping.keys()) != 1:
            raise AstSyntaxError('Ast node must have exactly one root element', filename=self.file_name, lineno=1)


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

    def is_instance(self, value, typename_list, listitem_typesnames=None):
        """Check if the type of a value matches at least one types in the typename_list."""
        type_match = False
        for typename in typename_list:
            # check primitive types
            if ((typename == 'object') or
                        (typename == 'integer' and isinstance(value, (int, long))) or
                        (typename == 'number' and isinstance(value, (int, long, float))) or
                        (typename == 'boolean' and isinstance(value, bool)) or
                        (typename == 'string' and isinstance(value, basestring))
            ):
                type_match = True
                break
            # check user defined types
            elif isinstance(value, dict) and value.has_key(typename):
                type_match = True
                break
            elif typename == 'list' and isinstance(value, collections.Iterable):
                if not listitem_typesnames:
                    # untyped list
                    type_match = True
                else:
                    # typed list
                    type_match = True
                    for v in value:
                        if not self.is_instance(v, listitem_typesnames):
                            type_match = False
                if type_match:
                    break

        return type_match

    def validate(self):

        self.nodetype = NodeType(file_name=self.nodetype_name, loader=self.loader, search_path=self.search_path)

        # check existence of required attrs
        for req_property_name in self.nodetype.required_properties:
            if req_property_name not in self.properties:
                raise AstSyntaxError("Ast node does not have required attribute {}".format(req_property_name), filename=self.mapping.file_name, lineno=1)

        # inject defaults
        for property_name in self.nodetype.properties:
            if property_name not in self.properties:
                self.set_property(property_name, self.nodetype.default(property_name))

        # type check
        for property_name in self.properties:
            value = self.get_property(property_name)

            # check if value is a placeholder, in the format of '{{ placeholder_name }}'
            if (isinstance(value, basestring) and re.match(r'^\s*\{\{\s*\w+\s*\}\}\s*$', value, 0)):
                # it's a placeholder, so don't do type checking
                continue

            # the allowed types (one or more) for the given parameter
            typename_list = self.nodetype.get_property_type(property_name)

            # if the typename_list contains a list type, listitem_typenames specify the allowed list item types
            listitem_typenames = self.nodetype.get_property_items_type(property_name)


            if not isinstance(typename_list, list):
                typename_list = [typename_list]

            if not self.is_instance(value, typename_list, listitem_typenames):
                raise AstSyntaxError('Type of parameter {} is not {}, but {}'.format(property_name, typename_list, type(value)), filename=self.file_name, lineno=property_name.start_mark.line)

        # recurse
        for property_name in self.properties:
            # recurse if it's a dict
            if isinstance(self.get_property(property_name), dict):
                ast = AstNode(mapping=self.get_property(property_name), loader=self.loader, search_path=self.search_path, file_name=self.file_name)
                ast.validate()
            # recurs if it's a list containing dists
            if isinstance(self.get_property(property_name), collections.Iterable):
                for list_item in self.get_property(property_name):
                    if isinstance(list_item, dict):
                        ast = AstNode(mapping=list_item, loader=self.loader, search_path=self.search_path, file_name=self.file_name)
                        ast.validate()

        return True

    def inject(self, mapping):

        # type check
        for property_name in self.properties:
            value = self.get_property(property_name)

            # check if value is a placeholder, in the format of '{{ placeholder_name }}'
            if isinstance(value, basestring):
                result = _PATTERN.match(value)
                if result:
                    # it's a placeholder
                    name = result.group('name')

                    # replace placeholder with
                    if name in mapping:
                        self.set_property(property_name, mapping[name])
            # recurse if value is a dict
            if isinstance(value, dict):
                ast = AstNode(mapping=value, loader=self.loader, search_path=self.search_path, file_name=self.file_name)
                ast.inject(mapping)

            # if the value is a list, try recursing into the items
            if isinstance(value, collections.Iterable):
                for list_item in value:
                    if isinstance(list_item, dict):
                        ast = AstNode(mapping=list_item, loader=self.loader, search_path=self.search_path, file_name=self.file_name)
                        ast.inject(mapping)



    def __repr__(self):
        return "AstNode(nodetype.name={}, ast={})".format(self.nodetype_name, pformat(self.mapping))

