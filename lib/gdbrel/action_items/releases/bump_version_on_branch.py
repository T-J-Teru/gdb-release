from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import trace

VERSION_IN_COMMIT_REV_LOG = """\
Bump GDB's version number to %(new_version)s.

This commit changes gdb/version.in to %(new_version)s.
"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return "set new version number"

    def do_AI(self):
        VERSION_IN_FILENAME = "gdb/version.in"

        trace(
            "Updating %(filename)s in branch ${hl_sbu}"
            "%(branch_name)s${hl_ebu}..."
            % {"filename": VERSION_IN_FILENAME, "branch_name": self.release_branch}
        )

        files_to_commit = [VERSION_IN_FILENAME]

        self.sandbox.checkout(self.release_branch)

        new_version = self.__new_version()
        with self.sandbox.open(VERSION_IN_FILENAME, "w") as f:
            f.write(new_version + "\n")

        # Compute the commit's revision log.
        rev_log = VERSION_IN_COMMIT_REV_LOG % {"new_version": new_version}

        # Commit the change.
        self.commit(self.release_branch, files_to_commit, rev_log)

    def __new_version(self):
        release_version = self.release_version
        if len(release_version.split(".")) < 3:
            # There is no micro number in the version number, which means
            # we just created an official release from this branch.
            # Add the '.90' micro number at the end.
            release_version = release_version + ".90"
        return "%s.DATE-git" % release_version
