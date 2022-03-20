from gdbrel.utils import query
from gdbrel.action_items.branches import AbstractBranchCreationAI

AI_BLURB = """\
Please post the creation of the branch on the website:

  1. Checkout the ${hl_sbu}htdocs${hl_ebu} repository from\
 sourceware.org:/cvs/gdb

  2. cd htdocs

  3. Edit news/index.html (use previous annoucements as template)

  4. Copy new entry to index.html

  5. Update last-modified dates:
     % ./index.sh news/index.html index.html

  6. Verify the modifications you just made:
     % cvs diff -up news/index.html index.html | tee announce.diff

  7. Commit the changes:
     % cvs ci news/index.html index.html
     (There will be a reminder later for the commit notification to be sent)

     Note: No need worry about www.gnu.org/software/gdb, which is managed
     via savannah, anymore.  There is a redirect from this website to
     the one hosted on sourceware.org.
"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return 'new branch web announcement'

    def do_AI(self):
        query(AI_BLURB)
