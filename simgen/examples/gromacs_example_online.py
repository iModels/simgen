# This example demonstrates how to generate multiple files from a single AST
import logging
import os
from os.path import dirname
from tempfile import mktemp, mkdtemp

from simgen.ghsync import Loader
from simgen.project import Project


def run():
    # # configure logging
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=0)

    # # initialize a project
    project = Project('https://github.com/imodels/simgen/res/binary_lj_sim/online_project.yaml')

    generated_code = project.render('binary_lj_sim_prg', output_dir='generated_code')

    print("Generated code:\n {}".format(generated_code))
    print("Additional files have been saved to: ./generated_code")

if __name__ == '__main__':
    run()