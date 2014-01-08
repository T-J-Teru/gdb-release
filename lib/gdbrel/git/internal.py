"""Utility code for calling git commands.

Derived in a very large part from the gnome git hooks, themselves
apparently adapted form git-bz.

Original copyright header:

| Copyright (C) 2008  Owen Taylor
| Copyright (C) 2009  Red Hat, Inc
|
| This program is free software; you can redistribute it and/or
| modify it under the terms of the GNU General Public License
| as published by the Free Software Foundation; either version 2
| of the License, or (at your option) any later version.
|
| This program is distributed in the hope that it will be useful,
| but WITHOUT ANY WARRANTY; without even the implied warranty of
| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
| GNU General Public License for more details.
|
| You should have received a copy of the GNU General Public License
| along with this program; if not, If not, see
| http://www.gnu.org/licenses/.
|
| (These are adapted from git-bz)
"""

from subprocess import CalledProcessError, Popen, PIPE, STDOUT


def git_run(command, *args, **kwargs):
    """Run a git command.

    PARAMETERS
        Non-keyword arguments are passed verbatim as command line arguments
        Keyword arguments are turned into command line options
           <name>=True => --<name>
           <name>='<str>' => --<name>=<str>
        Special keyword arguments:
           _input=<str>: Feed <str> to stdinin of the command
           _outfile=<file): Use <file> as the output file descriptor
           _cwd=<str>: Directory name from which to run the command.
           _split_lines: Return an array with one string per returned line
    """
    to_run = ['git', command.replace("_", "-")]

    input = None
    outfile = None
    do_split_lines = False
    cwd = None
    for (k, v) in kwargs.iteritems():
        if k == '_input':
            input = v
        elif k == '_outfile':
            outfile = v
        elif k == '_cwd':
            cwd = v
        elif k == '_split_lines':
            do_split_lines = True
        elif v is True:
            if len(k) == 1:
                to_run.append("-" + k)
            else:
                to_run.append("--" + k.replace("_", "-"))
        elif v is False:
            # Ignore this argument.
            pass
        else:
            to_run.append("--" + k.replace("_", "-") + "=" + v)

    to_run.extend(args)

    stdout = outfile if outfile else PIPE
    stdin = None if input is None else PIPE

    process = Popen(to_run, stdout=stdout, stderr=STDOUT, stdin=stdin,
                    cwd=cwd)
    output, error = process.communicate(input)
    # We redirected stderr to the same fd as stdout, so error should
    # not contain anything.
    assert not error

    if process.returncode != 0:
        raise CalledProcessError(process.returncode,
                                 " ".join(to_run),
                                 output)

    if outfile:
        return None
    else:
        if do_split_lines:
            return output.strip().splitlines()
        else:
            return output.strip()


class Git:
    """Wrapper to allow us to do git.<command>(...) instead of git_run()

    One difference: The `_outfile' parameter may be a string, in which
    case the output is redirected to that file (if the file is already
    present, it is overwritten).
    """
    def __init__(self, sandbox_dir=None):
        self.sandbox_dir = sandbox_dir

    def __getattr__(self, command):
        def f(*args, **kwargs):
            try:
                # If a string _outfile parameter was given, turn it
                # into a file descriptor.
                tmp_fd = None
                if (('_outfile' in kwargs
                     and isinstance(kwargs['_outfile'], basestring))):
                    tmp_fd = open(kwargs['_outfile'], 'w')
                    kwargs['_outfile'] = tmp_fd
                if '_cwd' not in kwargs:
                    kwargs['_cwd'] = self.sandbox_dir
                return git_run(command, *args, **kwargs)
            finally:
                if tmp_fd is not None:
                    tmp_fd.close()
        return f
