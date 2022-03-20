from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import is_pre_release, trace

VERSION_IN_COMMIT_REV_LOG = """\
Bump GDB's version number to %(new_version)s.

This commit changes gdb/version.in to %(new_version)s.
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

        files_to_commit = [VERSION_IN_FILENAME]

        # If not None, it means we updated the default.exp testcase,
        # and this variable contains its associated ChangeLog entry
        # (this does not include the gdb/testsuite/ChangeLog "header").
        default_exp_CL_entry = None

        self.sandbox.checkout(self.release_branch)

        new_version = self.__new_version()
        with self.sandbox.open(VERSION_IN_FILENAME, 'w') as f:
            f.write(new_version + '\n')

        if not is_pre_release(self.release_version):
            # We just created an official release, which means that
            # we updated the version number from <major>.<minor> to
            # <major>.<minor>.<revision-info>.
            #
            # Because of the addition of the <revision-info> part,
            # GDB sets "$_gdb_minor" to <minor+1>. As a result of that,
            # we need to update its expected value in the default.exp
            # testcase.

            version_minor = int(self.release_version.split('.')[1])
            (default_exp_filename, default_exp_CL_entry) = \
                self.update_gdb_version_in_default_exp(
                    var_name='_gdb_minor', new_version=str(version_minor + 1))
            files_to_commit.append(default_exp_filename)

        # Compute the commit's revision log.
        rev_log = VERSION_IN_COMMIT_REV_LOG % {'new_version': new_version}
        if default_exp_CL_entry is not None:
            rev_log += "\n".join([
                "",
                "This commit also makes the following changes in gdb/testsuite:",
                "",
                default_exp_CL_entry])

        # Commit the change.
        self.commit(self.release_branch, files_to_commit, rev_log)

    def __new_version(self):
        release_version = self.release_version
        if len(release_version.split('.')) < 3:
            # There is no micro number in the version number, which means
            # we just created an official release from this branch.
            # Add the '.90' micro number at the end.
            release_version = release_version + '.90'
        return '%s.DATE-git' % release_version
