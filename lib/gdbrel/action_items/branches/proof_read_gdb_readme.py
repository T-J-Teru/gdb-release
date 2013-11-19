from gdbrel.utils import query
from gdbrel.action_items.branches import AbstractBranchCreationAI

AI_BLURB = """\
Please proof-read the gdb/README file:

    Normally, there should be no modification needed (the update of
    the GDB version number will automatically be taken care of later).
    But if you find any, then please commit them now before going
    further.

    Note: Most likely, a commit in the past will be used as the branch
    point for our upcoming branch, which may result in this change
    not being part of the initial branch. If this is the case:
    ${hl_q}Remember to port this change to the upcoming branch as soon
    as it has been created.${no_hl}

"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return 'gdb/README proofing'

    def do_AI(self):
        query(AI_BLURB)
