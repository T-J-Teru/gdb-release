from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import query, info_skipped

QUERY_BLURB = """\
Updating the online documentation...

This step assumes that the\
 ${hl_sbu}%(sourceware.hostname)s:~%(sourceware.gdbadmin_uid)s/ss${hl_ebu}\
 directory exists.

In case it is accidently deleted, it is controlled under CVS, and thus
can be retrived using (on %(sourceware.hostname)s):

    %% cvs -d /cvs/gdbadmin co ss

Note: These changes do NOT need to be propagated to the gnu.org
copy of the website, since the URL pointing to the pages being updated
are hardcoded to the %(sourceware.hostname)s site. In other words, clicking
on the link in the GDB website that points to this documentation
leads us to the %(sourceware.hostname)s copy of the documentation.

Please execute the following instructions on %(sourceware.hostname)s\
 by hand,
until the scripts are improved to execute them for you:

${hl_q}\
    %% $$HOME/ss/update-web-docs \\
      %(sourceware.ftp.tarball_dir)s/%(release.xz_tarball)s \\
      $$HOME/tmp/update-web-docs \\
      %(sourceware.docs_dir)s \\
      gdb
${no_hl}\

"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return "update the online documentation"

    def do_AI(self):
        if self.is_pre_release():
            info_skipped("This is a pre-release, skipping...")
            return

        query(QUERY_BLURB % self.cfg)
