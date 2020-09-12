from gdbrel.errors import FatalError
from subprocess import call, STDOUT


def run(title, cmd, stdin=None, stdout=None, stderr=STDOUT,
        cwd=None, env=None, must_succeed=True):
    """A wrapper around subprocess.call.

    Returns the command's return code.

    Small differences:
        - TITLE is just a title for the command, which this routine
          uses to print messages such as error messages.
        - STDOUT can be a filename, as opposed to an open file
          descriptor. When a filename is provided, this routine
          will use it to create a temporary file descriptor.
          Also, any error message will also mention that file.
        - MUST_SUCCEED: If True, raise FatalError if the command
          failed, instead of returning the command's return code.
    """
    out_filename = None
    if isinstance(stdout, str):
        out_filename = stdout
        stdout = open(out_filename, 'w')

    status = call(cmd, stdin=stdin, stdout=stdout, stderr=stderr,
                  cwd=cwd, env=env)

    if out_filename is not None:
        stdout.close()

    if must_succeed and status != 0:
        err_msg = 'Failed to %s (error code: %d)' % (title, status)
        if out_filename is not None:
            err_msg += ('\nSee ${hl_sbu}%s${hl_ebu} for more details.'
                        % out_filename)
        raise FatalError(err_msg)

    return status
