from metamds.astnode import AstNode
from metamds.dict_merge import data_merge
from metamds.renderer import Renderer


class Simulation(object):
    def __init__(self, prg_path, search_path=''):
        self.prg_path = prg_path
        self.search_path = search_path

    def prep(self, parameters_dict):
        """Prepare the simulation for execution"""
        # load ast
        ast = AstNode(self.prg_path, search_path=self.search_path)

        # merge parameters_dict into ast
        ast.merge(parameters_dict)

        # validate and set defaults
        ast.validate()

        # initialize renderer
        renderer = Renderer(search_path=search_path)

        # generate code
        self.rendered_code = renderer.render_ast(ast.ast)

        return self.rendered_code

if __name__ == '__main__':
    search_path=['../code', '../templates', '../concepts', '../templates/lammps']

    sim = Simulation('binary_lj_sim_prg.yml', search_path=search_path)
    code = sim.prep({})
    print("Generated code:\n"+code)

