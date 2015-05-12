import os
import re
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
import yaml

__author__ = 'sallai'
from jinja2 import nodes
from jinja2.ext import Extension
import importlib


class MbuildLoaderExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['mbuild_loader'])

    def __init__(self, environment):
        super(MbuildLoaderExtension, self).__init__(environment)

        # # add the defaults to the environment
        # environment.extend(
        #     fragment_cache_prefix='',
        #     fragment_cache=None
        # )

    def parse(self, parser):
        token = next(parser.stream)
        if token.value == 'mbuild_loader':
            lineno = token.lineno #parser.stream.next().lineno

            # now we parse a single expression, which needs to resolve to the schema file
            schema_file_name = parser.parse_expression()

            args = [schema_file_name, nodes.ContextReference()]

            # now return a `CallBlock` node that calls our _param_check
            # helper method on this extension.
            return nodes.CallBlock(self.call_method('_mbuild_loader', args),
                                   [], [], []).set_lineno(lineno)

    def _isinstance(self, value, allowed_types):
        return True

    def _mbuild_loader(self, concept_filename, ast_node, caller):

        contents, filename, uptodate = ast_node.environment.loader.get_source(ast_node.environment, concept_filename)

        concept = yaml.safe_load(contents)

        # import the mbuild compound


        compound_path = ast_node["compound"]
        arguments = ast_node["arguments"]


        kwargs = dict()

        for arg in arguments:
            k = arg['arg']['name']
            v = arg['arg']['value']
            kwargs[k] = v




        compound_module_name, compound_class_name = os.path.splitext(compound_path)

        compound_module = importlib.import_module(compound_module_name, package=None)

        # import pdb
        # pdb.set_trace()

        compound_class = getattr(compound_module, compound_class_name[1:])

        m = compound_class(**kwargs)

        # apply atomtyping

        # write out files

        # dump the lammps/hoomds script that will be included in the jinja output
        simulation_script_text = u"% this is the simulation script code that makes use of the generated files"

        return simulation_script_text

