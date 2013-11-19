from gdbrel.action_items.branches import AbstractBranchCreationAI
from gdbrel.utils import trace

import os

DEVEL_COMMIT_REV_LOG = """\
Set development mode to "off" by default.

gdb/ChangeLog:

\t* %(devel_basename)s (development): Set to false.
"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return 'set development to false'

    def do_AI(self):
        DEVEL_FILENAME = 'gdb/development.sh'

        self.sandbox.checkout(self.release_branch)

        # Change 'development=true' into 'development=false'.
        trace('Fixing %s...' % DEVEL_FILENAME)
        with self.sandbox.open(DEVEL_FILENAME) as f:
            old_txt = f.readlines()
        with self.sandbox.open(DEVEL_FILENAME, 'w') as f:
            for l in old_txt:
                if l.startswith('development='):
                    l = 'development=false\n'
                f.write(l)

        # Commit the change...
        rev_log = (DEVEL_COMMIT_REV_LOG
                   % {'devel_basename': os.path.basename(DEVEL_FILENAME)})
        self.commit(self.release_branch, DEVEL_FILENAME, rev_log)
