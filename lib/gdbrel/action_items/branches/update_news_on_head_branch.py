from gdbrel.action_items.branches import AbstractBranchCreationAI
from gdbrel.utils import trace

NEW_NEWS_SECTION = """\
*** Changes since GDB %(branch_version)s

*** Changes in GDB %(branch_version)s
"""

NEWS_COMMIT_REV_LOG = """\
Update gdb/NEWS after GDB %(branch_version)s branch creation.

This commit a new section for the next release branch, and renames
the section of the current branch, now that it has been cut.
"""

NEWS_COMMIT_REVIEW_INSNS = """\
Please review this change to the NEWS file on branch \
${hl_sbu}%(branch_name)s${hl_ebu}

Because we use a commit in the past to create a branch, ${hl_warn}some of
the NEWS entries may have to be moved out of this section into the section
just above${no_hl}. To check this, just double-check what the NEWS file
documents on the branch. This commit makes the bet that the branchpoint
is sufficiently close in time that no update will be necessary.

If the commit needs to be adjusted, the adjustment needs to be performed
by hand. Here is how to do it:

${hl_warn}\
    %% cd %(sandbox_dir)s
    %% vi %(filename)s
    %% git commit --amend -v %(filename)s
${no_hl}\

Once that's done, very that the commit is now correct:

${hl_warn}\
    %% git show
${no_hl}\

And if satisfied, press [Enter] as prompted below to continue the release
process.
"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return "NEWS update on head branch"

    def do_AI(self):
        NEWS_FILENAME = "gdb/NEWS"
        subst_info = {
            "filename": NEWS_FILENAME,
            "branch_name": self.release_branch,
            "branch_version": self.cfg["release.branch-version"],
            "sandbox_dir": self.sandbox.path,
        }

        trace(
            "Updating %(filename)s in branch ${hl_sbu}"
            "%(branch_name)s${hl_ebu}..." % subst_info
        )

        self.sandbox.checkout(self.head_branch)

        # Update the NEWS file, hoping that the branch point is not
        # too far back that some entries entered in the current
        # version are past the branchpoint.  That's a fairly safe
        # bet and, should we have a problem, we will tell the user
        # how to handle the situation by hand.
        with self.sandbox.open(NEWS_FILENAME) as f:
            old = f.readlines()
        with self.sandbox.open(NEWS_FILENAME, "w") as f:
            for old_line in old:
                if old_line.startswith("*** Changes since GDB"):
                    f.write(NEW_NEWS_SECTION % subst_info)
                else:
                    f.write(old_line)

        # Commit the change.
        rev_log = NEWS_COMMIT_REV_LOG % subst_info
        review_insns = NEWS_COMMIT_REVIEW_INSNS % subst_info
        self.commit(self.head_branch, NEWS_FILENAME, rev_log, review_insns)
