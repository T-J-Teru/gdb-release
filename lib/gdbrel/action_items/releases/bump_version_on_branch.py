from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import trace

import re

VERSION_IN_COMMIT_REV_LOG = """\
Bump GDB version number to %(new_version)s.

gdb/ChangeLog:

\t* version.in: Set GDB version number to %(new_version)s.
"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return 'set new version number'

    def do_AI(self):
        VERSION_IN_FILENAME = 'gdb/version.in'

        trace('Updating %(filename)s in branch ${hl_sbu}'
              '%(branch_name)s${hl_ebu}...'
              % {'filename': VERSION_IN_FILENAME,
                 'branch_name': self.release_branch})

        self.sandbox.checkout(self.release_branch)

        new_version = self.__new_version()
        with self.sandbox.open(VERSION_IN_FILENAME, 'w') as f:
            f.write(new_version + '\n')

        # Commit the change.
        rev_log = VERSION_IN_COMMIT_REV_LOG % {'new_version': new_version}
        self.commit(self.release_branch, VERSION_IN_FILENAME, rev_log)

    def __new_version(self):
        release_version = self.release_version
        if len(release_version.split('.')) < 3:
            # There is no micro number in the version number, which means
            # we just created the first official release from this branch.
            # For versioning purposes, this is equivalent to having the
            # micro number set to "0".
            #
            # That way, after release x.y got released, the version number
            # for the snapshots become x.y.0.DATE-git, instead of just
            # x.y.DATE-git (as per the internals' manual).
            release_version = release_version + '.0'
        return '%s.DATE-git' % release_version
