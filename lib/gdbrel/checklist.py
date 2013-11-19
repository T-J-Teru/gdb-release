from gdbrel.utils import info

import os
import yaml


class Checklist(object):
    def __init__(self, cfg):
        self.checklist_dir = cfg['setup.checklists_dir']
        self.filename = ('%s/gdb-%s.yaml'
                         % (self.checklist_dir,
                            cfg['release.branch-version']))
        if not os.path.isdir(self.checklist_dir):
            info('GDB checklists dir does not exist; creating...',
                 '(%s)' % self.checklist_dir)
            os.makedirs(self.checklist_dir)
        self.info = []
        if os.path.exists(self.filename):
            with open(self.filename) as f:
                self.info = yaml.load(f) or []

    def is_done(self, category, action_item):
        if category is None:
            # Special case: If there is no category, then there is no
            # work to be done. So return True.
            return True

        for cat_info in self.info:
            if category in cat_info:
                return (cat_info[category]
                        and action_item in cat_info[category])
        return False

    def set_done(self, category, action_item):
        for cat_info in self.info:
            if category in cat_info:
                if cat_info[category] is None:
                    # The category was created empty... Make it an empty
                    # list instead of None.
                    cat_info[category] = []
                assert action_item not in cat_info[category]
                cat_info[category].append(action_item)
                self.write()
                return
        # The category does not exist yet.  Create it...
        self.info.append({category: [action_item]})
        self.write()

    def write(self):
        with open(self.filename, 'w') as f:
            yaml.dump(self.info, f, default_flow_style=False)
