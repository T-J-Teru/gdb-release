from gdbrel.action_items.branches.main import AI as MaybeCreateBranch
from gdbrel.action_items.releases.main import AI as MaybeCreateRelease
from gdbrel.config import Config
from gdbrel.checklist import Checklist
from gdbrel.git.sandboxes import GitSandbox
from gdbrel.utils import info

import os
from os import makedirs
from os.path import isdir
import sys


def do_release(ROOT_DIR):
    cfg = Config(ROOT_DIR)
    cklist = Checklist(cfg)
    sandbox = GitSandbox(os.path.join(cfg['setup.tmp_dir'],
                                      cfg['gdb_repo.name']))

    # Turn off git pagination.  It gets in a way in the context of
    # this task...  Pagers sometimes create a new screen inside which
    # they do the pagination, obscuring the previous output, and then
    # restore the old screen when exiting the pager, thus taking away
    # the contents that was paginated.  With this setting, the output
    # sent to stdout goes there, and stays there.  The Release Manager
    # can then review at will, and even come back to it later on.
    os.environ['GIT_PAGER'] = ''

    # Create the tmp directory, if it does not already exist...
    if not isdir(cfg['setup.tmp_dir']):
        info('GDB tmp directory does not exist; creating...',
             '(%s)' % cfg['setup.tmp_dir'])
        makedirs(cfg['setup.tmp_dir'])

    if not isdir(sandbox.path):
        info('GDB sandbox not found, creating new clone...',
             'from: %s' % cfg['gdb_repo.url'],
             'dest: %s' % sandbox.path)
        sandbox.clone(cfg['gdb_repo.url'],
                      # Only fetch the head branch in the clone.
                      # We will fetch other branches as needed.
                      single_branch=True,
                      branch=cfg['gdb_repo.head_branch'],
                      _outfile=sys.stdout)
    else:
        # If the repository was already created, make sure the URL
        # of the remote matches the URL we got fromt he config file
        # (the official URL almost never changes, but we do occasionally
        # override that URL to a local one when testing these scripts).
        sandbox.git.remote('set-url', 'origin', cfg['gdb_repo.url'])

    MaybeCreateBranch(cfg, cklist, sandbox)
    MaybeCreateRelease(cfg, cklist, sandbox)
