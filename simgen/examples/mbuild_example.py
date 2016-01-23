import os
import pprint
from simgen.astnode import AstNode
from simgen.ghsync import Loader
from simgen.renderer import Renderer

def build_ethane_box(box, n_molecules):
    from mbuild.examples import Ethane
    import mbuild as mb
    ethane = Ethane()
    full_box = mb.fill_box(ethane, n_molecules, box)
    full_box.name = '{}_ethanes'.format(n_molecules)
    return full_box

def run():

    # create a new offline loader with explicit github url to local directory association
    loader = Loader()
    loader.add_repo("https://github.com/imodels/simgen.git", os.path.join(os.path.split(os.path.dirname(__file__))[0],'..'))

    ethane_box = build_ethane_box(n_molecules=200, box= [3, 3, 3])

    ast_node = AstNode(file_name='prg', loader=loader, search_path=['https://github.com/imodels/simgen/tests/mbuild_test'])

    ast_node.inject({'ethane_box': ethane_box})

    print('Ast:\n{}'.format(pprint.pformat(ast_node)))

    ast_node.validate()

    renderer = Renderer(loader=loader, search_path=['https://github.com/imodels/simgen/tests/mbuild_test'])

    rendered_code = renderer.render_ast(ast_node)

    print('Rendered code:\n{}'.format(rendered_code))

if __name__ == '__main__':
    run()