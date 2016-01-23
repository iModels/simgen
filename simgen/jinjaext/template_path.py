import os
from pandas import json
import re
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
import yaml

__author__ = 'sallai'
from jinja2 import nodes
from jinja2.ext import Extension


class TemplatePathExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['pushtemplatepath', 'poptemplatepath'])

    def __init__(self, environment):
        super(TemplatePathExtension, self).__init__(environment)

    def parse(self, parser):
        token = next(parser.stream)
        if token.value == 'pushtemplatepath':
            lineno = token.lineno # parser.stream.next().lineno

            # now we parse a single expression, which needs to resolve to the schema file
            template_path = parser.parse_expression()

            args = [template_path, nodes.ContextReference(), nodes.Const(parser.filename)]

            # now return a `CallBlock` node that calls our _push_tamplate_path
            # helper method on this extension.
            return nodes.CallBlock(self.call_method('_push_template_path', args),
                                   [], [], []).set_lineno(lineno)
        elif token.value == 'poptemplatepath':
            lineno = token.lineno # parser.stream.next().lineno

            args = [nodes.ContextReference()]

            # now return a `CallBlock` node that calls our _pop_template_path
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
