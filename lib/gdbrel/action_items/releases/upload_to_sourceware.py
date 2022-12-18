from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.errors import FatalError
from gdbrel.utils import query, info_skipped, indent, file_size_in_MiB

from datetime import datetime
import os
from subprocess import call, STDOUT
import sys

SCP_QUERY = """\
Making the tarballs available at %(sourceware.hostname)s:

Making the gdb-%(release.do_release)s tarballs available at:

    %(tarballs_remote_url)s

Please confirm that the above is correct.

"""

NEW_FTP_README = """\

                GDB FTP directory

           GDB %(release.do_release)s, Released %(today_utc)s

See the GDB home page http://www.gnu.org/software/gdb/
for more information about GDB.

        gdb-%(release.do_release)s.tar.xz                  %(xz_size)sMiB
        gdb-%(release.do_release)s.tar.gz                  %(gz_size)sMiB
"""

NEW_README_QUERY = """\
Updating the README file on the FTP server.

%(readme_contents)s

Please confirm that the README above is correct.  If correct, this
file will be scp'ed to:

  %(tarballs_remote_url)s

"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return "upload tarballs to sourceware"

    def do_AI(self):
        self.__scp_tarballs()
        self.__update_ftp_readme()

    def __scp_tarballs(self):
        tmp_dir = self.cfg["setup.tmp_dir"]
        tarballs_remote_url = self.__tarballs_remote_url()
        scp_cmd = [
            "scp",
            os.path.join(tmp_dir, self.cfg.release_xz_tarball),
            os.path.join(tmp_dir, self.cfg.release_gzip_tarball),
            os.path.join(tarballs_remote_url, "."),
        ]

        subst = dict(self.cfg.data)
        subst["tarballs_remote_url"] = tarballs_remote_url
        query(SCP_QUERY % subst)

        status = call(scp_cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=STDOUT)
        if status != 0:
            raise FatalError(
                "Failed to scp release tarballs to sourceware host"
                " (error code: %d)." % status
            )

    def __update_ftp_readme(self):
        if self.is_pre_release():
            info_skipped("Skipping README update (this is only a pre-release)")
            return

        tmp_dir = self.cfg["setup.tmp_dir"]
        new_README_filename = os.path.join(tmp_dir, "README")
        tarballs_remote_url = self.__tarballs_remote_url()

        subst = dict(self.cfg.data)
        subst["today_utc"] = datetime.utcnow().strftime("%B %d, %Y")
        for ext in ("xz", "gz"):
            tarball = os.path.join(
                tmp_dir, "%s.%s" % (self.cfg["release.tarball"], ext)
            )
            subst["%s_size" % ext] = file_size_in_MiB(tarball)

        readme_contents = NEW_FTP_README % subst
        with open(new_README_filename, "w") as fd:
            fd.write(readme_contents)

        query(
            NEW_README_QUERY
            % {
                "readme_contents": indent(readme_contents, "| "),
                "tarballs_remote_url": tarballs_remote_url,
            }
        )

        status = call(
            ["scp", new_README_filename, tarballs_remote_url],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=STDOUT,
        )
        if status != 0:
            raise FatalError(
                "Failed to scp ftp README to sourceware host"
                " (error code: %d)." % status
            )

    def __tarballs_remote_url(self):
        return "%(uid)s@%(host)s:%(dir)s" % {
            "uid": self.cfg["sourceware.gdbadmin_uid"],
            "host": self.cfg["sourceware.hostname"],
            "dir": self.cfg.ftp_tarball_dir,
        }
