from gdbrel.fyaml import FlatYaml
from gdbrel.git import Git
from gdbrel.utils import is_pre_release

import os
import yaml

CONFIG_FILENAME = 'config.yaml'


class Config(object):
    def __init__(self, root_dir):
        config_filename = os.path.join(root_dir, CONFIG_FILENAME)
        initial_env = \
            {'root_dir': root_dir,
             'HOME': os.environ['HOME'],
             'rel_manager.name': Git().config('--global', 'user.name'),
             'rel_manager.email': Git().config('--global', 'user.email'),
             }
        self.data = FlatYaml(config_filename, initial_env).flattened

        # The release branch information: This information is loaded from
        # the setup.release_data_file, and for convenience of access,
        # we save the relevant info in self.data using "release." as
        # a namespace/prefix.
        with open(self['setup.release_data_file']) as f:
            def namespace(s):
                return 'release.%s' % s
            info = yaml.load(f)
            branch_name = info['current-branch']
            branch_info = info[branch_name]

            self.data[namespace('branch_name')] = info['current-branch']
            for k, v in branch_info.iteritems():
                self.data[namespace(k)] = v

        # Provide the release "kind" as "release.kind" in our config
        # object. That way, it is available in a dictionary form
        # if needed for string substitution.  MAY BE NONE.
        self.data['release.kind'] = self.__release_kind

        # Same for various other entities...
        self.data['release.tag'] = self.__release_tag
        self.data['release.tarball'] = self.release_tarball
        self.data['release.bzip2_tarball'] = self.release_bzip2_tarball
        self.data['release.gzip_tarball'] = self.release_gzip_tarball

        self.data['sourceware.ftp.branch_dir'] = self.ftp_branch_dir
        self.data['sourceware.ftp.release_dir'] = self.ftp_release_dir
        self.data['sourceware.ftp.tarball_dir'] = self.ftp_tarball_dir

    @ property
    def release_version(self):
        return (self.data['release.do_release']
                if 'release.do_release' in self.data
                else None)

    @property
    def __release_kind(self):
        if self.release_version is None:
            return None
        if is_pre_release(self.release_version):
            return 'pre-release'
        return 'release'

    @property
    def __release_tag(self):
        release_version = self.release_version
        if release_version is None:
            return None
        return 'gdb-%s-release' % release_version

    @property
    def release_tarball(self):
        release_version = self.release_version
        if release_version is None:
            return None
        return 'gdb-%s.tar' % release_version

    @property
    def release_bzip2_tarball(self):
        release_tarball = self.release_tarball
        if release_tarball is None:
            return None
        return release_tarball + '.bz2'

    @property
    def release_gzip_tarball(self):
        release_tarball = self.release_tarball
        if release_tarball is None:
            return None
        return release_tarball + '.gz'

    @property
    def ftp_branch_dir(self):
        return os.path.join(self.data['sourceware.ftp.root_dir'],
                            self.data['sourceware.ftp.branch_public_dir'])

    @property
    def ftp_release_dir(self):
        return os.path.join(self.data['sourceware.ftp.root_dir'],
                            self.data['sourceware.ftp.release_public_dir'])

    @property
    def ftp_tarball_dir(self):
        release_version = self.release_version
        if release_version is None:
            return None
        dir_key = ('branch_dir' if is_pre_release(release_version)
                   else 'release_dir')
        return self.data['sourceware.ftp.%s' % dir_key]

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, key):
        return key in self.data
