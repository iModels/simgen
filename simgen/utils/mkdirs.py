import os

import errno


def mkdirs(filename, is_dirname=False, exists_ok=True):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if not exists_ok:
                raise
            if exc.errno != errno.EEXIST:
                raise
