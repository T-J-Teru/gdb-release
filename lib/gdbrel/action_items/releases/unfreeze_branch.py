from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import query

QUERY_BLURB = """\
Email the GDB developers that the FREEZE is no longer in effect.

Thank the GDB developers for their patience :-)

"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return 'unfreeze branch'

    def do_AI(self):
        query(QUERY_BLURB)
