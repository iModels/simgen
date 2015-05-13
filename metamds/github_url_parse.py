import urlparse
from urlparse import urlparse

__author__ = 'sallai'

def parse(url):
    result = {}
    o = urlparse(url)
    if o.netloc != 'github.com':
        return None

    path = o.path
    path_parts = path.split('/')
    result['user'] = path_parts[1]
    result['project'] = path_parts[2]
    if len(path_parts) >= 5 and path_parts[3] == 'tree':
        result['tree'] = path_parts[4]
    else:
        return None

    return result

    dir = '_'.join(o.netloc.split(':') + o.path.split('/'))

def build_repo_url(**kwargs):
    return 'https://github.com/{}/{}.git'.format(kwargs['user'], kwargs['project'])

if __name__ == '__main__':
    u1 = 'https://github.com/tinyos/tinyos-main/tree/release_tinyos_2_1_2'
    print(parse(u1))
    print(build_repo_url(**parse(u1)))
