from gdbrel.action_items.branches import AbstractBranchCreationAI
from gdbrel.emails import Email

EMAIL_SUBJECT = "GDB %(release.branch-version)s release branch created!"

EMAIL_BODY = """\
Hello,

A quick message to announce that the GDB %(release.branch-version)s \
branch has just been created.

The prerelease snapshots will be available at:

    ftp://%(sourceware.hostname)s/%(sourceware.ftp.branch_public_dir)s/\
gdb.tar.xz

The sources are also accessible via GIT:

    git clone --single-branch --branch=%(release.branch_name)s\
 %(gdb_repo.public_url)s

This announcement has also been posted on the GDB web site at:

    http://www.sourceware.org/gdb/

"""

CONFIRMATION_BLURB = """\
Please confirm the following email to be sent:

%(email_as_string)s

"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return 'new branch email announcement'

    def do_AI(self):
        email_subject = EMAIL_SUBJECT % self.cfg
        email_body = EMAIL_BODY % self.cfg
        email = Email(email_from='%s <%s>' % (self.cfg['rel_manager.name'],
                                              self.cfg['rel_manager.email']),
                      email_to=self.cfg['gdb_repo.email.announce'],
                      email_subject=email_subject,
                      email_body=email_body)

        email.send_after_confirmation()
