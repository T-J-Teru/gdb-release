from gdbrel.action_items import AbstractAction
from gdbrel.utils import query, warn

import sys

INTRO = """\
Sending emails for the commits on ${hl_sbu}%(branch)s${hl_ebu}:

After you press [Enter] below, an editor will appear with all emails
that are about to be sent. Please review, edit, etc, as needed.
The emails will be sent, with your confirmation, once you exit
the editor.

"""

PUSH_QUERY = """\
Time to push the commits on branch ${hl_sbu}%(branch)s${hl_ebu}:

Now that the emails have been sent, time to push them to the official
repository.

"""

NO_CHANGE_WARNING = """\
No changes to be pushed to remote for branch ${hl_sbu}%(branch)s\
${hl_ebu}

${hl_warn}\
Normally, this is the point where we would push the commits we made
locally, as well as send emails about them.  But it appears that
there are no commits to be pushed for this branch. This message is
to alert you of that fact, which may or may not be normal.

If this is in fact expected, then just press [Enter] to continue
the release process.  Otherwise, press [Ctrl-c] and handle the
problem manually. Once handled, re-run this script.
${no_hl}\

"""

# FIXME: Make the subject a little more flexible.
BRANCH_SUBJECT = """\
FYI/BRANCH: Patches applied to branch %(release.branch_name)s
"""

MASTER_SUBJECT = """\
FYI/HEAD: Patches applied to branch %(gdb_repo.head_branch)s"""


class AI(AbstractAction):
    @property
    def name(self):
        return 'publish all commits'

    def do_AI(self):
        for (branch_name, email_subject) in (
                (self.release_branch, BRANCH_SUBJECT),
                (self.head_branch, MASTER_SUBJECT)):
            self.__publish_for_branch(branch_name, email_subject % self.cfg)

    def __publish_for_branch(self, branch_name, subject):
        subst = {'branch': branch_name}

        if not self.sandbox.has_local_commits(branch_name):
            warn(NO_CHANGE_WARNING % subst)
            return

        query(INTRO % subst)
        self.email_changes(branch_name, subject)
        query(PUSH_QUERY % subst)
        self.git.push('origin', branch_name, _outfile=sys.stdout)
