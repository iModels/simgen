import yaml

from metamds.astnode import AstNode
from renderer import Renderer

__author__ = 'sallai'

# load ast
ast = AstNode('binary_lj_sim_prg', search_path=['../code', '../concepts'])

# validate
ast.validate()

# initialize renderer
renderer = Renderer(search_path=['../templates', '../concepts', '../templates/lammps'])

# generate code for hoomd
rendered_code = renderer.render_ast(ast.ast)

print rendered_code