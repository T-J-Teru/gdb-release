from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.errors import FatalError
from gdbrel.utils import trace

import os
import shutil
from subprocess import call, STDOUT
import sys

DELETED_FILES_ERROR = """\
The following files have been deleted during the tar-ball creation process
(make -f src-release). This is not expected and needs to be fixed.

The deleted files:
%(deleted_files)s:
"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return "create tarballs"

    def do_AI(self):
        self.__checkout_release_commit()
        # The checkout above also ensures that our sandbox is completely
        # clean - no local modifications or untracked files.  So we can
        # create our tarballs without fear of parasite files creeping in.
        self.__create_tarballs()
        self.__ensure_no_deleted_files()
        self.__compress_tarballs()
        # The release process also causes a number of files to be
        # created.  Keep our sandbox clean, and delete those.
        self.sandbox.delete_untracked_files()

    def __checkout_release_commit(self):
        trace("Computing the commit to use for the release...")
        if self.is_pre_release():
            # No tag as a reference for the commit to use as our
            # pre-release. Just use the tip of the release branch.
            release_rev = self.release_branch
        else:
            # Use the release tag, to make extra-sure we use the commit
            # that was tagged for the release.
            release_rev = self.cfg["release.tag"]
        self.sandbox.checkout(release_rev)

    def __create_tarballs(self):
        MAKE_TAR_OUT = "%(setup.tmp_dir)s/make_tar.out" % self.cfg
        if os.path.exists(os.path.join(self.sandbox.path, "src-release.sh")):
            # This is the latest way of creating the release tarball,
            # where the "src-release" Makefile has been converted to
            # the "src-release.sh" script.
            trace(
                'running "./src-release.sh gdb"...', "tip: %% tail -f %s" % MAKE_TAR_OUT
            )
            with open(MAKE_TAR_OUT, "w") as out_fd:
                status = call(
                    "./src-release.sh gdb".split(),
                    cwd=self.sandbox.path,
                    stdout=out_fd,
                    stderr=STDOUT,
                )
        else:
            # Old-style way of creating the release tarball, based on
            # the "src-release" Makefile.  Used up to the GDB 7.8 branch.
            trace(
                'running "make -f src-release"...', "tip: %% tail -f %s" % MAKE_TAR_OUT
            )
            with open(MAKE_TAR_OUT, "w") as out_fd:
                status = call(
                    "make -f src-release gdb.tar".split(),
                    cwd=self.sandbox.path,
                    stdout=out_fd,
                    stderr=STDOUT,
                )
        if status != 0:
            raise FatalError(
                "Tarball creation failed (return %d). Aborting." % status,
                "Check %s for more details." % MAKE_TAR_OUT,
            )
        # Move the tarball to the tmp_dir...
        tarball_name = self.cfg.release_tarball
        trace(
            "Tarball created (%s), moving it to the tmp directory..." % tarball_name,
            "(%s)" % self.cfg["setup.tmp_dir"],
        )
        shutil.move(
            os.path.join(self.sandbox.path, tarball_name),
            os.path.join(self.cfg["setup.tmp_dir"], tarball_name),
        )

    def __ensure_no_deleted_files(self):
        # Verify that the release process did not delete any file from
        # the controlled tree (save for .git/ directory).
        deleted = self.git.ls_files("-d").splitlines()
        if deleted:
            deleted_str = "\n".join(["  - %s" % df for df in deleted])
            raise FatalError(DELETED_FILES_ERROR % {"deleted_files": deleted_str})

    def __compress_tarballs(self):
        src = os.path.join(self.cfg["setup.tmp_dir"], self.cfg.release_tarball)
        for zip_tool in ("xz", "gzip"):
            dst = os.path.join(
                self.cfg["setup.tmp_dir"], self.cfg["release.%s_tarball" % zip_tool]
            )
            trace("Creating %s..." % dst)
            with open(dst, "w") as out_fd:
                status = call(
                    [zip_tool, "-v", "-9", "-c", src], stdout=out_fd, stderr=sys.stderr
                )
                if status != 0:
                    raise FatalError("Failed to recreate %s archive!" % zip_tool)
