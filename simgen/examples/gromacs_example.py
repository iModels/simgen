# This example demonstrates how to generate multiple files from a single AST
import logging
import os

from simgen.ghsync import Loader
from simgen.project import Project


def run():
    # configure logging
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=0)

    # create a new offline loader with explicit github url to local directory association
    loader = Loader()
    loader.add_repo("https://github.com/imodels/simgen.git", os.path.join(os.path.split(os.path.dirname(__file__))[0],'..'))

    # initialize a project
    project = Project('https://github.com/imodels/simgen/tests/binary_lj_sim', loader)

    program_name = 'binary_lj_sim_prg'

    ast = project.load_ast(program_name)

    generated_code = project.render(ast)

    print("Generated code:\n {}".format(generated_code))

if __name__ == '__main__':
    run()