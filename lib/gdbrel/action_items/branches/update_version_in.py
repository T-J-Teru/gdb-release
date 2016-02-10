from gdbrel.action_items.branches import AbstractBranchCreationAI
from gdbrel.utils import trace

import re

VERSION_IN_COMMIT_REV_LOG = """\
Bump version to %(new_version)s.

Now that the GDB %(branch_version)s branch has been created, we can
bump the version number.

gdb/ChangeLog:

\tGDB %(branch_version)s branch created (%(branchpoint_SHA1)s):
\t* version.in: Bump version to %(new_version)s.
"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return 'version.in update (branch+HEAD)'

    def do_AI(self):
        self.__update_version_in(self.release_branch)
        self.__update_version_in(self.head_branch)

    def __update_version_in(self, branch_name):
        VERSION_IN_FILENAME = 'gdb/version.in'

        trace('Updating %(filename)s in branch ${hl_sbu}'
              '%(branch_name)s${hl_ebu}...'
              % {'filename': VERSION_IN_FILENAME,
                 'branch_name': branch_name})

        self.sandbox.checkout(branch_name)

        # Get the current version number.
        with self.sandbox.open(VERSION_IN_FILENAME) as f:
            old = f.readline()

        # Next, compute the new version number, which depends on which
        # branch is being updated.
        if branch_name == self.release_branch:
            # On the release branch, we "micro" part of the version
            # number, usually updating it from .50 to .90.
            new = re.sub(r'(\d+\.\d+)\.\d+\.', r'\1.90.', old)
        else:
            # On the head branch, we update the "major.minor" part
            # of the version number to the branch version number, leaving
            # the "micro" part intact.  For instance, when if we're at
            # version 6.7.50-DATE-git, and the branch version is 7.0,
            # then the new version becomes 7.0.50-DATE-git.
            new = re.sub(r'\d+.\d+.', r'%s.'
                         % self.cfg['release.branch-version'],
                         old)

        # Write that new version number:
        with self.sandbox.open(VERSION_IN_FILENAME, 'w') as f:
            f.write(new)

        # Commit the change.
        rev_log = (VERSION_IN_COMMIT_REV_LOG
                   % {'new_version': new.strip(),
                      'branch_version': self.cfg['release.branch-version'],
                      'branchpoint_SHA1': self.cfg['release.branchpoint']})
        self.commit(branch_name, VERSION_IN_FILENAME, rev_log)
