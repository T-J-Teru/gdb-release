from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import trace, query, indent

import sys

VERIFY_TAG_QUERY = """\
We are about to push the following tag.  Please verify that everything
is correct.

%(tag_info)s

Should we go ahead and push that tag to the official repository?

"""

NO_TAG_FOR_PRE_RELEASES = """\
Skipping tag creation, This is only a pre-release\
 (${hl_sbu}%(release.do_release)s${hl_ebu})

"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return 'create release tag'

    def do_AI(self):
        if self.is_pre_release():
            query(NO_TAG_FOR_PRE_RELEASES % self.cfg)
            return

        # Let's be extra paranoid and ask the user to double-check
        # the tag one more time before pushing it (the --stat is there
        # to avoid the "diff")
        tag_name = self.cfg['release.tag']
        tag_info = self.git.show(tag_name, stat=True, color=True)
        subst = {'tag_name': tag_name,
                 'tag_info': indent(tag_info, '| '),
                 }
        query(VERIFY_TAG_QUERY % subst)
        trace('Pushing new tag (${hl_sbu}%(tag_name)s${hl_ebu})'
              ' to remote...' % subst)
        self.git.push('origin', tag_name, _outfile=sys.stdout)
