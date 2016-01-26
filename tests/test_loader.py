import os

from tempfile import mkdtemp
import pytest
from os import getcwd

from simgen.ghsync import Loader


def test_split_github_path():
    from simgen.ghsync import split_github_path
    repo_url, path = split_github_path('https://github.com/iModels/concept-creation/n/o')
    assert repo_url == 'https://github.com/imodels/concept-creation.git'
    assert path == '/n/o'

    repo_url, path = split_github_path('https://github.com/iModels/concept-creation.git/n/o')
    assert repo_url == 'https://github.com/imodels/concept-creation.git'
    assert path == '/n/o'

    repo_url, path = split_github_path('https://github.com/iModels/concept-creation')
    assert repo_url == 'https://github.com/imodels/concept-creation.git'
    assert path is None

def test_loader():

    local_root_dir = mkdtemp()

    # create a loader with a new temporary directory
    loader1 = Loader(local_root_dir=local_root_dir)

    # locate requirements.txt, after cloning the repo
    local_path = loader1.find_file("requirements", ["https://github.com/imodels/simgen.git"], implicit_ext=['', '.txt'])
    assert local_path is not None
    assert os.path.realpath(local_path) == os.path.realpath(os.path.join(local_root_dir,'imodels','simgen','requirements.txt'))

    # create a new loader with the same temp dir
    loader2 = Loader(local_root_dir=local_root_dir)

    # locate requirements.txt, after pulling the repo
    local_path = loader2.find_file("requirements", ["https://github.com/imodels/simgen.git"], implicit_ext=['', '.txt'])
    assert local_path is not None
    assert os.path.realpath(local_path) == os.path.realpath(os.path.join(local_root_dir,'imodels','simgen','requirements.txt'))

    # create a new offline loader with explicit github url to local directory association
    loader3 = Loader()
    loader3.add_repo("https://github.com/imodels/simgen.git", os.path.realpath(os.path.join(local_root_dir,'imodels','simgen')))

    # locate requirements.txt locally
    local_path = loader3.find_file("requirements", ["https://github.com/iModels/simgen.git"], implicit_ext=['', '.txt'])
    assert local_path is not None
    assert os.path.realpath(local_path) == os.path.realpath(os.path.join(local_root_dir,'imodels','simgen','requirements.txt'))

def test_loader_local():
    # create a loader
    loader = Loader()
    path_to_this_file, this_file_name = os.path.split(__file__)
    found_file = loader.find_file(file_name=this_file_name, mixed_path = ['./', path_to_this_file])
    assert os.path.realpath(__file__) == os.path.realpath(found_file)

