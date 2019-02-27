from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import trace

import re

VERSION_IN_COMMIT_REV_LOG = """\
Set GDB version number to %(release.do_release)s.

gdb/ChangeLog:

\t* version.in: Set GDB version number to %(release.do_release)s.
"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return 'set release version number'

    def do_AI(self):
        VERSION_IN_FILENAME = 'gdb/version.in'

        trace('Updating %(filename)s in branch ${hl_sbu}'
              '%(branch_name)s${hl_ebu}...'
              % {'filename': VERSION_IN_FILENAME,
                 'branch_name': self.release_branch})

        self.sandbox.checkout(self.release_branch)

        with self.sandbox.open(VERSION_IN_FILENAME, 'w') as f:
            f.write(self.release_version + '\n')

        # Commit the change.
        rev_log = VERSION_IN_COMMIT_REV_LOG % self.cfg
        self.commit(self.release_branch, VERSION_IN_FILENAME, rev_log)
