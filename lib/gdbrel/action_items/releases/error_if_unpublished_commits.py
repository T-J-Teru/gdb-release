from gdbrel.action_items import AbstractAction
from gdbrel.errors import FatalError
from gdbrel.utils import trace

INTERNAL_ERROR_MSG = """\
Internal Error: On branch ${hl_sbu}%(branch_name)s${hl_ebu}
The following commits have not been pushed:
%(commit_list)s
"""


class AI(AbstractAction):
    @property
    def name(self):
        return "check all local commits have been published"

    def do_AI(self):
        self.__check_branch(self.release_branch)
        self.__check_branch(self.head_branch)

    def __check_branch(self, branch_name):
        trace("Checking %s..." % branch_name)
        unpushed = self.git.log(
            "origin/%(branch)s..%(branch)s" % {"branch": branch_name},
            oneline=True,
            color=True,
        )
        if unpushed:
            raise FatalError(
                INTERNAL_ERROR_MSG
                % {
                    "branch_name": branch_name,
                    "commit_list": unpushed,
                }
            )
