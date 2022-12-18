#! /usr/bin/env python3
"""List all GDB bugs fixed in a given release.

This script takes a version number as input, and generates a list of
bugs markes as FIXED with that milestone.  This list can be generated
either in text format (the default) or in HTML format.
"""

import argparse
from os.path import abspath, dirname
import sys


def parse_args(argv=None):
    """Parse the command-line and return the arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--html",
        action="store_true",
        default=False,
        help=("Dump the list of bugs in HTML format"),
    )
    parser.add_argument("version", help=("The GDB release version to look up"))
    return parser.parse_args(argv)


def main(argv=None):
    """The main subprogram."""
    args = parse_args(argv)

    ROOT_DIR = dirname(abspath(__file__))
    LIB_DIR = "%s/%s" % (ROOT_DIR, "lib")
    sys.path.insert(0, LIB_DIR)

    from gdbrel.bugzilla import DumpFormat, dump_fixed_bugs
    from gdbrel.config import Config

    cfg = Config(ROOT_DIR)
    fmt = DumpFormat.HTML if args.html else DumpFormat.TEXT
    dump_fixed_bugs(cfg, args.version, fmt)


if __name__ == "__main__":
    main()
