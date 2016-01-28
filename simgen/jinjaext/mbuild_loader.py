import os
import re
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
import yaml

from simgen.utils import mkdirs

__author__ = 'sallai'
from jinja2 import nodes
from jinja2.ext import Extension
import importlib


class MbuildLoaderExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['save_compound'])

    def __init__(self, environment):
        super(MbuildLoaderExtension, self).__init__(environment)

        # # add the defaults to the environment
        # environment.extend(
        #     fragment_cache_prefix='',
        #     fragment_cache=None
        # )

    def parse(self, parser):
        token = next(parser.stream)
        if token.value == 'save_compound':
            lineno = token.lineno #parser.stream.next().lineno

            compound = parser.parse_expression()
            system_name = parser.parse_expression()
            forcefield = parser.parse_expression()

            args = [compound, system_name, forcefield, nodes.ContextReference()]

            # now return a `CallBlock` node that calls our _param_check
            # helper method on this extension.
            return nodes.CallBlock(self.call_method('_save_compound', args),
                                   [], [], []).set_lineno(lineno)

    def _isinstance(self, value, allowed_types):
        return True

    def _save_compound(self, compound, system_name, forcefield, ast_node, caller):

        import mbuild as mb
        if isinstance(compound, mb.Compound):
            system_name = os.path.join(self.environment.globals['output_dir'], system_name)
            mkdirs.mkdirs(system_name, exists_ok=True)
            compound.save(system_name, forcefield=forcefield, overwrite=True)
        else:
            raise TemplateSyntaxError("Context is not an mBuild Compound.", 0)

        return ''

