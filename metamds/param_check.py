import os
from pandas import json
import re
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
from jinja2.runtime import Context
import yaml

__author__ = 'sallai'
from jinja2 import nodes
from jinja2.ext import Extension


class ParamCheckExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['implements', 'pushtemplatepath', 'poptemplatepath'])

    def __init__(self, environment):
        super(ParamCheckExtension, self).__init__(environment)

        # # add the defaults to the environment
        # environment.extend(
        #     fragment_cache_prefix='',
        #     fragment_cache=None
        # )

    def parse(self, parser):
        token = next(parser.stream)
        if token.value == 'implements':
            lineno = token.lineno #parser.stream.next().lineno

            # now we parse a single expression, which needs to resolve to the schema file
            schema_file_name = parser.parse_expression()

            args = [schema_file_name, nodes.ContextReference()]

            # now return a `CallBlock` node that calls our _param_check
            # helper method on this extension.
            return nodes.CallBlock(self.call_method('_param_check', args),
                                   [], [], []).set_lineno(lineno)
        elif token.value == 'pushtemplatepath':
            lineno = token.lineno # parser.stream.next().lineno

            # now we parse a single expression, which needs to resolve to the schema file
            template_path = parser.parse_expression()

            args = [template_path, nodes.ContextReference(), nodes.Const(parser.filename)]

            # now return a `CallBlock` node that calls our _param_check
            # helper method on this extension.
            return nodes.CallBlock(self.call_method('_push_template_path', args),
                                   [], [], []).set_lineno(lineno)
        elif token.value == 'poptemplatepath':
            lineno = token.lineno # parser.stream.next().lineno

            args = [nodes.ContextReference()]

            # now return a `CallBlock` node that calls our _param_check
            # helper method on this extension.
            return nodes.CallBlock(self.call_method('_pop_template_path', args),
                                   [], [], []).set_lineno(lineno)

    def _push_template_path(self, template_path, context, current_template_filename, caller):
        current_template_dir = os.path.dirname(current_template_filename)
        new_template_dir = os.path.join(current_template_dir, template_path)
        context.environment.loader.searchpath.insert(0, new_template_dir)
        return u''

    def _pop_template_path(self, context, caller):
        del context.environment.loader.searchpath[0]
        return u''

    def _isinstance(self, value, allowed_types):
        return True

    def _param_check(self, schema_filename, context, caller):
        error = None
        schema = None
        for extension in ['', '.yaml', '.yml', '.json']:
            try:
                contents, filename, uptodate = context.environment.loader.get_source(context.environment, schema_filename+extension)
                schema_filename = schema_filename+extension
                if schema_filename.endswith('.json'):
                    schema = json.loads(contents)
                else:
                    schema = yaml.safe_load(contents)
                break
            except TemplateNotFound as e:
                error = e

        if not schema:
            error.name = error.message = "Could not load {}[.yaml|.yml|.json]?".format(schema_filename)
            raise error

        # TODO: make sure schema is well-formed, e.g. by using Rx (http://rx.codesimply.com/)
        # and raise some meaningful exceptions (SyntaxError) otherwise

        for param_name, param_properties in schema['properties'].iteritems():
            # print "*** param: {}".format(param)
            # for param_name, param_properties in param.iteritems():
                if 'type' in param_properties:
                    param_type = param_properties['type']
                else:
                    param_type = 'object'

                if 'items' in param_properties:
                    param_items = param_properties['items']
                else:
                    param_items = None

                if 'description' in param_properties:
                    param_description = param_properties['description']
                else:
                    param_description = None

                if 'required' in schema and  param_name in schema['required']:
                    param_required = True
                else:
                    param_required = False

                if 'default' in param_properties:
                    param_default = param_properties['default']
                else:
                    param_default = None

                if param_name in context:
                    param_exists = True
                    param_value = context[param_name]
                else:
                    param_exists = False

                # set default value if needed/possible
                if not param_exists and param_default:
                    param_exists = True
                    param_value = param_default
                    context[param_name] = param_value

                # check if param exists
                if param_required and not param_exists:
                    raise TemplateSyntaxError('Parameter {} not found in context'.format(param_name), 1, filename=schema_filename)


                # check param type
                param_is_paceholder =  (isinstance(param_value, basestring) and re.match(r'^\s*\{\{\s*\w+\s*\}\}\s*$', param_value, 0))

                if param_type != 'object' and not param_is_paceholder:
                    if param_type == 'integer':
                        if not isinstance(param_value, (int,long)):
                            raise TemplateSyntaxError('Parameter {} is not an integer'.format(param_name), 1, filename=schema_filename)
                    if param_type == 'bool' or param_type == 'boolean':
                        if not isinstance(param_value, (bool)):
                            raise TemplateSyntaxError('Parameter {} is not a boolean value'.format(param_name), 1, filename=schema_filename)
                    if param_type == 'number':
                        if not isinstance(param_value, (float, int, long)):
                            raise TemplateSyntaxError('Parameter {} is not a number'.format(param_name), 1, filename=schema_filename)
                    elif param_type == 'string':
                        if not isinstance(param_value, basestring):
                            raise TemplateSyntaxError('Parameter {} is not a string'.format(param_name), 1, filename=schema_filename)
                    elif param_type == 'list':
                        if not isinstance(param_value, list):
                            raise TemplateSyntaxError('Parameter {} is not a list'.format(param_name), 1, filename=schema_filename)
                        if param_items:
                            for item in param_value:
                                if not self._isinstance(param_value, param_items):
                                    raise TemplateSyntaxError('Parameter {} is not a list of items {}'.format(param_name, param_items.join(' or ')), 1, filename=schema_filename)
                    else:
                        raise TemplateSyntaxError('Unknown parameter type: {}'.format(param_type), 1, filename=schema_filename)

        return u''

