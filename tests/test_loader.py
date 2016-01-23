from tempfile import mkdtemp

import pytest


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
    import os
    from simgen.ghsync import Loader

    local_root_dir = mkdtemp()

    # create a loader with a new temporary directory
    loader1 = Loader(local_root_dir=local_root_dir)

    # locate project.yaml, after cloning the repo
    local_path = loader1.find_file("project", ["https://github.com/imodels/simgen.git"], implicit_ext=['.yaml', '.yml'])
    assert os.path.realpath(local_path) == os.path.realpath(os.path.join(local_root_dir,'imodels','simgen','project.yaml'))

    # create a new loader with the same temp dir
    loader2 = Loader(local_root_dir=local_root_dir)

    # locate project.yaml, after pulling the repo
    local_path = loader2.find_file("project", ["https://github.com/imodels/simgen.git"], implicit_ext=['.yaml', '.yml'])
    assert os.path.realpath(local_path) == os.path.realpath(os.path.join(local_root_dir,'imodels','simgen','project.yaml'))

    # create a new offline loader with explicit github url to local directory association
    loader3 = Loader()
    loader3.add_repo("https://github.com/imodels/simgen.git", os.path.realpath(os.path.join(local_root_dir,'imodels','simgen')))

    # locate project.yaml locally
    local_path = loader3.find_file("project", ["https://github.com/iModels/simgen.git"], implicit_ext=['.yaml', '.yml'])
    assert os.path.realpath(local_path) == os.path.realpath(os.path.join(local_root_dir,'imodels','simgen','project.yaml'))


