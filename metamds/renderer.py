__author__ = 'sallai'

from jinja2.runtime import StrictUndefined
from jinja2 import Environment, FileSystemLoader
import yaml


class Renderer(object):
    def __init__(self, search_dirs=None):
        self.env = Environment(loader=FileSystemLoader(search_dirs), undefined=StrictUndefined, extensions=['jinja2.ext.with_', 'param_check.ParamCheckExtension', 'mbuild_loader.MbuildLoaderExtension'], trim_blocks=True, cache_size=0)
        self.env.globals['render'] = self._make_render()

    def render_ast(self, ast, template_search_dirs=None):
        ast_node_type = ast.keys()[0]
        template = self.env.get_template (ast_node_type+'.jinja')
        return template.render(ast[ast_node_type])

    def render_file(self, ast_yaml_filename, template_search_dirs=None):
        f = file(ast_yaml_filename, 'r')
        mapping = yaml.safe_load(f)
        f.close()

        return self.render_ast(mapping, template_search_dirs=template_search_dirs)

    def render_string(self, ast_yaml_string, template_search_dirs=None):
        mapping = yaml.safe_load(ast_yaml_string)
        return self.render_ast(mapping, template_search_dirs=template_search_dirs)

    def _make_render(self):
        def render(mapping):
            return self.render_ast(mapping)
        return render

#
# if __name__ == '__main__':
#     print Renderer(search_dirs=['../templates','../concepts']).render_file('../code/lj_spheres.yml')

