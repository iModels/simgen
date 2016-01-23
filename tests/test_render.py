import os
from simgen.ghsync import Loader
from simgen.astnode import AstNode
from simgen.renderer import Renderer


def test_ast():

    # create a new offline loader with explicit github url to local directory association
    loader = Loader()
    loader.add_repo("https://github.com/imodels/simgen.git", os.path.split(os.path.dirname(__file__))[0])

    ast_node = AstNode(file_name='prg', loader=loader, search_path=['https://github.com/imodels/simgen/tests/ast_test'])

    assert ast_node is not None
    assert ast_node.nodetype_name == 'add'
    assert ast_node.mapping['add'] is not None
    assert ast_node.mapping['add']['expr1'] is not None
    assert ast_node.mapping['add']['expr2'] is not None

    ast_node.validate()


def test_render_local():
    # create a new offline loader with explicit github url to local directory association
    loader = Loader()
    loader.add_repo("https://github.com/imodels/simgen.git", os.path.split(os.path.dirname(__file__))[0])

    ast_node = AstNode(file_name='prg', loader=loader, search_path=['https://github.com/imodels/simgen/tests/ast_test'])

    renderer = Renderer(loader=loader, search_path=['https://github.com/imodels/simgen/tests/ast_test'])

    rendered_code = renderer.render_ast(ast_node)
    assert rendered_code == '1 + 2 + 3'

    rendered_code = renderer.render_file('prg')

    assert rendered_code == '1 + 2 + 3'