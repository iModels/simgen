import logging

from astnode import AstNode
from ghsync import Loader
from renderer import Renderer
from simgen.utils.marked_yaml import marked_load

__author__ = 'sallai'

log = logging.getLogger(__file__)

class Error(Exception): pass

class Project(object):
    def __init__(self, repo_url, loader=None):

        if loader:
            self.loader = loader
        else:
            self.loader = Loader()

        self.repo_url = repo_url
        self._load_manifest()

    def _load_manifest(self):
        log.debug("Loading project.yml from {}".format(self.repo_url))
        with open(self.loader.find_file('project', [self.repo_url], implicit_ext=['.yaml', '.yml','']), 'r') as f:
            y = marked_load(f)

        self.title = y['title']
        self.mixed_search_path = y['path']

    # def find_file(self, file_name, implicit_ext=None):
    #     self.loader.find_file(file_name, self.mixed_search_path, implicit_ext=implicit_ext)

    def load_ast(self, file_name):
        # find file
        log.debug('Loading ast from file: {}'.format(file_name))

        # load ast
        ast = AstNode(file_name=file_name, loader=self.loader, search_path=self.mixed_search_path)
        log.debug("Ast loaded: {}".format(ast))

        # validate
        ast.validate()

        return ast

    def render(self, ast_or_filename, output_dir=''):
        if isinstance(ast_or_filename, basestring):
            ast = self.load_ast(ast_or_filename)
        else:
            ast = ast_or_filename

        assert isinstance(ast, AstNode)

        self.renderer = Renderer(self.loader, search_path=self.mixed_search_path, output_dir=output_dir)
        rendered_code = self.renderer.render_ast(ast)
        return rendered_code

