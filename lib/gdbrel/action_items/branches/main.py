from gdbrel.action_items.branches import AbstractBranchCreationAI
from gdbrel.action_items.branches.proof_read_gdb_readme import (
    AI as proof_read_gdb_readme,
)
from gdbrel.action_items.update_head_branch import AI as update_head_branch
from gdbrel.action_items.branches.create_branchpoint_tag import (
    AI as create_branchpoint_tag,
)
from gdbrel.action_items.branches.create_release_branch import (
    AI as create_release_branch,
)
from gdbrel.action_items.update_release_branch import AI as update_release_branch
from gdbrel.action_items.branches.update_version_in import AI as update_version_in
from gdbrel.action_items.branches.disable_devel_mode import AI as disable_devel_mode
from gdbrel.action_items.branches.update_snapshots import AI as update_snapshots
from gdbrel.action_items.branches.web_announce_branch import AI as web_announce_branch
from gdbrel.action_items.branches.double_check_schedule import (
    AI as double_check_schedule,
)
from gdbrel.action_items.branches.announce_branch_by_email import (
    AI as announce_branch_by_email,
)
from gdbrel.action_items.branches.update_news_on_head_branch import (
    AI as update_news_on_head_branch,
)
from gdbrel.action_items.publish_all_commits import AI as publish_all_commits
from gdbrel.utils import info


SKIP_INFO_MSG = """\
Skipping branch creation procedure, already done\
 (branch: ${hl_sbu}%(release.branch_name)s${hl_ebu})
"""

BLURB_AFTER_BRANCH_CREATION_DONE = """\
Branch creation (%(branch_name)s) completed!

Congratulations!

${hl_q}\
Usually, the first pre-release should be created immediately,
${no_hl}\
or right after having checked-in any patch that are needed for
the release but were checked after the branch point.

${hl_warn}\
!!! If you cannot create the first pre-release immediately: !!!
${no_hl}\

Make sure to remember that the first pre-release version number
should be .91, not .90 (otherwise, the version number would end
up going backwards!).

"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return "ALL DONE!"

    @property
    def is_elementary_action_item(self):
        return False

    def skip_info_msg(self):
        return (SKIP_INFO_MSG % self.cfg).splitlines()

    def do_AI(self):
        info("Starting Meta Action Item: Branch Creation...")

        for AI in (
            proof_read_gdb_readme,
            update_head_branch,
            create_branchpoint_tag,
            create_release_branch,
            update_release_branch,
            update_version_in,
            disable_devel_mode,
            update_snapshots,
            web_announce_branch,
            double_check_schedule,
            announce_branch_by_email,
            update_news_on_head_branch,
            publish_all_commits,
        ):
            AI(self.cfg, self.cklist, self.sandbox)

        subst_info = {
            "branch_name": self.release_branch,
            "release_data_file": self.cfg["setup.release_data_file"],
        }
        info(BLURB_AFTER_BRANCH_CREATION_DONE % subst_info)
