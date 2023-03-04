from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.emails import Email

import os

PRE_RELEASE_SUBJECT = """\
GDB %(release.do_release)s available for testing
"""

PRE_RELEASE_BODY = """\
Hello,

I have just finished creating the gdb-%(release.do_release)s pre-release.
It is available for download at the following location:

    https://%(sourceware.hostname)s/%(sourceware.ftp.branch_public_dir)s\
/%(release.xz_tarball)s

A gzip'ed version is also available: %(release.gzip_tarball)s.

Please give it a test if you can and report any problems you might find.

On behalf of all the GDB contributors, thank you!
-- \n\
%(rel_manager.name)s
"""

RELEASE_SUBJECT = """\
GDB %(release.do_release)s released!
"""

RELEASE_BODY = """\
%(announcement)s

-- \n\
%(rel_manager.name)s
"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return "email release announcement"

    def do_AI(self):
        if self.is_pre_release():
            email_to = self.cfg["gdb_repo.email.patches"]
            email_subject = PRE_RELEASE_SUBJECT % self.cfg
            email_body = PRE_RELEASE_BODY % self.cfg
        else:
            subst = {
                "announcement": self.__get_announcement(),
                "rel_manager.name": self.cfg["rel_manager.name"],
            }
            # Add ANNOUNCE from htdocs to subst.
            email_to = ", ".join(
                [
                    self.cfg["gdb_repo.email.announce"],
                    self.cfg["gdb_repo.email.info-gnu"],
                ]
            )
            email_subject = RELEASE_SUBJECT % self.cfg
            email_body = RELEASE_BODY % subst

        email = Email(
            email_from="%s <%s>"
            % (self.cfg["rel_manager.name"], self.cfg["rel_manager.email"]),
            email_to=email_to,
            email_subject=email_subject,
            email_body=email_body,
        )
        email.send_after_confirmation()

    def __get_announcement(self):
        with open(
            os.path.join(self.cfg["setup.htdocs_sandbox"], "download/ANNOUNCEMENT")
        ) as f:
            return f.read().rstrip()
