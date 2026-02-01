from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.action_items.update_release_branch import AI as update_release_branch
from gdbrel.action_items.update_head_branch import AI as update_head_branch
from gdbrel.action_items.releases.freeze_branch import AI as freeze_branch
from gdbrel.action_items.releases.update_news import AI as update_news
from gdbrel.action_items.releases.update_version_in import AI as update_version_in
from gdbrel.action_items.publish_all_commits import AI as publish_all_commits
from gdbrel.action_items.releases.create_release_tag import AI as create_release_tag
from gdbrel.action_items.releases.create_tarballs import AI as create_tarballs
from gdbrel.action_items.releases.unfreeze_branch import AI as unfreeze_branch
from gdbrel.action_items.releases.sanity_check import AI as sanity_check
from gdbrel.action_items.releases.push_release_tag import AI as push_release_tag
from gdbrel.action_items.releases.upload_to_sourceware import AI as upload_to_sourceware
from gdbrel.action_items.releases.upload_to_gnu import AI as upload_to_gnu
from gdbrel.action_items.releases.announce_release_web import AI as announce_release_web
from gdbrel.action_items.releases.update_online_docs import AI as update_online_docs
from gdbrel.action_items.releases.email_release_announcement import (
    AI as email_release_announcement,
)
from gdbrel.action_items.releases.update_schedule import AI as update_schedule
from gdbrel.action_items.releases.bump_version_on_branch import (
    AI as bump_version_on_branch,
)
from gdbrel.action_items.releases.error_if_unpublished_commits import (
    AI as error_if_unpublished_commits,
)
from gdbrel.action_items.releases.update_bugzilla_version_db import (
    AI as update_bugzilla_version_db,
)
from gdbrel.utils import info


HOWTO_MAKE_A_RELEASE = """\
No release to be created.

To create a pre-release or a release, edit the following file...

    %% vi %(setup.release_data_file)s

... and add the following line at the end of the ${hl_q}\
"%(release.branch_name)s:"${no_hl}
block:

    do_release: <version_number>

(where <version_number> is the (pre-)release version - Eg. 7.6.90, 7.7,
7.7.1, etc).

The scripts will automatically figure out, based on the version
number provided, whether this is just a pre-release, or whether
this is a full-on release.

"""

BLURB_AFTER_RELEASE_CREATION_DONE = """\
GDB %(release.do_release)s has now been officially released!

Congratulations, you are done!
"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return "ALL DONE!"

    @property
    def is_elementary_action_item(self):
        return False

    def skip_info_msg(self):
        return (HOWTO_MAKE_A_RELEASE % self.cfg).splitlines()

    def do_AI(self):
        info(
            "Starting Meta Action Item: Release Creation "
            " (version: ${hl_sbu}%(release.do_release)s${hl_ebu})..." % self.cfg
        )

        for AI in (
            freeze_branch,
            update_release_branch,
            update_head_branch,
            update_news,
            update_version_in,
            # We need to publish all commits now, in order to
            # make sure that the tag we are about to create
            # points to a commit that exists in the official
            # repository.
            publish_all_commits,
            create_release_tag,
            create_tarballs,
            sanity_check,
            # Now that we've completed our sanity check, it looks
            # like we are going ahead with our release. So make
            # associated commits and publish them now.  That way,
            # we reduce the chances of conflict with changes from
            # other contributors.
            push_release_tag,
            update_schedule,
            bump_version_on_branch,
            publish_all_commits,
            # We could have released the freezed right after we
            # had created the tarballs, but we are keeping it
            # until now, because we had some commits to make
            # after tarball creation, and holding it helps avoiding
            # potential conflicts.
            #
            # The reason we need to keep the freeze at least
            # until we have created the tarballs is the following:
            #
            # For pre-releases, we do not create a tag, so
            # we rely on the tip of the release branch instead.
            # We do not want an unexpected patch affecting
            # the release tarballs.
            unfreeze_branch,
            # The rest of the work should be paperwork...
            upload_to_sourceware,
            upload_to_gnu,
            announce_release_web,
            update_online_docs,
            email_release_announcement,
            update_bugzilla_version_db,
            # As stated above, everything we did since we last
            # called publish_all_commits should not involve any
            # commit in the GDB repository.  But just to be sure
            # we did not have bug in the scripts, double-check
            # that this is the case...
            error_if_unpublished_commits,
        ):
            AI(self.cfg, self.cklist, self.sandbox)

        info(BLURB_AFTER_RELEASE_CREATION_DONE % self.cfg)
