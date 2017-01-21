from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import trace

import re

VERSION_IN_COMMIT_REV_LOG = """\
Set GDB version number to %(release.do_release)s.

gdb/ChangeLog:

\t* version.in: Set GDB version number to %(release.do_release)s.
\t* PROBLEMS: Likewise.
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

        # Also update the version info in gdb/PROBLEMS file...
        PROBLEMS_FILENAME = 'gdb/PROBLEMS'

        trace('Updating %(filename)s in branch ${hl_sbu}'
              '%(branch_name)s${hl_ebu}...'
              % {'filename': PROBLEMS_FILENAME,
                 'branch_name': self.release_branch})

        problems = self.sandbox.open(PROBLEMS_FILENAME).readlines()
        with self.sandbox.open(PROBLEMS_FILENAME, 'w') as f:
            for line in problems:
                m = re.match(r'(\s*Known\s+problems\s+in\s+GDB)\s', line)
                if m is not None:
                    line = '%s %s\n' % (m.group(1), self.release_version)
                f.write(line)

        # Commit the change.
        rev_log = VERSION_IN_COMMIT_REV_LOG % self.cfg
        self.commit(self.release_branch,
                    (VERSION_IN_FILENAME, PROBLEMS_FILENAME),
                    rev_log)
