import logging

from astnode import AstNode
from ghsync import Loader
from renderer import Renderer
from simgen.utils.marked_yaml import marked_load

__author__ = 'sallai'

log = logging.getLogger(__file__)

class Error(Exception): pass

class Project(object):
    def __init__(self, manifest_filename_or_mapping, loader=None):
        """
        :param manifest_filename_or_mapping: file name of project manifest or a mapping containing the same information
        :param project_root_or
        :param loader: loader object that resolves files in a search path
        """

        if loader:
            self.loader = loader
        else:
            self.loader = Loader()

        if isinstance(manifest_filename_or_mapping, basestring):
            # we got a manifest file name, one of
            #  local filename
            #  github path in the form of https://github.com/owner/repo/some/path/to/project.yml
            mapping = self._load_manifest(manifest_filename_or_mapping)
        else:
            # we got a mapping
            mapping = manifest_filename_or_mapping

        # get path, title, etc. from mapping
        assert isinstance(mapping, dict)
        self.title = mapping['title']
        self.mixed_search_path = mapping['path']

    def _load_manifest(self, manifest_filename):
        implicit_exts = ['', '.yaml', '.yml']
        log.debug("Loading project manifest from {} {}".format(manifest_filename, implicit_exts))
        resolved_manifest_filename = self.loader.find_file(manifest_filename, implicit_ext=implicit_exts)
        if resolved_manifest_filename is None:
            raise Error('Cannot find manifest file {}'.format(manifest_filename))
        with open(resolved_manifest_filename, 'r') as f:
            mapping = marked_load(f)

        return mapping

    def load_ast(self, file_name, inject_dict=None, validation=True):
        # find file
        log.debug('Loading ast from file: {}'.format(file_name))

        # load ast
        ast = AstNode(file_name=file_name, loader=self.loader, search_path=self.mixed_search_path)
        log.debug("Ast loaded: {}".format(ast))

        # inject values from inject_dict to replace placeholders in ast
        if inject_dict:
            ast.inject(inject_dict)

        # validate
        if validation:
            ast.validate()

        return ast

    def render(self, ast_or_filename, output_dir='', inject_dict=None, validation=True):
        if isinstance(ast_or_filename, basestring):
            ast = self.load_ast(ast_or_filename, inject_dict=inject_dict, validation=validation)
        else:
            ast = ast_or_filename
            assert isinstance(ast, AstNode)
            ast.inject(inject_dict)
            ast.validate()

        self.renderer = Renderer(self.loader, search_path=self.mixed_search_path, output_dir=output_dir)
        rendered_code = self.renderer.render_ast(ast)
        return rendered_code

