import logging

from simgen.astnode import AstNode
from simgen.ghsync import Loader
from simgen.renderer import Renderer
from simgen.utils.marked_yaml import marked_load

from six import string_types

log = logging.getLogger(__file__)


class Error(Exception):
    pass


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

        if isinstance(manifest_filename_or_mapping, string_types):
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
        self.code_path = mapping['code_path']
        self.concept_path = mapping['concept_path']
        self.template_path = mapping['template_path']

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
        ast = AstNode(file_name=file_name, loader=self.loader, code_path=self.code_path, concept_path=self.concept_path)
        log.debug("Ast loaded: {}".format(ast))

        # inject values from inject_dict to replace placeholders in ast
        if inject_dict:
            ast.inject(inject_dict)

        # validate
        if validation:
            ast.validate()

        return ast

    def render(self, ast_or_filename, output_dir='', inject_dict=None, validation=True):
        if isinstance(ast_or_filename, string_types):
            ast = self.load_ast(ast_or_filename, inject_dict=inject_dict, validation=validation)
        else:
            ast = ast_or_filename
            assert isinstance(ast, AstNode)
            ast.inject(inject_dict)
            ast.validate()

        self.renderer = Renderer(self.loader, output_dir=output_dir, code_path=self.code_path, concept_path=self.concept_path, template_path=self.template_path)
        rendered_code = self.renderer.render_ast(ast)
        return rendered_code


    def render_tasks(self, ast_or_filename, output_dir='', inject_dict=None, validation=True):

        gen_code = self.render(ast_or_filename, output_dir, inject_dict, validation)
        run_script = []
        for line in gen_code.split("\n"):
            if line.strip().startswith("#"):
                continue
            elif not line.strip():
                continue
            else:
                run_script.append(line.strip())

        return run_script