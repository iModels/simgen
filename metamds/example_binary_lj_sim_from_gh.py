import logging

import yaml

from ghsync import find_in_mixed_path
from ghsync import mixed_to_local_path
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

program_file = find_in_mixed_path(program, local_code_path, local_root_dir='/tmp')

print('Found program file: {}'.format(program_file))

# load the abstract syntax tree
with file(program_file, 'r') as f:
    ast = yaml.safe_load(f)

# initialize renderer
renderer = Renderer(search_dirs=local_template_path+local_concept_path)

# generate code for hoomd
rendered_code = renderer.render_ast(ast)

print rendered_code

# # set the target of the simulation node to lammps (it was set to hoomd in the input file)
# ast['target'] = 'lammps'
#
# # generate code for lammps
# print renderer.render_ast(ast)
#

