import logging
import pprint

from simgen.astnode import AstNode
from simgen.utils.marked_yaml import marked_load


from jinja2.runtime import StrictUndefined
from jinja2 import Environment, FileSystemLoader
import yaml
from six import string_types

log = logging.getLogger(__file__)

class Renderer(object):
    def __init__(self, loader, code_path=[], template_path=[], concept_path=[], output_dir='', **kwargs):
        self.loader = loader
        log.info('template_path: {}'.format(template_path))
        log.info('concept_path: {}'.format(concept_path))
        log.info('code_path: {}'.format(code_path))

        self.tempate_path=template_path
        self.concept_path=concept_path
        self.code_path=code_path

        self.env = Environment(loader=FileSystemLoader(self.loader.mixed_to_local_path(template_path)), undefined=StrictUndefined, extensions=['jinja2.ext.with_', 'simgen.jinjaext.template_path.TemplatePathExtension', 'simgen.jinjaext.mbuild_loader.MbuildLoaderExtension', 'simgen.jinjaext.redirect.RedirectExtension'], trim_blocks=True, cache_size=0)
        self.env.globals['render'] = self._make_render()
        self.env.globals['output_dir'] = output_dir

    def _make_render(self):
        def render(mapping):
            return self.render_ast(mapping)
        return render

    def render_ast(self, ast):

        log.debug("Render_ast called with:\n{}".format(pprint.pformat(ast)))

        # for primitive types, convert to string
        if isinstance(ast, (string_types, float, int)):
            return str(ast)

        # if ast is not an AstNode, convert ast to AstNode
        if not isinstance(ast, AstNode):
            ast = AstNode(ast, self.loader, self.concept_path)

        # get template
        template = self.env.get_template (ast.nodetype_name+'.jinja')

        # render and return ast
        rendered_ast = template.render(ast.mapping[ast.nodetype_name])
        assert rendered_ast is not None
        return rendered_ast

    # def render_file(self, file_name, search_path=None):
    #     if not search_path:
    #         search_path = self.search_path
    #
    #     ast_node = AstNode(file_name=file_name, loader=self.loader, search_path=search_path)
    #
    #     return self.render_ast(ast_node)

    def render_file(self, file_name):

        ast_node = AstNode(file_name=file_name, loader=self.loader, code_path=self.code_path, concept_path=self.concept_path)

        return self.render_ast(ast_node)

    def render_string(self, ast_yaml_string, search_path=None):
        ast_node = AstNode(ast_yaml_string, loader=self.loader, code_path=self.code_path, concept_path=self.concept_path)

        return self.render_ast(ast_node)

