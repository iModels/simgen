import os
import re
from tempfile import mktemp, mkdtemp

GITHUB_URL_PATTERN = r'https://(?P<domain>.+?)/(?P<owner>.+?)/(?P<repo>.+?)(.git)?(?P<path>/.+)?$'
_PATTERN = re.compile(GITHUB_URL_PATTERN)


class Error(Exception): pass


def _sync_repo(local_root_dir, repo_org, repo_name, parent_repo_org=None, parent_repo_name=None):
        """Clone github repo to local folder, or pull if a local repo already exists"""
        # adapted from https://gist.github.com/kennethreitz/619473

        repo_org = repo_org.lower()
        repo_name = repo_name.lower()

        # store the current directory
        cwd = os.getcwd()

        if not local_root_dir:
            local_root_dir = mkdtemp()

        # create local root directory (safely)
        try:
            os.makedirs(local_root_dir)
        except OSError:
            pass
        os.chdir(local_root_dir)

        # create org directory (safely)
        try:
            os.makedirs(repo_org)
        except OSError:
            pass

        # enter org dir
        os.chdir(repo_org)

        if os.path.exists(repo_name):
            # do a pull
            os.chdir(repo_name)
            repo_dir = os.getcwd()
            print('Updating repo: {}'.format(repo_name))
            os.system('git pull')

            if parent_repo_org and parent_repo_name:
                print('Adding upstream: {}/{}'.format(parent_repo_org,parent_repo_name))
                os.system('git remote add upstream git@github.com:{}/{}.git'.format(parent_repo_org,parent_repo_name))

            os.chdir('..')

        else:
            # do a clone
            print('Cloning repo: {}/{}'.format(repo_org, repo_name))
            os.system('git clone git@github.com:{}/{}.git'.format(repo_org, repo_name))
            print ('git clone git@github.com:{}/{}.git'.format(repo_org, repo_name))

            os.chdir(repo_name)
            repo_dir = os.getcwd()

            if parent_repo_org and parent_repo_name:
                print('Adding upstream: {}/{}'.format(parent_repo_org, parent_repo_name))
                os.system('git remote add upstream git@github.com:{}/{}.git'.format(parent_repo_org, parent_repo_name))

            os.chdir('..')

        # cd back to the original working directory
        os.chdir(cwd)

        # return the repo directory
        return repo_dir


def sync_repo(local_root_dir, repo_url, parent_repo_url=None):
    """Clone github repo to local folder, or pull if a local repo already exists"""

    if not validate_github_url(repo_url):
        raise Error("Invalid github repo url: {}".format(repo_url))

    (owner, repo, path) = parse_github_url(repo_url)
    if not parent_repo_url:
        return _sync_repo(local_root_dir, owner, repo)
    else:
        if not validate_github_url(parent_repo_url):
            raise Error("Invalid github parent repo url: {}".format(parent_repo_url))

        (parent_owner, parent_repo, parent_path) = parse_github_url(parent_repo_url)
        return _sync_repo(local_root_dir, owner, repo, parent_repo_org=parent_owner, parent_repo_name=parent_repo)

def parse_github_url(gh_path):
    """Get owner, repo name, and optionally a path to a file therein from a github url"""
    result = _PATTERN.match(gh_path)

    if not result:
        return None
    else:
        return (result.group('owner'), result.group('repo'), result.group('path'))


def validate_github_url(gh_path):
    return parse_github_url(gh_path) is not None

def split_github_path(gh_path):
    """Given an url that points to a folder or file in github, split it to project URL and path"""
    result = _PATTERN.match(gh_path)

    if not result:
        return None
    else:
        return ('https://github.com/{owner}/{repo}.git'.format(owner=result.group('owner'), repo=result.group('repo')), result.group('path') )


def mixed_to_local_path(mixed_path, local_root_dir=None):
    """Convert mixed path to local path, cloning/pulling github repos as necessary."""

    local_path = []

    for path_elem in mixed_path:
        if validate_github_url(path_elem):

            (repo_url, path_in_repo) = split_github_path(path_elem)

            local_repo_dir = sync_repo(local_root_dir, repo_url=repo_url)
            print('Local repo dir: {}'.format(local_repo_dir))
            if local_repo_dir:
                # clone/pull is successfule
                if path_in_repo:
                    # make sure we remove the / from the beginning of the path in repo
                    local_path.append(os.path.join(local_repo_dir, path_in_repo[1:]))
                else:
                    local_path.append(local_repo_dir)
            else:
                # error cloning repo... print error message?
                pass
        else:
            # path element is a local directory
            local_path.append(path_elem)

    return local_path


def find_in_mixed_path(file_name, mixed_path, local_root_dir=None, match_func=os.path.exists):

    local_path = mixed_to_local_path(mixed_path, local_root_dir)
    print('Local path: {}'.format(local_path))
    for dirname in local_path:
        candidate = os.path.join(dirname, file_name)
        print('Testing {}'.format(candidate))
        if match_func(candidate):
            return candidate

    raise Error("Can't find file {} in path {}".format(file_name, mixed_path))


if __name__ == '__main__':
    r = split_github_path('https://github.com/iModels/concept-creation/n/o')
    print(r)

    r = split_github_path('https://github.com/iModels/concept-creation.git/n/o')
    print(r)

    r = split_github_path('https://github.com/iModels/concept-creation')
    print(r)

