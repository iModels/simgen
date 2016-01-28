import logging
import os
import re
from tempfile import mkdtemp

from os import getcwd

from simgen.utils import searchpath

GITHUB_URL_PATTERN = r'https://(?P<domain>.+?)/(?P<owner>.+?)/(?P<repo>.+?)(.git)?(?P<path>/.+)?$'
_PATTERN = re.compile(GITHUB_URL_PATTERN)


log = logging.getLogger(__file__)


class Error(Exception):
    pass


# def _sync_repo(local_root_dir, repo_org, repo_name, parent_repo_org=None, parent_repo_name=None):
#         """Clone github repo to local folder, or pull if a local repo already exists"""
#         # adapted from https://gist.github.com/kennethreitz/619473
#
#         repo_org = repo_org.lower()
#         repo_name = repo_name.lower()
#
#         # store the current directory
#         cwd = os.getcwd()
#
#         if not local_root_dir:
#             local_root_dir = mkdtemp()
#
#         # create local root directory (safely)
#         try:
#             os.makedirs(local_root_dir)
#         except OSError:
#             pass
#         os.chdir(local_root_dir)
#
#         # create org directory (safely)
#         try:
#             os.makedirs(repo_org)
#         except OSError:
#             pass
#
#         # enter org dir
#         os.chdir(repo_org)
#
#         if os.path.exists(repo_name):
#             # do a pull
#             os.chdir(repo_name)
#             repo_dir = os.getcwd()
#             print('Updating repo: {}'.format(repo_name))
#             os.system('git pull')
#
#             if parent_repo_org and parent_repo_name:
#                 print('Adding upstream: {}/{}'.format(parent_repo_org,parent_repo_name))
#                 os.system('git remote add upstream git@github.com:{}/{}.git'.format(parent_repo_org,parent_repo_name))
#
#             os.chdir('..')
#
#         else:
#             # do a clone
#             print('Cloning repo: {}/{}'.format(repo_org, repo_name))
#             os.system('git clone git@github.com:{}/{}.git'.format(repo_org, repo_name))
#             print ('git clone git@github.com:{}/{}.git'.format(repo_org, repo_name))
#
#             os.chdir(repo_name)
#             repo_dir = os.getcwd()
#
#             if parent_repo_org and parent_repo_name:
#                 print('Adding upstream: {}/{}'.format(parent_repo_org, parent_repo_name))
#                 os.system('git remote add upstream git@github.com:{}/{}.git'.format(parent_repo_org, parent_repo_name))
#
#             os.chdir('..')
#
#         # cd back to the original working directory
#         os.chdir(cwd)
#
#         # return the repo directory
#         return repo_dir
#
#
# def sync_repo(local_root_dir, repo_url, parent_repo_url=None):
#     """Clone github repo to local folder, or pull if a local repo already exists"""
#
#     if not validate_github_url(repo_url):
#         raise Error("Invalid github repo url: {}".format(repo_url))
#
#     (owner, repo, path) = parse_github_url(repo_url)
#     if not parent_repo_url:
#         return _sync_repo(local_root_dir, owner, repo)
#     else:
#         if not validate_github_url(parent_repo_url):
#             raise Error("Invalid github parent repo url: {}".format(parent_repo_url))
#
#         (parent_owner, parent_repo, parent_path) = parse_github_url(parent_repo_url)
#         return _sync_repo(local_root_dir, owner, repo, parent_repo_org=parent_owner, parent_repo_name=parent_repo)

def parse_github_url(gh_path):
    """Get owner, repo name, and optionally a path to a file therein from a github url"""
    result = _PATTERN.match(gh_path)

    if not result:
        return None
    else:
        return (result.group('owner').lower(), result.group('repo').lower(), result.group('path'))


def validate_github_url(gh_path):
    return parse_github_url(gh_path) is not None


def make_github_url(owner, repo, path=''):
    return 'https://github.com/{owner}/{repo}.git{path}'.format(owner=owner.lower(), repo=repo.lower(), path=path)


def split_github_path(gh_path):
    """Given an url that points to a folder or file in github, split it to project URL and path"""
    (owner, repo, path) = parse_github_url(gh_path)
    return make_github_url(owner, repo), path


# def mixed_to_local_path(mixed_path, local_root_dir=None):
#     """Convert mixed path to local path, cloning/pulling github repos as necessary."""
#
#     local_path = []
#
#     for path_elem in mixed_path:
#         if validate_github_url(path_elem):
#
#             (repo_url, path_in_repo) = split_github_path(path_elem)
#
#             local_repo_dir = sync_repo(local_root_dir, repo_url=repo_url)
#             print('Local repo dir: {}'.format(local_repo_dir))
#             if local_repo_dir:
#                 # clone/pull is successfule
#                 if path_in_repo:
#                     # make sure we remove the / from the beginning of the path in repo
#                     local_path.append(os.path.join(local_repo_dir, path_in_repo[1:]))
#                 else:
#                     local_path.append(local_repo_dir)
#             else:
#                 # error cloning repo... print error message?
#                 pass
#         else:
#             # path element is a local directory
#             local_path.append(path_elem)
#
#     return local_path


# def find_file(seekName, mixed_path, implicitExt='', local_root_dir=None):
#     """Given a pathsep-delimited path string or list of directories or github URLs, find seekName.
#     Returns path to seekName if found, otherwise None.
#     Also allows for files with implicit extensions (eg, .exe, or ['.yml','.yaml']),
#     returning the absolute path of the file found.
#     >>> find_file('ls', '/usr/bin:/bin', implicitExt='.exe')
#     '/bin/ls'
#     """
#     local_path = mixed_to_local_path(mixed_path, local_root_dir)
#     return searchpath.find_file(seekName, local_path, implicitExt)




class Loader(object):
    def __init__(self, local_root_dir=None):
        if not local_root_dir:
            local_root_dir = mkdtemp()

        self.local_root_dir = local_root_dir

        log.info('local_root_dir is {}'.format(self.local_root_dir))
        self.gh_to_local_map = dict()

    def add_repo(self, repo_url, local_repo_path):
        if not validate_github_url(repo_url):
            raise Error('Not a valid github repo URL: {}'.repo_url)

        if not os.path.exists(local_repo_path):
            raise Error('Local path does not exist: {}'.local_repo_path)

        (repo_org, repo_name, _) = parse_github_url(repo_url)
        self.gh_to_local_map[make_github_url(repo_org.lower(), repo_name.lower())] = local_repo_path

    def sync_repo(self, repo_url, local_repo_path=None):

        if not validate_github_url(repo_url):
            raise Error('Not a valid github repo URL: {}'.repo_url)

        (repo_org, repo_name, _) = parse_github_url(repo_url)

        if local_repo_path is None:
            # default to local_root_dir/owner/repo

            # store the current directory
            cwd = os.getcwd()

            if not self.local_root_dir:
                self.local_root_dir = mkdtemp()

            # create local root directory (safely)
            try:
                os.makedirs(self.local_root_dir)
            except OSError:
                pass
            os.chdir(self.local_root_dir)

            # create owner directory (safely)
            try:
                os.makedirs(repo_org)
            except OSError:
                pass
            os.chdir(repo_org)


            if os.path.exists(repo_name):
                # do a pull
                os.chdir(repo_name)
                print('Updating repo: {}'.format(repo_name))
                os.system('git pull')
            else:
                # do a clone
                print('Cloning repo: {}/{}'.format(repo_org, repo_name))
                os.system('git clone git@github.com:{}/{}.git'.format(repo_org, repo_name))
                print ('git clone git@github.com:{}/{}.git'.format(repo_org, repo_name))
                os.chdir(repo_name)

            local_repo_path = os.getcwd()

        else:
            if os.path.exists(local_repo_path):
                # do a pull
                os.chdir(local_repo_path)
                print('Updating repo: {}'.format(repo_name))
                os.system('git pull')
            else:
                # create local_repo_path if it does not exist yet
                os.makedirs(local_repo_path, exist_ok=True)
                # do a clone
                print('Cloning repo: {}/{} to {}'.format(repo_org, repo_name, local_repo_path))
                os.system('git clone git@github.com:{}/{}.git {}'.format(repo_org, repo_name, local_repo_path))
                print ('git clone git@github.com:{}/{}.git {}'.format(repo_org, repo_name), local_repo_path)

        # remember the github to local path mapping
        self.add_repo(repo_url, local_repo_path)

        os.chdir(cwd)

        return local_repo_path

    def mixed_to_local_path(self, mixed_path):
        """Convert mixed path to local path, cloning/pulling github repos as necessary."""

        if isinstance(mixed_path, (list, tuple)):
            path_parts = mixed_path
        else:
            path_parts = mixed_path.split(os.pathsep)

        log.debug("Converting mixed path to local: {}".format(path_parts))

        local_path = []

        for path_elem in path_parts:
            if validate_github_url(path_elem):
                # it's a github url
                (repo_url, path_in_repo) = split_github_path(path_elem)

                if repo_url in self.gh_to_local_map:
                    local_repo_dir = self.gh_to_local_map[repo_url]
                else:
                    local_repo_dir = self.sync_repo(repo_url)

                if path_in_repo:
                    local_repo_path = os.path.join(local_repo_dir, path_in_repo[1:])
                else:
                    local_repo_path = local_repo_dir

                # log.debug('Local repo dir of {} is {}'.format(path_elem, local_repo_path))
                local_path.append(local_repo_path)

                # log.debug("Local path is: {} ".format(local_path))

            else:
                # path element is a local directory
                local_path.append(path_elem)

        return local_path

    def find_file(self, file_name, mixed_path=None, implicit_ext=''):
        # import pdb; pdb.set_trace()
        if not mixed_path:
            mixed_path = []

        if validate_github_url(file_name):
            # if file_name is an absolute github path, split it into base url and path, prepending mixed_path with base_url
            repo_url, file_path = split_github_path(file_name)
            mixed_path.insert(0, repo_url)
            file_name = file_path[1:]
        elif file_name.startswith('/'):
            # if file_name is an absolute local path, split it into dir and file_name, prepending mixed_path with dir
            abs_dir, file_name = os.path.split(file_name)
            mixed_path.insert(0, abs_dir)


        local_path = self.mixed_to_local_path(mixed_path)
        log.debug('Mixed path is: {}'.format(local_path))

        log.debug('Local path is: {}'.format(local_path))
        return searchpath.find_file(file_name, local_path, implicit_ext)


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=0)

    r = split_github_path('https://github.com/iModels/concept-creation/n/o')
    print(r)

    r = split_github_path('https://github.com/iModels/concept-creation.git/n/o')
    print(r)

    r = split_github_path('https://github.com/iModels/concept-creation')
    print(r)

    session = Loader()
    local_file = session.find_file('Default', ['https://github.com/iModels/concept-creation/code'], implicit_ext=['.yaml', '.yml'])

    print('Local file: {}'.format(local_file))
