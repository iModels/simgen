import logging

from astnode import AstNode

__author__ = 'sallai'

from jinja2.runtime import StrictUndefined
from jinja2 import Environment, FileSystemLoader
import yaml

log = logging.getLogger(__file__)

class Renderer(object):
    def __init__(self, session, search_dirs=None):
        self.session = session
        log.info('Search dirs: {}'.format(search_dirs))
        self.env = Environment(loader=FileSystemLoader(self.session.mixed_to_local_path(search_dirs)), undefined=StrictUndefined, extensions=['jinja2.ext.with_', 'param_check.ParamCheckExtension', 'mbuild_loader.MbuildLoaderExtension', 'redirect.RedirectExtension'], trim_blocks=True, cache_size=0)
        self.env.globals['render'] = self._make_render()

    def _make_render(self):
        def render(mapping):
            return self.render_ast(mapping)
        return render

    def render_ast(self, ast, template_search_dirs=None):
        assert isinstance(ast, AstNode)
        template = self.env.get_template (ast.nodetype_name+'.jinja')
        rendered_ast = template.render(ast.mapping[ast.nodetype_name])
        assert rendered_ast is not None
        return rendered_ast

    def render_file(self, ast_yaml_filename, template_search_dirs=None):
        f = file(ast_yaml_filename, 'r')
        mapping = yaml.safe_load(f)
        f.close()

        return self.render_ast(mapping, template_search_dirs=template_search_dirs)

    def render_string(self, ast_yaml_string, template_search_dirs=None):
        mapping = yaml.safe_load(ast_yaml_string)
        return self.render_ast(mapping, template_search_dirs=template_search_dirs)

