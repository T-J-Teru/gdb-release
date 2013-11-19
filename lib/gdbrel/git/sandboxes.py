from gdbrel.git.internal import Git, CalledProcessError
from gdbrel.errors import FatalError
from gdbrel.utils import trace, warn

import os
import sys


class GitSandbox(object):
    def __init__(self, sandbox_dir):
        self.path = sandbox_dir
        self.git = Git(self.path)

    def clone(self, url, *args, **kwargs):
        full_args = args + (url, self.path)
        # We cannot use self.git to create the clone, as this instance
        # would essentially try to cd to self.path before spawning
        # the underlying command.  But since we are trying to create
        # a clone at that location, the directory may not exist yet.
        # Use a temporary Git object instead.
        Git().clone(*full_args, **kwargs)

    def ensure_is_clean(self):
        status = self.git.status(short=True)
        if status:
            raise FatalError('The GDB sandbox seems to be dirty (with'
                             ' changes not checked in). Aborting.')

    def get_current_branch(self):
        return self.git.rev_parse('HEAD', abbrev_ref=True)

    def has_branch(self, branch_name):
        """Return True iff the branch exists in our sandbox.
        """
        try:
            self.git.show_ref('refs/heads/%s' % branch_name,
                              verify=True, quiet=True)
            return True
        except CalledProcessError:
            return False

    def branch(self, branch_name, start_point):
        self.git.branch(branch_name, start_point,
                        _outfile=sys.stdout)
        # Add a fetch line for that branch.  Otherwise, "git push"
        # will not update our associated ref in "refs/remotes".
        self.git.config('remote.origin.fetch',
                        '+refs/heads/%(branch_name)s:'
                        'refs/remotes/origin/%(branch_name)s'
                        % {'branch_name': branch_name},
                        add=True)

    def delete_untracked_files(self):
        untracked = self.git.ls_files('-o').splitlines()
        if untracked:
            warn('Deleting the following untracked files from your sandbox:',
                 *('  - %s' % filename for filename in untracked))
            for filename in untracked:
                os.remove(os.path.join(self.path, filename))

    def checkout(self, branch_name):
        self.ensure_is_clean()
        if branch_name != self.get_current_branch():
            trace('checking out branch %s...' % branch_name)
            self.git.checkout(branch_name)
        # While at it, also delete any untracked files...
        self.delete_untracked_files()

    def fetch_and_rebase(self, branch_name):
        trace('updating branch ${hl_sbu}%s${hl_ebu} in our sandbox...'
              % branch_name)
        self.ensure_is_clean()
        self.git.fetch('origin',
                       '+refs/heads/%(branch_name)s:'
                       'refs/remotes/origin/%(branch_name)s'
                       % {'branch_name': branch_name},
                       _outfile=sys.stdout)
        if not self.has_branch(branch_name):
            trace('branch %s does not exist in your sandbox.' % branch_name,
                  'Creating it now (pointing to origin/%s)...' % branch_name)
            start_point = 'origin/%s' % branch_name
            self.branch(branch_name, start_point)
            # Make this branch a tracking branch of the corresponding
            # branch on the remote.  Not strictly necessary, but enables
            # some convenient features.
            self.git.branch(branch_name, set_upstream_to=start_point)
        else:
            self.checkout(branch_name)
            self.git.rebase('origin/%s' % branch_name, _outfile=sys.stdout)

    def has_local_commits(self, branch_name):
        new_rev = self.git.rev_parse(branch_name)
        old_rev = self.git.rev_parse('origin/%s' % branch_name)
        return new_rev != old_rev

    def fullpath(self, rel_path):
        return os.path.join(self.sandbox_dir, rel_path)

    def open(self, filename, mode=None):
        args = [os.path.join(self.path, filename)]
        if mode is not None:
            args.append(mode)
        return open(*args)
