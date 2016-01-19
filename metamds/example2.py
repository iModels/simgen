import yaml
from renderer import Renderer

__author__ = 'sallai'

# load the abstract syntax tree
with file('../code/lj_spheres_prg.yml', 'r') as f:
    ast = yaml.safe_load(f)

# initialize renderer
renderer = Renderer(search_path=['../templates', '../concepts', '../templates/python'])

# generate code for hoomd
rendered_code = renderer.render_ast(ast)

print rendered_code

# # set the target of the simulation node to lammps (it was set to hoomd in the input file)
# ast['target'] = 'lammps'
#
# # generate code for lammps
# print renderer.render_ast(ast)
#

