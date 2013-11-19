from gdbrel.action_items import AbstractAI
from gdbrel.utils import is_pre_release


class AbstractReleaseCreationAI(AbstractAI):
    @property
    def category_name(self):
        return ('gdb-%s-release' % self.release_version
                if self.release_version is not None
                else None)

    @property
    def release_version(self):
        return (self.cfg['release.do_release']
                if 'release.do_release' in self.cfg
                else None)

    def is_pre_release(self):
        version_str = self.release_version
        assert version_str is not None
        return is_pre_release(version_str)
