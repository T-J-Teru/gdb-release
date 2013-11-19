from gdbrel.action_items import AbstractAction


class AI(AbstractAction):
    @property
    def name(self):
        return 'fetch-and-rebase release branch'

    def do_AI(self):
        # This creates the branch locally if necessary.
        self.sandbox.fetch_and_rebase(self.release_branch)
