from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.utils import query, info_skipped

from string import Template


QUERY_BLURB = """\
Please post the creation of the release on the website:

 1. Checkout the ${hl_sbu}htdocs${hl_ebu} repository from\
 ${hl_sbu}CVS${hl_ebu}:
    sourceware.org:/cvs/gdb

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

 7. Update last-modified dates:
    % ./index.sh download/index.html news/index.html index.html

 8. Verify the modifications you just made:
    % cvs diff -up download/ANNOUNCEMENT download/index.html\
 news/index.html index.html | tee announce.diff

 9. Commit the changes:
    % cvs ci download/ANNOUNCEMENT download/index.html news/index.html\
 index.html

10. Resync the www.gnu.org/software/gdb copy.
    (done through savannah)

11. Send a commit email to gdb-patches with the associated patch.

"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return 'announce release on web'

    def do_AI(self):
        if self.is_pre_release():
            info_skipped('This is a pre-release, skipping...')
            return

        query(Template(QUERY_BLURB).safe_substitute(
            tag=self.cfg['release.tag']))
