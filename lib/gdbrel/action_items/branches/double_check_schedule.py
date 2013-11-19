from gdbrel.utils import query
from gdbrel.action_items.branches import AbstractBranchCreationAI

AI_BLURB = """\
Please visit the following URL and confirm the schedule:

    http://www.sourceware.org/gdb/schedule/

If you do make a change, remember to send the patch to gdb-patches.

"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return 'double-check schedule on web'

    def do_AI(self):
        query(AI_BLURB)
