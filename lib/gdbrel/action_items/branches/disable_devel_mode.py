from gdbrel.action_items.branches import AbstractBranchCreationAI
from gdbrel.utils import trace, error

import os

DEVEL_COMMIT_REV_LOG = """\
Set development mode to "off" by default.

%(devel_dirname)s/ChangeLog:

\t* %(devel_basename)s (development): Set to false.
"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return 'set development to false'

    def do_AI(self):
        self.sandbox.checkout(self.release_branch)

        # For newer versions of binutils-gdb.git, the development.sh
        # script lives in bfd/. But we want to maintain a certain amount
        # of support for older versions of GDB, in case we want to make
        # new releases on old branches. So, try each location...
        DEVEL_FILENAMES = ('bfd/development.sh', 'gdb/development.sh')
        devel_file = None
        for f in DEVEL_FILENAMES:
            if self.sandbox.isfile(f):
                devel_file = f
                break
        if devel_file is None:
            error('Cannot find development.sh script')

        # Change 'development=true' into 'development=false'.
        trace('Fixing %s...' % devel_file)
        with self.sandbox.open(devel_file) as f:
            old_txt = f.readlines()
        with self.sandbox.open(devel_file, 'w') as f:
            for line in old_txt:
                if line.startswith('development='):
                    line = 'development=false\n'
                f.write(line)

        # Commit the change...
        rev_log = (DEVEL_COMMIT_REV_LOG
                   % {'devel_dirname': os.path.dirname(devel_file),
                      'devel_basename': os.path.basename(devel_file),
                      })
        self.commit(self.release_branch, devel_file, rev_log)
