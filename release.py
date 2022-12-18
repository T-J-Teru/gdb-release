#! /usr/bin/env python3

from os.path import abspath, dirname
from subprocess import CalledProcessError
import sys


def main():
    ROOT_DIR = dirname(abspath(__file__))
    LIB_DIR = "%s/%s" % (ROOT_DIR, "lib")
    sys.path.insert(0, LIB_DIR)

    # This variable gets set if an error gets detected, and is then
    # expected to contain an error message to be displayed to the user.
    err_msg = None

    import gdbrel
    from gdbrel.errors import FatalError
    from gdbrel.utils import error

    try:
        gdbrel.do_release(ROOT_DIR)
    except FatalError as e:
        err_msg = str(e)
    except CalledProcessError as e:
        err_msg = "\n".join(
            [
                f"The following command returned nonzero ({e.returncode}):",
                f"$ {e.cmd}",
            ]
        )
        if e.output is not None:
            err_msg += f"\n{e.output}"
        else:
            err_msg += "\n[command output sent to stdout just above]"

    if err_msg is not None:
        error(err_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
