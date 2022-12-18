from gdbrel.action_items import AbstractAI


class AbstractBranchCreationAI(AbstractAI):
    @property
    def category_name(self):
        return "branch-creation"
