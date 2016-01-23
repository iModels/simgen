import logging

from astnode import AstNode
from simgen.utils.marked_yaml import marked_load

__author__ = 'sallai'

from jinja2.runtime import StrictUndefined
from jinja2 import Environment, FileSystemLoader
import yaml

log = logging.getLogger(__file__)

class Renderer(object):
    def __init__(self, loader, search_path=None):
        self.loader = loader
        log.info('Search path: {}'.format(search_path))
        self.search_path=search_path
        self.env = Environment(loader=FileSystemLoader(self.loader.mixed_to_local_path(search_path)), undefined=StrictUndefined, extensions=['jinja2.ext.with_', 'simgen.jinjaext.template_path.TemplatePathExtension', 'simgen.jinjaext.mbuild_loader.MbuildLoaderExtension', 'simgen.jinjaext.redirect.RedirectExtension'], trim_blocks=True, cache_size=0)
        self.env.globals['render'] = self._make_render()

    def _make_render(self):
        def render(mapping):
            return self.render_ast(mapping)
        return render

    def render_ast(self, ast):
        # for primitive types, convert to string
        if isinstance(ast, (basestring, float, int)):
            return str(ast)

        # if ast is not an AstNode, convert ast to AstNode
        if not isinstance(ast, AstNode):
            ast = AstNode(ast, self.loader, self.search_path)

        # get template
        template = self.env.get_template (ast.nodetype_name+'.jinja')

        # render and return ast
        rendered_ast = template.render(ast.mapping[ast.nodetype_name])
        assert rendered_ast is not None
        return rendered_ast

    def render_file(self, file_name, search_path=None):
        if not search_path:
            search_path = self.search_path

        ast_node = AstNode(file_name=file_name, loader=self.loader, search_path=search_path)

        return self.render_ast(ast_node)

    def render_string(self, ast_yaml_string, search_path=None):
        ast_node = AstNode(ast_yaml_string, loader=self.loader, search_path=search_path)

        return self.render_ast(ast_node)

