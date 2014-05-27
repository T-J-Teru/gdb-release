from gdbrel.action_items.releases import AbstractReleaseCreationAI
from gdbrel.ex import run
from gdbrel.utils import query, trace

import os

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

    def __unpack_tarball(self):
        tmp_dir = self.cfg['setup.tmp_dir']
        tar_out = os.path.join(tmp_dir, 'untar.out')
        xz_tarball = self.cfg['release.xz_tarball']
        trace('unpacking %(release.xz_tarball)s...' % self.cfg)
        run('unpack %s' % xz_tarball,
            ['tar', 'xfJ', xz_tarball],
            cwd=tmp_dir, stdout=tar_out)

    def __configure_gdb(self):
        tmp_dir = self.cfg['setup.tmp_dir']
        gdb_dir = os.path.join(tmp_dir, 'gdb-%s' % self.cfg.release_version)
        prefix = os.path.join(gdb_dir, 'install')
        configure_out = os.path.join(tmp_dir, 'configure.out')
        trace('configuring GDB...',
              'tip: tail -f %s' % configure_out)
        run('configure GDB',
            ['./configure', '--prefix=%s' % prefix, 'CFLAGS=-g'],
            cwd=gdb_dir, stdout=configure_out)

    def __build_gdb(self):
        tmp_dir = self.cfg['setup.tmp_dir']
        gdb_dir = os.path.join(tmp_dir, 'gdb-%s' % self.cfg.release_version)
        build_out = os.path.join(tmp_dir, 'build.out')
        trace('building GDB...',
              'tip: tail -f %s' % build_out)
        run('build GDB', ['make', '-j6'],
            cwd=gdb_dir, stdout=build_out)

    def __install_gdb(self):
        tmp_dir = self.cfg['setup.tmp_dir']
        gdb_dir = os.path.join(tmp_dir, 'gdb-%s' % self.cfg.release_version)
        install_out = os.path.join(tmp_dir, 'install.out')
        trace('installing GDB...',
              'tip: tail -f %s' % install_out)
        run('install GDB', ['make', '-C', 'gdb', 'install'],
            cwd=gdb_dir, stdout=install_out)
