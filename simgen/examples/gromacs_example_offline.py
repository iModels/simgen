# This example demonstrates how to generate multiple files from a single AST
import logging
import os
from os.path import dirname
from tempfile import mktemp, mkdtemp

from simgen.ghsync import Loader
from simgen.project import Project


def run():
    res_dir = os.path.join(dirname(__file__), '..', '..', 'res', 'binary_lj_sim')

    manifest = {
        'title': 'Binary LJ Simulation',
        'code_path': [os.path.join(res_dir, 'code')],
        'concept_path': [os.path.join(res_dir, 'concepts')],
        'template_path': [os.path.join(res_dir, 'templates')]
    }

    project = Project(manifest)

    generated_code = project.render('binary_lj_sim_prg', output_dir='generated_code')

    print("Generated code:\n {}".format(generated_code))
    print("Additional files have been saved to: ./generated_code")

if __name__ == '__main__':
    run()