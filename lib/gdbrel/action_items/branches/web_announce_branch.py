from gdbrel.utils import query
from gdbrel.action_items.branches import AbstractBranchCreationAI

AI_BLURB = """\
Please post the creation of the branch on the website:

  1. Clone the ${hl_sbu}htdocs${hl_ebu} repository from\
 ssh://sourceware.org/git/gdb-htdocs.git

  2. cd htdocs

  3. Edit news/index.html (use previous annoucements as template)

  4. Copy the new entry to index.html

  5. Update last-modified dates:

         % ./index.sh news/index.html index.html

  6. Verify the modifications you just made:

         % git diff -up news/index.html index.html

  7. Commit the changes:

         % git ci news/index.html index.html

  8. Push the change
     (this will automatically deploy the change to the GDB website
     hosted on sourceware.org)

         % git push origin main


Note: The GDB website hosted at www.gnu.org/software/gdb is managed via
      savannah. That website is a simple redirect to the website on
      sourceware.org, so there is no need to do anything to update
      the gnu.org side.
"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return "new branch web announcement"

    def do_AI(self):
        query(AI_BLURB)
