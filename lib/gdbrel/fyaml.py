from gdbrel.errors import FatalError

import yaml
import re


class FlatYaml(object):
    VAR_MATCHER = re.compile(r'\${([^}]+)}')

    def __init__(self, yaml_filename, env):
        self.yaml_filename = yaml_filename
        self.flattened = dict(env)
        with open(yaml_filename) as f:
            self.root_tree = yaml.safe_load(f)
        self.__flatten(self.root_tree, None)
        for k in self.flattened.keys():
            self.__resolve(k)

    def __flatten(self, subtree, parent_tree_name):
        if isinstance(subtree, basestring):
            self.flattened[parent_tree_name] = subtree
        else:
            # At the moment, we do not need to support collections...
            assert isinstance(subtree, dict)
            for k, v in subtree.iteritems():
                self.__flatten(v, self.__tree_name(parent_tree_name, k))

    def __resolve(self, key):
        if key not in self.flattened.keys():
            raise FatalError(
                'Invalid variable name in %s: %s' % (self.yaml_filename, key))

        while True:
            value = self.flattened[key]
            m = self.__class__.VAR_MATCHER.search(value)
            if m is None:
                return  # Done!

            sub_var_name = m.group(1)
            self.__resolve(sub_var_name)
            self.flattened[key] = (value[:m.start()]
                                   + self.flattened[sub_var_name]
                                   + value[m.end():])

    def __tree_name(self, parent_tree_name, subtree_name):
        if parent_tree_name is None:
            prefix = ''
        else:
            prefix = '%s.' % parent_tree_name
        return prefix + subtree_name
