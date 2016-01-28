from __future__ import print_function

import os
from os import pathsep


def resolve_file_name(candidate, implicitExt=''):
    """Check if file exists, optionally with appended extensions.
    Also allows for files with implicit extensions (eg, .exe, or ['.yml','.yaml']),
    returning the absolute path of the file found.
    """
    if implicitExt:
        if isinstance(implicitExt, (list,tuple)):
            for ext in implicitExt:
                if os.path.isfile(candidate + ext):
                    return candidate + ext
        else:
            if os.path.isfile(candidate + implicitExt):
                return candidate + implicitExt
    else:
        if os.path.isfile(candidate):
            return candidate
    return None

def find_file(seekName, path, implicitExt='', allow_absolute=False):
    """Given a pathsep-delimited path string or list of directories, find seekName.
    Returns path to seekName if found, otherwise None.
    Also allows for files with implicit extensions (eg, .exe, or ['.yml','.yaml']),
    returning the absolute path of the file found.
    >>> find_file('ls', '/usr/bin:/bin', implicitExt='.exe')
    '/bin/ls'
    """
    if allow_absolute:
        fn = resolve_file_name(seekName, implicitExt=implicitExt)
        if fn:
            # Already absolute path.
            return fn
    if isinstance(path, (list, tuple)):
        path_parts = path
    else:
        path_parts = path.split(os.pathsep)
    for p in path_parts:
        candidate = os.path.join(p, seekName)
        fn = resolve_file_name(candidate, implicitExt=implicitExt)
        if fn:
            return fn
    return None

if __name__ == '__main__':
   search_path = 'c:/cygwin/bin' + pathsep + 'c:/cygwin/usr/bin'  # ; on windows, : on unix
   fn = find_file('ls', search_path, implicitExt=['.exe'])
   if fn:
      print("File found at %s" % fn)
   else:
      print("File not found")
