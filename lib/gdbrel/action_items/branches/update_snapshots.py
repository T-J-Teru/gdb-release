from gdbrel.utils import query
from gdbrel.action_items.branches import AbstractBranchCreationAI

AI_BLURB = """\
Please update the snaphot building process to use the new branch:

     1. Log in as gdbadmin on sourceware.org
     2. cd crontab
     3. Edit crontab and change BRANCH to ${hl_sbu}%(branch_name)s${hl_ebu}
        You can verify that your change is correct with the following "diff"
        command:
          %% cvs diff crontab
     4. Commit change in CVS
          %% cvs ci crontab
     5. Load the new crontab file:
          %% crontab crontab

"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return "update nightly snapshots setup"

    def do_AI(self):
        blurb = AI_BLURB % {"branch_name": self.release_branch}
        query(blurb)
