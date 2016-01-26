import os
import pprint
from os.path import dirname

from simgen.astnode import AstNode
from simgen.ghsync import Loader
from simgen.project import Project
from simgen.renderer import Renderer

def build_ethane_box(box, n_molecules):
    from mbuild.examples import Ethane
    import mbuild as mb
    ethane = Ethane()
    full_box = mb.fill_box(ethane, n_molecules, box)
    full_box.name = '{}_ethanes'.format(n_molecules)
    return full_box

def run():

    ethane_box = build_ethane_box(n_molecules=200, box= [3, 3, 3])

    offline_project_manifest = os.path.join(dirname(__file__), '..', '..', 'res', 'mbuild_test', 'offline_project.yaml')
    project = Project(offline_project_manifest)

    generated_code = project.render('prg', output_dir='generated_code', inject_dict={'ethane_box': ethane_box})

    print("Generated code:\n {}".format(generated_code))
    print("Additional files have been saved to: ./generated_code")

if __name__ == '__main__':
    run()