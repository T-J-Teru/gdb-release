from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.errors import FatalError
from gdbrel.utils import query, info_skipped, info

import os
from subprocess import call, STDOUT
import sys

DIRECTIVE_FILE = """\
version: 1.2
directory: gdb
filename: %(tarball)s
"""

UPLOAD_INSNS = """\
Upload the tarballs on the gnu.org FTP server:

The general procedure for uploading files to ftp.gnu.org is described at:
https://www.gnu.org/prep/maintain/maintain.html#Automated-Upload-Procedure

More specifically, to upload this release, you will need to do
the following actions:

  1. Upload the following files on ftp-upload.gnu.org:

     %% cd %(setup.tmp_dir)s
     %% lftp ftp-upload.gnu.org/incoming/ftp
     ftp> put %(release.tarball)s.gz %(release.tarball)s.gz.sig\
 %(release.tarball)s.gz.directive.asc
     ftp> put %(release.tarball)s.xz %(release.tarball)s.xz.sig\
 %(release.tarball)s.xz.directive.asc

  2. Wait for 5-10 minutes to see if the upload was successful or not.
     The uploads are processed every 5 mins.

"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return "upload tarballs to gnu.org"

    def do_AI(self):
        if self.is_pre_release():
            info_skipped(
                "${hl_sbu}NOT${hl_ebu} uploading tarballs to" " the gnu.org FTP site",
                "(only full releases get uploaded there)",
            )
            return

        for tarball_ext in (".xz", ".gz"):
            self.__create_updload_files(tarball_ext)
        self.__upload_tarballs()

    def __create_updload_files(self, tarball_ext):
        tarball = self.cfg.release_tarball + tarball_ext
        signed_tarball = tarball + ".sig"
        directive_filename = tarball + ".directive"
        signed_directive = directive_filename + ".asc"
        tmp_dir = self.cfg["setup.tmp_dir"]

        # First, sign the tarball.
        info("Signing %s (into: ${hl_sbu}%s${hl_ebu})" % (tarball, signed_tarball))
        status = call(
            ["gpg", "-b", os.path.join(tmp_dir, tarball)],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=STDOUT,
        )
        if status != 0:
            raise FatalError("Signing of %s failed, aborting." % tarball)

        # Next, create a directive file...
        info(
            "Creating the directive file (${hl_sbu}%s${hl_ebu})..." % directive_filename
        )
        with open(os.path.join(tmp_dir, directive_filename), "w") as f:
            f.write(DIRECTIVE_FILE % {"tarball": tarball})

        # And now, clear-sign it...
        info(
            "Clear-signing the directive file"
            " (into: ${hl_sbu}%s${hl_ebu})..." % signed_directive
        )
        status = call(
            ["gpg", "--clearsign", os.path.join(tmp_dir, directive_filename)],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=STDOUT,
        )
        if status != 0:
            raise FatalError(
                "Clear-signing of %s faileed, aborting." % directive_filename
            )

    def __upload_tarballs(self):
        query(UPLOAD_INSNS % self.cfg)
