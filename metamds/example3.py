import yaml
from renderer import Renderer

__author__ = 'sallai'

def run_simulation(simulation_ast_file, working_directory='.' ):
    # load the abstract syntax tree
    with file(simulation_ast_file, 'r') as f:
        ast = yaml.safe_load(f)

    # initialize renderer
    renderer = Renderer(search_dirs=['../concepts', '../templates/python'])

    # generate code for hoomd
    rendered_code = renderer.render_ast(ast)

    file_name = 'input.data'
    n_step = 1000

    tmp_rendered_code_file_name = 'tmp_rendered_code.py'
    with file(tmp_rendered_code_file_name, 'w') as f:
        f.write(rendered_code)

    execfile(tmp_rendered_code_file_name)
    # exec(rendered_code)

if __name__ == '__main__':
    run_simulation('../code/lj_spheres_prg.yml')
