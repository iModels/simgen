from git.objects.commit import Commit
import yaml

__author__ = 'sallai'

import os
import tempfile
from urlparse import urlparse
from git import Repo
import github_url_parse as ghu
join = os.path.join

# functions to fetch the dependencies of a project from git sources

# def repo_url_to_local_path(repo_url, prefix=''):
#     o = urlparse(repo_url)
#     dir = '_'.join(o.netloc.split(':') + o.path.split('/'))
#     return join(prefix,dir)


def pru_to_local_path(parsed_repo_url, prefix=''):
    dir = '_'.join(['github.com', parsed_repo_url['user'], parsed_repo_url['project'], parsed_repo_url['tree']])
    return join(prefix,dir)

def load_manifest(local_repo_path):
    f = file(join(local_repo_path,'project.yaml'), 'r')
    manifest = yaml.safe_load (f)
    return manifest

def fetch(repo_urls, tempdir=None, url_to_local_path_map=None):

    if not url_to_local_path_map:
        url_to_local_path_map = dict();

    if not repo_urls:
        return url_to_local_path_map

    if not tempdir:
        tempdir = tempfile.mkdtemp(prefix='gittool')

    for repo_url in repo_urls:
        parsed_repo_url = ghu.parse(repo_url)

        # if parsing is not successful, treat it as a local folder
        if parsed_repo_url is None:
            if os.path.isdir(repo_url):
                url_to_local_path_map[repo_url] = repo_url
            else:
                print('Folder not found: ' + repo_url)
            continue

        local_repo_path = pru_to_local_path(parsed_repo_url, prefix=tempdir)

        repo = None

        # check if local repo exists
        if os.path.exists(local_repo_path):
            repo = Repo.init(local_repo_path, mkdir=False)
            # do a pull
            repo.remotes.origin.pull()

        if not repo:
            # clean up dir
            import shutil
            try:
                shutil.rmtree(local_repo_path)
            except:
                pass
            # clone repo
            repo = Repo.clone_from(ghu.build_repo_url(**parsed_repo_url), local_repo_path)

            assert Repo.init(local_repo_path).__class__ is Repo


        # switch to commit/branch/tag
        # import ipdb; ipdb.set_trace()
        repo.head.reset(parsed_repo_url['tree'])

        url_to_local_path_map[repo_url] = local_repo_path

        manifest = load_manifest(local_repo_path)

        u2lp = fetch(manifest['path'], tempdir=tempdir, url_to_local_path_map=url_to_local_path_map)

    return url_to_local_path_map

class Project(object):

    def __init__(self, repo_url):
        """
        Initialize a project
        :param repo_url: the url of the repository.
        :return:
        """

        # check out project repo and all referenced projects
        self.tempdir = '/tmp/gittool'
        self.url_to_local_path_map = fetch([repo_url], tempdir=self.tempdir)
        manifest = load_manifest(self.url_to_local_path_map[repo_url])
        self.title = manifest['title']
        self.path = manifest['path']

    def find(self, filepath):
        """
        Find a file relative to the repo url list of the project.
        :param filepath: e.g. path/to/somefile.txt
        :return:
        """

        for repo_url in self.path:
            try:
                local_repo_path = self.url_to_local_path_map[repo_url]
                if os.path.exists(join(local_repo_path,filepath)):
                    return join(local_repo_path, filepath)
            except KeyError:
                # the repo url does not exist
                pass

        raise IOError('file {} not found under search path {}'.format(filepath, str(self.path)))

if __name__ == '__main__':

    # project = Project('https://github.com/iModels/metamds-cli/tree/master')
    project = Project('https://github.com/sallai/metamds-p2/tree/6a693e409d271f67ebb27c952b1631eb352249a1')
    print project.url_to_local_path_map
    print project.find('project.yaml')
    # import ipdb; ipdb.set_trace()