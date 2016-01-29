import os
import shutil

from IPython.display import HTML, display, IFrame
import requests
from IPython.paths import get_ipython_dir

file_path = os.path.normpath(os.path.dirname(__file__))
ip_dir = get_ipython_dir()
nbext_dir = os.path.join(ip_dir, 'nbextensions')

mdsblocks_url = 'file://' + file_path
mdsblocks_dir = 'mdsblocks'
mdsblocks_files = [
    ['mdsblocks-dist.js'],
    ['mdsblocks-ipy.js'],
    ['mdsblocks-dist.css'],
    ['frame.html'],
    ['index.html']
    ]

def install_files(url, dir, files):
    base_url = url
    base_path = os.path.join(nbext_dir, dir)
    try:
        os.makedirs(base_path)
    except OSError:
        pass
    for f in files:
        url = '/'.join([base_url]+f)
        path = os.path.join(base_path, *f)
        try:
            os.makedirs(os.path.split(path)[0])
        except OSError:
            pass
        if url.startswith('file://'):
            src = url[len('file://'):]
            shutil.copy(src, path)
        else:
            r = requests.get(url)
            with open(path, 'wb') as f:
                print('installing: %s' % path)
                f.write(r.content)

install_files(mdsblocks_url, mdsblocks_dir, mdsblocks_files)

id_to_editor_map = dict()

class Editor(object):
    def __init__(self, githubToken, repoUrl):
        self.githubToken = githubToken
        self.repoUrl = repoUrl

    def show(self):
        # save a reference to the current editor object
        id_to_editor_map[id(self)] = self
        frame = """<script language="text/javascript">
                        window.IPY_VARS = {{
                            OAUTH_TOKEN: "{token}",
                            DEFAULT_PROJECT: "{repo}",
                            EDITOR_ID: "{id}"
                        }};

                        console.log('hello!!!!!!!!!');
                        console.log(window.IPY_VARS.OAUTH_TOKEN);
                    </script>
                    <iframe width="99%" height="1000" src="/nbextensions/mdsblocks/frame.html">"""

        frame = frame.format(token=self.githubToken, repo=self.repoUrl, id=id(self))

        print(frame)

        return HTML(frame)
