#!//usr/bin/env python
"""Fixes the arcade pyinstaller hook and builds a onefile executable for windows."""
import pkgutil
from os import chdir, pathsep
from pathlib import Path
from subprocess import check_call as call

arcade_path = pkgutil.find_loader('arcade')
if arcade_path is not None:
    arcade_path = arcade_path.path
    hook_path = Path(arcade_path).parent / '__pyinstaller' / 'hook-arcade.py'
    assert hook_path.exists()
    # the arcade hook is incorrectly setup to include chipmunk.dll/.so which doesn't exist
    with hook_path.open('a') as f:
        f.write('\nbinaries = []\n')

    print('updated arcade pyinstaller hook')

call(['git', 'clone', 'https://github.com/pyinstaller/pyinstaller.git'])
chdir('pyinstaller')
chdir('bootloader')
call(['python', 'waf', 'all'])

print('rebuilt pyinstaller bootloader')

chdir('..')
chdir('..')
call(['pip', 'install', '-e', 'pyinstaller'])

print('installed pyinstaller')

call(['pyinstaller',
      '--add-data', '.' + pathsep + '.',
      '--windowed',
      '--onefile',
      'aaaaAAAA/__main__.py'
      ])

print('done')
