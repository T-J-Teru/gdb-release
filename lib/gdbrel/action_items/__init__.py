from gdbrel.errors import FatalError
from gdbrel.utils import (info, info_skipped, query, trace, indent,
                          get_changelog_entries)

from datetime import datetime
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
        print

        # First, "git add" all files to be checked in.
        for f in files:
            self.git.add(f)

        # Next, extract ChangeLog entries from the revision log.
        # We expect at least one entry.  Otherwise, something is
        # seriously wrong.
        cl_entries = get_changelog_entries(rev_log)
        assert cl_entries

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
        self.git.send_email(rev_list,
                            annotate=True, compose=(n_revs > 1),
                            subject=subject,
                            subject_prefix=subject_prefix,
                            to=self.cfg['gdb_repo.email.patches'],
                            confirm='always',
                            no_chain_reply_to=True,
                            _outfile=sys.stdout)


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
