#! /usr/bin/env python

from os.path import abspath, dirname
import sys


def main():
    ROOT_DIR = dirname(abspath(__file__))
    LIB_DIR = '%s/%s' % (ROOT_DIR, 'lib')
    sys.path.insert(0, LIB_DIR)

    import gdbrel
    from gdbrel.errors import FatalError
    try:
        gdbrel.do_release(ROOT_DIR)
    except FatalError, E:
        from gdbrel.utils import error
        error(str(E))
        sys.exit(1)


if __name__ == '__main__':
    main()
