from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import query

QUERY_BLURB = """\
Update the NEWS file if necessary:

1. On the ${hl_sbu}%(release.branch_name)s${hl_ebu} branch:

   Change the "Changes since GDB <version>" into "Changes in ...".

   The version number that should be used is the version number
   of the next official release. ${hl_warn}In the case of a pre-release,
   do ${hl_sbu}NOT${hl_ebu} use the pre-release version number!${no_hl}

   If this update has already been done during a previous pre-release
   process, then go to the next point without adjusting this file.

2. On the ${hl_sbu}%(gdb_repo.head_branch)s${hl_ebu} branch:

   If creating an official release, then the NEWS file in the head
   needs to be synchronized with the data that's provided in the branch.
   In particular:

     a. "*** Changes since ..." needs to be changed into "*** Changes
        in ..." as we would do on the branch.

     b. Create a new "*** Changes since ..." section for next branch.

     c. The content of the new "*** Changes in ..." section should
        match the contents of the same section on the branch.
        In other words, entries that might have added in this section
        after the branch was cut and didn't make it to the branch
        should be moved up in the new "*** Changes since ..." section.

3. Send an email to ${hl_sbu}gdb-patches${hl_ebu}

"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return "update gdb/NEWS"

    def do_AI(self):
        query(QUERY_BLURB % self.cfg)
