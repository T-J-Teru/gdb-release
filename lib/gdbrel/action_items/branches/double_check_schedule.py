from gdbrel.utils import query
from gdbrel.action_items.branches import AbstractBranchCreationAI

AI_BLURB = """\
Please visit the following URL and check the schedule:

    https://www.sourceware.org/gdb/schedule/

If you need to make a change, you can make it via the htdocs repository:

  1. Clone the ${hl_sbu}htdocs${hl_ebu} repository from\
 ssh://sourceware.org/git/gdb-htdocs.git

  2. cd htdocs

  3. Edit schedule/index.html

  4. Update last-modified date:

       % ./index.sh schedule/index.html

  5. Commit and then push your change

       % git commit schedule/index.html
       % git push origin main

The deployment to the live GDB website is done automatically.
"""


class AI(AbstractBranchCreationAI):
    @property
    def name(self):
        return "double-check schedule on web"

    def do_AI(self):
        query(AI_BLURB)
