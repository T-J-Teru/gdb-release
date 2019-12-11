from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.ex import run
from gdbrel.utils import query, trace

import os
import shutil

QUERY_BLURB = """\
Please do a quick sanity-checking of the tarballs:

This basically consists in verifying that we can build the debugger
and that "break main; run" works. These scripts have already built
and installed the debugger, so all that is left to do is:

     %% ${hl_sbu}cd %(setup.tmp_dir)s/gdb-%(release.do_release)s${hl_ebu}
     %% ${hl_sbu}./gdb/gdb ./gdb/gdb${hl_ebu}
     [...]
     (gdb) ${hl_sbu}b main${hl_ebu}
     Breakpoint 1 at 0x80732bc: file main.c, line 734.
     (gdb) ${hl_sbu}run${hl_ebu}
     Starting program: /[...]/gdb

     Breakpoint 1, main (argc=1, argv=0xbffff8b4) at main.c:734
     734       catch_errors (captured_main, &args, "", RETURN_MASK_ALL);
     (gdb) ${hl_sbu}print args${hl_ebu}
     $1 = {argc = 136426532, argv = 0x821b7f0}
     (gdb)

"""


class AI(AbstractReleaseCreationAI):
    @property
    def name(self):
        return 'sanity check'

    def do_AI(self):
        # First, do as much of the sanity check as possible.
        self.__unpack_tarball()
        self.__configure_gdb()
        self.__build_gdb()
        self.__install_gdb()

        # And finally, as the user to do the rest.
        query(QUERY_BLURB % self.cfg)

    @property
    def __gdb_unpacked_dir(self):
        return os.path.join(self.cfg['setup.tmp_dir'],
                            'gdb-{}'.format(self.cfg.release_version))

    @property
    def __gdb_src_dir(self):
        return self.__gdb_unpacked_dir + '-src'

    @property
    def __gdb_bld_dir(self):
        return self.__gdb_unpacked_dir

    def __unpack_tarball(self):
        # If there are any directories with the same directory names
        # that we might be using, delete them now...
        for dir_name in (self.__gdb_unpacked_dir,
                         self.__gdb_src_dir,
                         self.__gdb_bld_dir):
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)

        tmp_dir = self.cfg['setup.tmp_dir']
        tar_out = os.path.join(tmp_dir, 'untar.out')
        xz_tarball = self.cfg['release.xz_tarball']
        trace('unpacking %(release.xz_tarball)s...' % self.cfg)
        run('unpack %s' % xz_tarball,
            ['tar', 'xfJ', xz_tarball],
            cwd=tmp_dir, stdout=tar_out)

        # Now, rename the unpacked directory into the src directory,
        # and create the build directory...
        os.rename(self.__gdb_unpacked_dir, self.__gdb_src_dir)
        os.mkdir(self.__gdb_bld_dir)

    def __configure_gdb(self):
        tmp_dir = self.cfg['setup.tmp_dir']
        prefix = os.path.join(self.__gdb_bld_dir, 'install')
        configure_out = os.path.join(tmp_dir, 'configure.out')
        trace('configuring GDB...',
              'tip: tail -f %s' % configure_out)
        run('configure GDB',
            [os.path.join(self.__gdb_src_dir, 'configure'),
             '--prefix=%s' % prefix, 'CFLAGS=-g', 'CXXFLAGS=-g'],
            cwd=self.__gdb_bld_dir, stdout=configure_out)

    def __build_gdb(self):
        tmp_dir = self.cfg['setup.tmp_dir']
        build_out = os.path.join(tmp_dir, 'build.out')
        trace('building GDB...',
              'tip: tail -f %s' % build_out)
        run('build GDB', ['make', '-j6'],
            cwd=self.__gdb_bld_dir, stdout=build_out)

    def __install_gdb(self):
        tmp_dir = self.cfg['setup.tmp_dir']
        install_out = os.path.join(tmp_dir, 'install.out')
        trace('installing GDB...',
              'tip: tail -f %s' % install_out)
        run('install GDB', ['make', '-C', 'gdb', 'install'],
            cwd=self.__gdb_bld_dir, stdout=install_out)
