from gdbrel.action_items import AbstractAction


class AI(AbstractAction):
    @property
    def name(self):
        return "fetch-and-rebase head branch"

    def do_AI(self):
        self.sandbox.fetch_and_rebase(self.head_branch)
