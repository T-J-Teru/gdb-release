from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import query

QUERY_BLURB = """\
Email the GDB developers that the FREEZE is no longer in effect.

For that, I simply reply to the email that was previously sent
by this script: It allows mailers to have both the freeze email
and the unfreeze email to be seen together in people's email.

Hint: You can change the email subject to indicate the unfreeze.
      For instance:

          gdb-17 branch now *OPEN* (was: "gdb-17 branch FROZEN")
"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return "unfreeze branch"

    def do_AI(self):
        query(QUERY_BLURB)
