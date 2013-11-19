from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.emails import Email

EMAIL_SUBJECT = 'gdb-%(release.branch-version)s branch FROZEN'

EMAIL_BODY = """
Hello everyone,

Please avoid pushing any commit to the %(release.branch_name)s branch during
the next few hours. I am working on creating the next %(release.kind)s
off this branch.

Also, if at all possible, it saves me a bit of time if you can avoid
pushing changes to the %(gdb_repo.head_branch)s branch, as it would force me
to handle rebasing and conflict resolution (Eg: ChangeLog).

I will send a followup message when the branch is open again.

Thank you,
-- \

%(rel_manager.name)s
"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return 'freeze branch'

    def do_AI(self):
        email = Email(email_from='%s <%s>' % (self.cfg['rel_manager.name'],
                                              self.cfg['rel_manager.email']),
                      email_to=self.cfg['gdb_repo.email.patches'],
                      email_subject=EMAIL_SUBJECT % self.cfg,
                      email_body=EMAIL_BODY % self.cfg)
        email.send_after_confirmation()
