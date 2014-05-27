from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import query, info_skipped

QUERY_BLURB = """\
Updating the ARI for our release...

Please execute the following instructions on %(sourceware.hostname)s\
 by hand,
until the scripts are improved to execute them for you:

${hl_q}\
    %% /bin/sh ~/ss/update-web-ari \\
       %(sourceware.ftp.tarball_dir)s/%(release.xz_tarball)s \\
       ~/tmp/www \\
       %(sourceware.ari_dir)s \\
       gdb
${no_hl}\

"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return 'update the ARI'

    def do_AI(self):
        if self.is_pre_release():
            info_skipped('This is a pre-release, skipping...')
            return

        query(QUERY_BLURB % self.cfg)
