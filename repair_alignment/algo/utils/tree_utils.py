from pm4py.objects.process_tree.pt_operator import Operator


class RangeInterval(object):
    def __init__(self, lower_bound, upper_bound):
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

    def is_in_range(self, number):
        return True if self._lower_bound <= number <= self._upper_bound else False

    def __repr__(self):
        return '[' + str(self._lower_bound) + ', ' + str(self._upper_bound) + ']'

    def _set_lower_bound(self, lower_bound):
        self._lower_bound = lower_bound

    def _set_upper_bound(self, upper_bound):
        self._upper_bound = upper_bound

    def _get_lower_bound(self):
        return self._lower_bound

    def _get_upper_bound(self):
        return self._upper_bound

    lower_bound = property(_get_lower_bound, _set_lower_bound)
    upper_bound = property(_get_upper_bound, _set_upper_bound)


class TreeInfo(object):
    def __init__(self, tree, paths, tree_range):
        self._tree = tree
        self._paths = paths
        self._tree_range = tree_range

    def __repr__(self):
        return str(self._tree) + ', ' + str(self._paths) + ', ' + str(self._tree_range) + '\n'

    def _set_tree(self, tree):
        self._tree = tree

    def _set_paths(self, paths):
        self._paths = paths

    def _set_tree_range(self, tree_range):
        self._tree_range = tree_range

    def _get_tree(self):
        return self._tree

    def _get_paths(self):
        return self._paths

    def _get_tree_range(self):
        return self._tree_range

    tree = property(_get_tree, _set_tree)
    paths = property(_get_paths, _set_paths)
    tree_range = property(_get_tree_range, _set_tree_range)


def recursively_init_tree_tables(tree, tree_info, mapping_t, paths):
    max_index = 0

    if tree.label is not None:
        mapping_t[tree.label] = tree.index

    if tree.operator is None:
        max_index = tree.index

    for child in tree.children:
        max_index = max(
            recursively_init_tree_tables(child, tree_info, mapping_t, paths + [child.index]),
            max_index)

    tree_info[tree.index] = TreeInfo(tree, paths, RangeInterval(tree.index, max_index))
    return max_index


def detect_stop_condition(subtree1, tree_info):
    node = subtree1
    while node.parent is not None:
        if node.parent.operator == Operator.LOOP:
            ri_parent = tree_info[node.parent.index].tree_range
            ri_node = tree_info[node.index].tree_range
            return [RangeInterval(ri_parent.lower_bound, ri_node.lower_bound - 1),
                    RangeInterval(ri_node.upper_bound + 1, ri_parent.upper_bound)]
        node = node.parent
    return [RangeInterval(0, -1), RangeInterval(0, -1)]
