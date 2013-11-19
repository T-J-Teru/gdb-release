from gdbrel.utils import query, trace
from gdbrel.action_items.branches import AbstractBranchCreationAI

import sys

BLURB = """\
About to create branch: ${hl_sbu}%(branch_name)s${hl_ebu}...

... from the following commit ${hl_q}%(sha1)s${no_hl}:

%(commit_info)s

"""

COMMIT_INFO_FORMAT = """\
| Author: %an <%ae>
| Date: %ad
| Subject: %s
"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return 'branch creation'

    def do_AI(self):
        # Ask confirmation that we're branching on the right commit.
        commit_info = self.git.show(pretty='format:' + COMMIT_INFO_FORMAT,
                                    quiet=True)
        query(BLURB % {'branch_name': self.release_branch,
                       'sha1': self.cfg['release.branchpoint'],
                       'commit_info': commit_info})

        # Create the branch...
        self.sandbox.branch(self.release_branch,
                            self.cfg['release.branchpoint'])

        # Then push it to the remote... Add the --set-upstream switch,
        # which enables some convenient features in git.
        trace('pushing the new branch to the remote...')
        self.git.push('origin', self.release_branch,
                      set_upstream=True,
                      _outfile=sys.stdout)

        # At this point, we are done for this AI.  We don't need to
        # send an email about the branch, since one will be sent later
        # (to the "announce" mailing-list).  We don't want to do it
        # now, because there are a few things to setup for that
        # branch before we announce it.
