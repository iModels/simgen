import logging
from pprint import pprint, pformat

from marked_yaml import marked_load
from astnode import AstNode
from ghsync import Session
from renderer import Renderer

__author__ = 'sallai'

import os
import tempfile

log = logging.getLogger(__file__)

class Error(Exception): pass

class Project(object):
    def __init__(self, repo_url, session=None):

        if session:
            self.session = session
        else:
            self.session = Session()

        self.repo_url = repo_url

        self._load_manifest()
        self._init_renderer()

    def _load_manifest(self):

        with open(self.session.find_file('project.yaml', [self.repo_url]), 'r') as f:
            y = marked_load(f)

        self.title = y['title']
        self.mixed_search_path = y['path']
        # self.local_search_path = self.session.mixed_to_local_path(self.mixed_search_path)

    def _init_renderer(self):
        self.renderer = Renderer(self.session, search_dirs=self.mixed_search_path)

    def find_file(self, file_name, implicit_ext=None):
        self.session.find_file(file_name, self.mixed_search_path, implicitExt=implicit_ext)

    def load_ast(self, file_name):
        # find file
        log.debug('Loading ast from file: {}'.format(file_name))

        # load ast
        ast = AstNode(file_name, self.session, search_path=self.mixed_search_path)
        log.debug("Ast loaded: {}".format(ast))

        # validate
        ast.validate()

        return ast

    def render(self, ast):
        rendered_code = self.renderer.render_ast(ast)
        return rendered_code



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=0)

    # initialize a local session
    session = Session()
    # session.add_repo('https://github.com/imodels/simgen', '/Users/sallai/PycharmProjects/simgen')
    session.add_repo('https://github.com/imodels/simgen', '..')

    # initialize a project
    project = Project('https://github.com/imodels/simgen', session)

    program_name = 'binary_lj_sim_prg'

    ast = project.load_ast(program_name)

    print("Ast is: {}".format(ast))

    generated_code = project.render(ast)

    print("Generated code:\n {}".format(generated_code))