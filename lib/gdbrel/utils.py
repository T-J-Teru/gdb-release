import os
import re
from string import Template
import sys

# Various terminal sequences to enable certain colors.  The colors
# are mapped to a given type of text.
HL_MAP = {'hl_info': '\033[36m',    # Info messages (cyan)
          'hl_q': '\033[32m',       # Questions/See-me (green)
          'hl_warn': '\033[33m',    # Warning (yellow)
          'hl_err': '\033[31m',     # Error (red)
          'hl_sbu': '\033[1;4m',    # Start bold+underline
          'hl_ebu': '\033[21;24m',  # End bold+underline
          'no_hl': '\033[0m',       # End of highlighting.
          }


def apply_highlighting(s):
    return Template(s).safe_substitute(HL_MAP)


def hl_print(hl_type, s, out=sys.stdout, new_line=True):
    if hl_type is not None:
        s = '${%s}%s${no_hl}' % (hl_type, s)
    out.write(apply_highlighting(s))
    if new_line:
        out.write('\n')
    out.flush()


def _inform(indent='', hl_type=None, *args):
    assert len(args) > 0
    # Handle the case where a single multi-list string is passed.
    if len(args) == 1:
        args = args[0].splitlines()

    hl_print(hl_type, indent + args[0])
    for arg in args[1:]:
        print(' ' * len(indent) + apply_highlighting(arg))


def trace(*args):
    _inform('--- ', None, *args)


def info(*args):
    _inform('+++ ', 'hl_info', *args)


def info_skipped(*args):
    _inform('... ', 'hl_info', *args)


def query(*args):
    _inform('!!! ', 'hl_q', *args)
    press_enter_or_control_c()


def warn(*args):
    _inform('??? ', 'hl_warn', *args)
    press_enter_or_control_c()


def error(*args):
    assert len(args) > 0
    # Print a new-line, since we might not be at the start of a line...
    print()
    for arg in args:
        hl_print('hl_err', '*** ' + arg)
    sys.exit(1)


def press_enter_or_control_c():
    try:
        hl_print(
            'hl_q', '??? Press [Enter] to continue or [Ctrl-C] to abort:',
            new_line=False)
        sys.stdin.readline()
    except KeyboardInterrupt:
        error('Aborting due to explicit keyboard interrupt (Ctrl-c)')


def indent(s, indenter):
    return '\n'.join([indenter + line for line in s.splitlines()])


def get_changelog_entries(rev_log):
    cl_prog = re.compile(r'(\S*\bChangeLog):\S*$', re.IGNORECASE)
    result = {}
    current_cl_text = None
    for line in rev_log.splitlines():
        m = cl_prog.match(line)
        if m is not None:
            # Start of a new ChangeLog entry...
            current_cl_text = []
            result[m.group(1)] = current_cl_text
        elif line and not line[0:1].isspace():
            # Line does not start with whitespace. It cannot be part
            # of a ChangeLog entry.  So close the current_cl_text.
            current_cl_text = None
        elif current_cl_text is not None:
            # Do not add empty lines before the start of the CL text.
            if line.strip() or current_cl_text:
                current_cl_text.append(line)

    # Remove all empty lines at the end of each ChangeLog entry.
    for (_, cl_text) in result.items():
        while cl_text and (not cl_text[-1] or cl_text[-1].isspace()):
            cl_text.pop()

    return result


def is_pre_release(version_str):
    """Return True if VERSION_STR corresponds to a pre-release version number.

    Pre-release version numbers typically have the micro version number
    in the .90s, whereas release version numbers usually have no micro
    version number at all, or one that is very small. We chose the cut-off
    to be .50 - that gives us 49 releases before we have to fix this
    function...
    """
    version_info = version_str.split('.')
    if len(version_info) < 3:
        # No micro version number, definitely a real release...
        return False
    micro = int(version_info[2])
    return micro >= 50


def file_size_in_MiB(filename):
    """Return the size of a file in MiB.

    The size returned is an integer number of MiB, rounded UP. This seems
    to mimick the behavior of "ls -lh" on GNU/Linux systems.
    """
    one_MiB = 1048576
    # To get the "round up" behavior, we use the trick of adding
    # the (divisior -1) to the dividend...
    return (os.path.getsize(filename) + (one_MiB - 1)) // one_MiB
