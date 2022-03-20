from gdbrel.errors import FatalError
from gdbrel.utils import (info, info_skipped, query, trace, indent,
                          get_changelog_entries)

from datetime import datetime
import os
import re
import sys

PATCH_REVIEW_BLURB = """\
The following patch has been checked in branch %(branch_name)s:

%(commit_info)s

%(review_insns)s
"""

PATCH_REVIEW_DEFAULT_INSNS = """\
Please review the commit above (on branch\
 ${hl_sbu}%(branch_name)s${hl_ebu}), and press
[Ctrl-c] if not correct.
"""


class AbstractAI(object):
    def __init__(self, cfg, cklist, sandbox):
        self.cfg = cfg
        self.cklist = cklist
        self.sandbox = sandbox
        self.__ensure_hasattr('category_name')
        self.__ensure_hasattr('name')
        if ((self.do_AI_once_only
             and self.cklist.is_done(self.category_name, self.name))):
            info_skipped(*self.skip_info_msg())
            return
        elif self.is_elementary_action_item:
            info('Starting Action Item: %s...' % self.name)
        self.do_AI()
        if self.do_AI_once_only:
            self.cklist.set_done(self.category_name, self.name)

    def __ensure_hasattr(self, attr_name):
        if not hasattr(self, attr_name):
            raise FatalError(
                'Internal Error: %s.%s attribute not defined by class'
                % (self.__class__.__name__, attr_name))

    @property
    def is_elementary_action_item(self):
        # By default, we are an elementary AI (ie, we don't run AIs
        # as part of our do_AI method implementation).
        return True

    @property
    def do_AI_once_only(self):
        # By default, once an AI is done, don't do it again (Eg: Once
        # a change has been made, no need to redo it the next we run
        # this script).  However, so AIs are necessary each time we
        # run the script - for instance, updating the sandbox to
        # the latest.  Set this property to False if the AI needs to
        # be run every time.
        return True

    def skip_info_msg(self):
        return ('Skipping Action Item: %s (already done)' % self.name, )

    def do_AI(self):
        raise FatalError('Internal Error: %s.do_AI method not implemented'
                         % self.__class__.__name__)

    ######################################
    # Git-related convenience methods... #
    ######################################

    @property
    def git(self):
        return self.sandbox.git

    @property
    def release_branch(self):
        return self.cfg['release.branch_name']

    @property
    def head_branch(self):
        return self.cfg['gdb_repo.head_branch']

    def add_changelog_entry(self, cl_filename, cl_text):
        with self.sandbox.open(cl_filename) as f:
            old_cl_lines = f.readlines()
        with self.sandbox.open(cl_filename, 'w') as f:
            f.write("""\
%(iso_date)s  %(name)s  <%(email)s>

%(cl_text)s

"""
                    % {'iso_date': datetime.utcnow().date().isoformat(),
                       'name': self.cfg['rel_manager.name'],
                       'email': self.cfg['rel_manager.email'],
                       'cl_text': '\n'.join(cl_text)})
            f.writelines(old_cl_lines)

    def commit(self, branch_name, files, rev_log, review_insns=None):
        # If checking in a single file, it is acceptable to pass it
        # directly, rather than embedding it in an iterable.  Just
        # turn into to a single-element tuple instead.
        if isinstance(files, str):
            files = (files, )
        if review_insns is None:
            review_insns = (
                PATCH_REVIEW_DEFAULT_INSNS % {'branch_name': branch_name})

        current_branch = self.sandbox.get_current_branch()
        if branch_name != current_branch:
            raise FatalError(
                'Checkin attempt on wrong branch (%(current)s'
                ' - expected %(expected)s.'
                % {'current': current_branch,
                   'expected': branch_name},
                'Aborting.')

        trace('Checking in the following files '
              ' (on branch: ${hl_sbu}%s${hl_ebu}):'
              % current_branch,
              *('  - %s' % filename for filename in files))
        print()

        # First, "git add" all files to be checked in.
        for f in files:
            self.git.add(f)

        # Next, extract ChangeLog entries from the revision log.
        # Starting with GDB 12, it's possible that ChangeLog entries
        # might not be included anymore (requirement now dropped
        # for GDB and binutils). We still keep support for them,
        # for directories where ChangeLog files are still in use.
        cl_entries = get_changelog_entries(rev_log)

        # Add those entries to the corresponding ChangeLog files,
        # and then "git add" them.
        for (cl_filename, cl_text) in cl_entries.items():
            self.add_changelog_entry(cl_filename=cl_filename,
                                     cl_text=cl_text)
            self.git.add(cl_filename)

        # Commit the change with the given revision log.
        self.git.commit(message=rev_log)

        # And finally, confirm with the user that the commit is correct.
        commit_info = self.git.show(color=True)
        query(PATCH_REVIEW_BLURB
              % {'branch_name': current_branch,
                 'commit_info': indent(commit_info, '| '),
                 'review_insns': review_insns,
                 })

    def email_changes(self, branch_name, subject):
        rev_list = 'origin/%(branch)s..%(branch)s' % {'branch': branch_name}
        subject_prefix = (
            'release/%s' % ('branch' if branch_name == self.release_branch
                            else 'HEAD'))

        n_revs = len(self.git.rev_list(rev_list).splitlines())
        self.git.send_email(
            rev_list,
            annotate=True, compose=(n_revs > 1),
            subject=subject,
            subject_prefix=subject_prefix,
            to=self.cfg['gdb_repo.email.patches'],
            # Cc the release manager as well, in case he is
            # on GMail, where emails sent and received back
            # are not shown unless explicitly listed in
            # the recipients' list.
            cc=f"{self.cfg['rel_manager.name']} <{self.cfg['rel_manager.email']}",
            confirm='always',
            no_chain_reply_to=True,
            _outfile=sys.stdout,
        )

    ##############################################
    # Other miscellaneous convenience methods... #
    ##############################################

    def update_gdb_version_in_default_exp(self, var_name, new_version):
        GDB_TESTSUITE_DIR = os.path.join('gdb', 'testsuite')
        DEFAULT_EXP_REL_FILENAME = os.path.join('gdb.base', 'default.exp')
        DEFAULT_EXP_FILENAME = os.path.join(
            GDB_TESTSUITE_DIR, DEFAULT_EXP_REL_FILENAME)

        # A regular expression, which matches the part of the default.exp
        # testcase where the expected value for the variable whose value
        # we are trying to change is provided.
        VER_RE = (
            # Start of line...
            r"^"
            # Everything up to the name of var we are changing (incl.)...
            r"(?P<lhs>.*\${var_name})"
            # The assignment operator...
            r"(?P<eq>\s*=\s*)"
            # The version number...
            r"(?P<rhs>\d+)"
            # Everything else afterwards, up to...
            r"(?P<after_rhs>\D*)"
            # ... the end of line...
            "$"
        ).format(var_name=var_name)

        # A replacement string for the region matched by VER_RE.
        VER_REPL = r"\g<lhs>\g<eq>{new_version}\g<after_rhs>".format(
            new_version=new_version)

        with self.sandbox.open(DEFAULT_EXP_FILENAME) as f:
            default_exp = f.read()

        new_default_exp = re.sub(
            VER_RE, VER_REPL, default_exp, flags=re.MULTILINE)

        # Make sure that the substitution resulted in an actual change;
        # otherwise, something unexpected must have happened.

        if new_default_exp == default_exp:
            err_msg = (
                "%s update failed: Substitution did not result in any change:",
                f"  - var_name: {var_name}",
                f"  - new_version: {new_version}",
                f"  - VER_RE: {VER_RE}",
                f"  - VER_REPL: {VER_REPL}",
                "Aborting.",
            )
            raise FatalError("\n".join(err_msg))

        with self.sandbox.open(DEFAULT_EXP_FILENAME, "w") as f:
            f.write(new_default_exp)

        # Return the file we just updated (relative to the root of
        # the repository, and the corresponding CL entry.
        return (
            DEFAULT_EXP_FILENAME,
            f"\t* {DEFAULT_EXP_REL_FILENAME}: Change ${var_name} to {new_version}.\n"
        )


class AbstractAction(AbstractAI):
    """An action we need to do potentially more than once...

    ... regardless of whether we've done it before or not.
    Eg: Update a branch in our sandbox, for instance.
    """
    @property
    def category_name(self):
        return 'undefined'

    @property
    def do_AI_once_only(self):
        return False
