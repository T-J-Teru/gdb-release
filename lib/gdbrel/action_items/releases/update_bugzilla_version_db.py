from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import HL_MAP, error, query, info_skipped

import re

BUGZILLA_UPDATE_REQUEST = """\
Add new versions in Bugzilla

  1. Please visit the following Bugzilla administration page:

        {hl_info}{edit_release_version_url}{no_hl}

     You should see a list of GDB release versions. Use the link
     at the bottom of that page to add the newly created release
     version:

        {hl_info}{new_release_version}{no_hl}

     This will allow users to that a problem being reported affects
     the release we just created.

  2. {hl_warn}IF (and only iff) we are planning for a corrective\
 release in the future:{no_hl}

     Please visit the following Bugzilla administration page:

        {hl_info}{edit_milestones_url}{no_hl}

     You should see a list of target milestone versions.

     Scroll to the very bottom of the page, and click on the "Add a version"
     link to add the following Target Milestone version:

        {hl_info}{new_target_milestone_version}{no_hl}

     This will allow users to specify that a given PR should be fixed
     for this version of GDB.
"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return "bugzilla: Add new versions after release"

    def do_AI(self):
        if self.is_pre_release():
            info_skipped("This is a pre-release, skipping...")
            return

        # Extract the major and minor portions of the release version.
        m = re.match(r"(?P<major>.+)\.(?P<minor>\d+)", self.release_version)
        if m is None:
            error(f"Unable to parse version number `{self.release_version}'")

        # Compute the version number of the next corrective release.
        new_target_milestone_version = "{major}.{minor}".format(
            major=m.group("major"), minor=int(m.group("minor")) + 1
        )

        # Ask the user to update the various version fields in bugzilla.
        query(
            BUGZILLA_UPDATE_REQUEST.format(
                edit_release_version_url=self.cfg["bugzilla.edit_version_url"],
                new_release_version=self.release_version,
                edit_milestones_url=self.cfg["bugzilla.edit_milestones_url"],
                new_target_milestone_version=new_target_milestone_version,
                hl_info=HL_MAP["hl_info"],
                hl_warn=HL_MAP["hl_warn"],
                no_hl=HL_MAP["no_hl"],
            )
        )
