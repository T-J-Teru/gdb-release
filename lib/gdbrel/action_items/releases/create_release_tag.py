from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.errors import FatalError
from gdbrel.utils import trace, query, indent

NEW_TAG_QUERY = """\
Creating the release tag...

Please confirm the creation of the release tag, using the following
commit:

%(commit_info)s

This commit will be tagged as: ${hl_q}%(tag_name)s${no_hl}.

"""

TAG_REV_LOG = """\
GDB %(release.do_release)s Release.
"""

VERIFY_TAG_QUERY = """\
Please verify that we created the tag correctly.

Note that this tag will be pushed later on, after we've made the tarball;
this way, if anything happens during tarball creation, we can re-create
the tag, since that tag has not been publicly pushed yet.

%(tag_info)s

Is everything correct in this tag?


"""

UNPUSHED_CHANGES_ERROR = """\
The ${hl_sbu}%(release.branch_name)s${hl_ebu}\
in your sandbox has some commits that have not been
pushed to the official repository yet.  Since we are going to use
the tip of that branch as the release point, and therefore for
the release tag, we need to make sure that this commit has been
pushed to the official repository first.

Please investigate and fix...
"""

NO_TAG_FOR_PRE_RELEASES = """\
Skipping tag creation, This is only a pre-release\
 (${hl_sbu}%(release.do_release)s${hl_ebu})

"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return "create release tag"

    def do_AI(self):
        if self.is_pre_release():
            query(NO_TAG_FOR_PRE_RELEASES % self.cfg)
            return

        self.sandbox.fetch_and_rebase(self.release_branch)
        if self.sandbox.has_local_commits(self.release_branch):
            raise FatalError(UNPUSHED_CHANGES_ERROR % self.cfg)

        commit_info = self.git.log("-n1", self.release_branch)
        tag_name = self.cfg["release.tag"]
        subst = {
            "commit_info": indent(commit_info, "| "),
            "tag_name": tag_name,
        }

        # Create the tag after having asked the user to confirm that
        # we are we are going to use the correct commit to create it.
        query(NEW_TAG_QUERY % subst)
        trace("Creating new tag now (${hl_sbu}%(tag_name)s${hl_ebu})..." % subst)
        self.git.tag(
            tag_name, self.release_branch, sign=True, message=TAG_REV_LOG % self.cfg
        )

        # Now that the tag has been created, let's be extra paranoid
        # and ask the user to double-check the tag before continuing
        # further (the --stat is there to avoid the "diff")
        tag_info = self.git.show(tag_name, stat=True, color=True)
        subst["tag_info"] = indent(tag_info, "| ")
        query(VERIFY_TAG_QUERY % subst)
