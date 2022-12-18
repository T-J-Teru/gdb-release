from gdbrel.utils import query, trace, indent
from gdbrel.action_items.branches import AbstractBranchCreationAI

import sys

BLURB = """\
About to create branchpoint tag: ${hl_sbu}%(tag_name)s${hl_ebu}...

... from the following commit ${hl_q}%(sha1)s${no_hl}:

%(commit_info)s

"""

COMMIT_INFO_FORMAT = """\
| Author: %an <%ae>
| Date: %ad
| Subject: %s
"""

TAG_REV_LOG = """\
%(branch_name)s branchpoint
"""

VERIFY_TAG_QUERY = """\
We are about to push the following tag.  Please verify that everything
is correct.


%(tag_info)s

Should we go ahead and push that tag to the official repository?

"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return "branchpoint tag creation"

    def do_AI(self):
        # Ask confirmation that we're branching on the right commit.
        commit_info = self.git.show(
            self.cfg["release.branchpoint"],
            pretty="format:" + COMMIT_INFO_FORMAT,
            quiet=True,
        )
        subst = {
            "tag_name": self.branchpoint_tag_name,
            "sha1": self.cfg["release.branchpoint"],
            "commit_info": commit_info,
        }
        query(BLURB % subst)

        # Create the tag...
        trace("Creating new tag now (${hl_sbu}%(tag_name)s${hl_ebu})..." % subst)
        self.git.tag(
            self.branchpoint_tag_name,
            self.cfg["release.branchpoint"],
            sign=True,
            message=TAG_REV_LOG % {"branch_name": self.cfg["release.branch_name"]},
        )

        # Now that the tag has been created, let's be extra paranoid
        # and ask the user to double-check the tag before continuing
        # further (the --stat is there to avoid the "diff")
        tag_info = self.git.show(self.branchpoint_tag_name, stat=True, color=True)
        subst["tag_info"] = indent(tag_info, "| ")
        query(VERIFY_TAG_QUERY % subst)
        trace("Pushing new tag (${hl_sbu}%(tag_name)s${hl_ebu}) to remote..." % subst)
        self.git.push("origin", self.branchpoint_tag_name, _outfile=sys.stdout)
