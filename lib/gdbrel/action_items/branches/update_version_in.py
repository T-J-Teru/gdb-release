from gdbrel.action_items.branches import AbstractBranchCreationAI
from gdbrel.utils import error, trace

import re

VERSION_IN_COMMIT_REV_LOG = """\
Bump version to %(new_version)s.

Now that the GDB %(branch_version)s branch has been created,
this commit bumps the version number in gdb/version.in to
%(new_version)s

For the record, the GDB %(branch_version)s branch was created
from commit %(branchpoint_SHA1)s.
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

        files_to_commit = [VERSION_IN_FILENAME]

        # If not None, it means we updated the default.exp testcase,
        # and this variable contains its associated ChangeLog entry
        # (this does not include the gdb/testsuite/ChangeLog "header").
        default_exp_CL_entry = None

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
            # On the head branch, we just increment the "major" part
            # of the version number by one. The rest stays the same.
            m = re.match(r'(?P<major>\d+)(?P<rest>\..*)', old)
            if m is None:
                error('Unable to parse version number in {} ({}).'
                      .format(old, VERSION_IN_FILENAME),
                      'Cannot compute new version number for master')
            major = int(m.group('major'))
            new = str(major + 1) + m.group('rest')

            # Now that we updated the major version number, we also need
            # to update the corresponding test in default.exp.

            (default_exp_filename, default_exp_CL_entry) = \
                self.update_gdb_version_in_default_exp(
                    var_name='_gdb_major', new_version=str(major + 1))
            files_to_commit.append(default_exp_filename)

        # Write that new version number:
        with self.sandbox.open(VERSION_IN_FILENAME, 'w') as f:
            f.write(new)

        # Compute the commit's revision log.
        rev_log = (VERSION_IN_COMMIT_REV_LOG
                   % {'new_version': new.strip(),
                      'branch_version': self.cfg['release.branch-version'],
                      'branchpoint_SHA1': self.cfg['release.branchpoint']})
        if default_exp_CL_entry is not None:
            rev_log += "\n".join([
                "",
                "Also, as a result of the version bump, the following changes",
                "have been made in gdb/testsuite:",
                "",
                default_exp_CL_entry])

        # Commit the change.
        self.commit(branch_name, files_to_commit, rev_log)
