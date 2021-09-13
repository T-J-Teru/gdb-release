from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import trace, info_skipped

COMMIT_REV_LOG = """\
Document the GDB %(release.do_release)s release in gdb/ChangeLog

gdb/ChangeLog:

\tGDB %(release.do_release)s released.
"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return 'add release in gdb/ChangeLog'

    def do_AI(self):
        self.__update_changelog(self.release_branch)
        # No longer necessary for master.
        # self.__update_changelog(self.head_branch)

    def __update_changelog(self, branch):
        # For the head branch, we only want to mention official
        # releases, not pre-releases.
        if branch == self.head_branch and self.is_pre_release():
            info_skipped('${hl_sbu}NO${hl_ebu} ChangeLog entry for the'
                         ' %(gdb_repo.head_branch)s branch'
                         ' (this is only a pre-release)'
                         % self.cfg)
            return

        trace('Updating ChangeLog in branch ${hl_sbu}%(branch)s${hl_ebu}...'
              % {'branch': self.release_branch})

        self.sandbox.checkout(branch)
        rev_log = COMMIT_REV_LOG % self.cfg
        self.commit(branch, (), rev_log)
