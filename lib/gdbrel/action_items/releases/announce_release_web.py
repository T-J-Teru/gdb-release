from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import query, info_skipped

from string import Template


QUERY_BLURB = """\
Please post the creation of the release on the website:

 1. Checkout the ${hl_sbu}htdocs${hl_ebu} repository from\
 ${hl_sbu}Git${hl_ebu}:
    sourceware.org/git/gdb-htdocs.git

 2. cd htdocs

 3. Update ${hl_sbu}download/ANNOUNCEMENT${hl_ebu}

    Remember to provide the gitweb URL to the gdb/NEWS file corresponding
    to our release:

        ${hl_sbu}${hl_warn}https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;a=blob_plain;f=gdb/NEWS;hb=${tag}${no_hl}

 4. Update ${hl_sbu}download/index.html${hl_ebu}
    (just update the version number of the latest release)

 5. Edit ${hl_sbu}news/index.html${hl_ebu}
    (use previous annoucements as template)

 6. Edit ${hl_sbu}index.html${hl_ebu}:
     6.1.  Update latest release version number
           (the links themselves are fine).
     6.2.  Copy new NEWS entry from news/index.html.
           ${hl_warn}(remember to fix the ${hl_sbu}"../download"${hl_ebu} link to just ${hl_sbu}"download"${hl_ebu})${no_hl}

 7. Update last-modified dates:
    % ./index.sh download/index.html news/index.html index.html

 8. Verify the modifications you just made:
    % git diff download/ANNOUNCEMENT download/index.html\
 news/index.html index.html

 9. Commit the changes:
    % git commit download/ANNOUNCEMENT download/index.html news/index.html\
 index.html

10. Push the changes to the upstream repository

    Note: No need worry about www.gnu.org/software/gdb, which is managed
    via savannah, anymore.  There is a redirect from this website to
    the one hosted on sourceware.org.
"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return "announce release on web"

    def do_AI(self):
        if self.is_pre_release():
            info_skipped("This is a pre-release, skipping...")
            return

        query(Template(QUERY_BLURB).safe_substitute(tag=self.cfg["release.tag"]))
