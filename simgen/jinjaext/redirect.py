import logging
import os
from jinja2 import nodes
from jinja2.ext import Extension

from simgen.utils import mkdirs

log = logging.getLogger(__file__)

__author__ = 'sallai'

class RedirectExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['redirect', 'endredirect'])

    def __init__(self, environment):
        super(RedirectExtension, self).__init__(environment)

        # # add the defaults to the environment
        # environment.extend(
        #     fragment_cache_prefix='',
        #     fragment_cache=None
        # )

    def parse(self, parser):
        token = next(parser.stream)
        if token.value == 'redirect':
            lineno = token.lineno

            # now we parse a single expression, which needs to resolve to the file name
            file_name = parser.parse_expression()

            args = [file_name, nodes.ContextReference()]

            # now we parse the body of the redirect block up to `endrediret` and
            # drop the needle (which would always be `endredirect` in that case)
            body = parser.parse_statements(['name:endredirect'], drop_needle=True)

            # now return a `CallBlock` node that calls our _redirector
            # helper method on this extension.
            return nodes.CallBlock(self.call_method('_redirector', args),
                                   [], [], body).set_lineno(lineno)

    def _isinstance(self, value, allowed_types):
        return True

    def _redirector(self, file_name, ast_node, caller):
        body = caller()
        file_name = os.path.join(self.environment.globals['output_dir'], file_name)
        mkdirs.mkdirs(file_name, exists_ok=True)
        with open(file_name, 'w') as f:
            f.write(body)
        return ''


