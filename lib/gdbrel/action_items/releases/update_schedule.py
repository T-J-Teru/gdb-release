from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import query

QUERY_BLURB = """\
Please visit the following URL and confirm the schedule:

        ${hl_sbu}http://www.sourceware.org/gdb/schedule/${hl_ebu}

%(official_release_blurb)s

If you do make a change, remember to send the patch to gdb-patches.
"""

OFFICIAL_RELEASE_BLURB = """\
${hl_q}\
Since this is an official release, please update the "Schedule History"
table at that page to add an entry for our release.
${no_hl}\
"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return 'update schedule web page'

    def do_AI(self):
        official_release_blurb = ('' if self.is_pre_release()
                                  else OFFICIAL_RELEASE_BLURB)
        subst = {'official_release_blurb': official_release_blurb}
        query(QUERY_BLURB % subst)
