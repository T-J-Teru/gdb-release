from gdbrel.action_items.branches import AbstractBranchCreationAI
from gdbrel.utils import HL_MAP, error, query

import re

BUGZILLA_UPDATE_REQUEST = """\
Add a new target milestone in Bugzilla

Please visit the following Bugzilla administration page:

    {hl_info}{edit_milestones_url}{no_hl}

You you see a list of target milestone versions.

Scroll to the very bottom of the page, and click on the "Add a version"
link to add the following Target Milestone version:

    {hl_info}{new_target_milestone_version}{no_hl}

This will allow users to specify that a given PR should
should be fixed for this version of GDB.
"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return "bugzilla: Add target milestone after release branching"

    def do_AI(self):
        VERSION_IN_FILENAME = "gdb/version.in"

        # Get the current major version number on the HEAD branch...
        self.sandbox.checkout(self.head_branch)
        with self.sandbox.open(VERSION_IN_FILENAME) as f:
            version_str = f.readline()
        m = re.match(r"(?P<major>\d+)(?P<rest>\..*)", version_str)
        if m is None:
            error(
                f"Unable to parse version number in {version_str}"
                f" ({VERSION_IN_FILENAME})."
            )

        new_target_milestone_version = f"{m.group('major')}.1"

        # Ask the user to add the Target Milestone.
        query(
            BUGZILLA_UPDATE_REQUEST.format(
                edit_milestones_url=self.cfg["bugzilla.edit_milestones_url"],
                new_target_milestone_version=new_target_milestone_version,
                hl_info=HL_MAP["hl_info"],
                no_hl=HL_MAP["no_hl"],
            )
        )
