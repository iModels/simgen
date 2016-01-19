import logging

import yaml

from ghsync import find_file
from ghsync import mixed_to_local_path
from astnode import AstNode
from renderer import Renderer

OFFLINE=True

__author__ = 'sallai'
logging.basicConfig(format='%(levelname)s:%(name)s:%(message)s', level=logging.DEBUG)
log = logging.getLogger(__file__)


if OFFLINE:
    local_code_path = ['/Users/sallai/PycharmProjects/simgen/code']
    local_concept_path = ['/Users/sallai/PycharmProjects/simgen/concepts']
    local_template_path = ['/Users/sallai/PycharmProjects/simgen/templates/gromacs']
else:
    local_root = '/tmp'

    code_path = ['https://github.com/iModels/simgen/code']
    concept_path = ['https://github.com/iModels/simgen/concepts']
    template_path = ['https://github.com/iModels/simgen/templates/gromacs']

    local_code_path = mixed_to_local_path(code_path, local_root_dir=local_root)
    local_concept_path = mixed_to_local_path(concept_path, local_root_dir=local_root)
    local_template_path = mixed_to_local_path(template_path, local_root_dir=local_root)

program = 'binary_lj_sim_prg.yml'

program_file = find_file(program, local_code_path, local_root_dir='/tmp')

print('Found program file: {}'.format(program_file))

# load ast
ast = AstNode(program_file, search_path=local_concept_path)

# validate
ast.validate()

# initialize renderer
renderer = Renderer(search_dirs=local_template_path+local_concept_path)

# generate code for hoomd
rendered_code = renderer.render_ast(ast)

print rendered_code
