"""
apply to add other locks to alignment that is with only loop locks
"""
from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.objects.process_tree.process_tree import ProcessTree
from repair_alignment.algo.utils.align_utils import LOCK_START, LOCK_END


class RangeInterval(object):
    def __init__(self, lower_bound, upper_bound):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def is_in_range(self, number):
        return True if self.lower_bound <= number <= self.upper_bound else False

    def __repr__(self):
        return '[' + str(self.lower_bound) + ', ' + str(self.upper_bound) + ']'


def init_index_table(node, index_t):
    index_t[node.index] = node


def init_mapping_table(node, mapping_t):
    if (node.parent is not None and node.parent.operator == Operator.LOOP) \
            or (node.label is None and node.operator is None):
        mapping_t[str(node.index) + LOCK_START] = node.index
        mapping_t[str(node.index) + LOCK_END] = node.index
    if node.label is not None:
        mapping_t[node.label] = node.index


def init_label_table(node, label_t):
    label_t[node.index] = [node.index]
    parent = node.parent
    while parent is not None:
        label_t[node.index] += [parent.index]
        parent = parent.parent


def init_tree_tables(tree: ProcessTree, index_t, mapping_t, label_t):
    q = list()
    q.append(tree)
    while len(q) != 0:
        node = q.pop(0)

        init_index_table(node, index_t)
        init_mapping_table(node, mapping_t)
        init_label_table(node, label_t)

        for i in range(len(node.children)):
            q.append(node.children[i])


def init_align_inverse_table(alignment, loop_ts, inverse_ts, mapping_t, label_t):
    for align in alignment:
        loop_t, inverse_t = dict(), dict()
        for pos, (log_l, model_l) in enumerate(align['alignment']):
            if model_l is not None and model_l != '>>':
                node_index = mapping_t[model_l]
                if log_l == '>>' and (model_l.endswith(LOCK_END) or model_l.endswith(LOCK_START)):
                    loop_t[node_index] = [pos] if loop_t.get(node_index) is None else loop_t[node_index] + [pos]
                for node in label_t[node_index]:
                    inverse_t[node] = [pos] if inverse_t.get(node) is None else inverse_t[node] + [pos]
        loop_ts.append(loop_t)
        inverse_ts.append(inverse_t)


def add_lock(lock_list, range_interval, node_index):
    lock_list[range_interval.lower_bound] = [str(node_index) + LOCK_START] if lock_list.get(
        range_interval.lower_bound) is None else lock_list[range_interval.lower_bound] + [str(node_index) + LOCK_START]

    lock_list[range_interval.upper_bound + 1] = [str(node_index) + LOCK_END] if lock_list.get(
        range_interval.upper_bound + 1) is None else [str(node_index) + LOCK_END] + lock_list[
        range_interval.upper_bound + 1]


def compute_range(range_p, index_list, lock_list, node_index):
    ranges = {}
    for pos in index_list:
        for range_index in range(len(range_p)):
            if range_p[range_index].is_in_range(pos):
                ranges[range_index] = [pos] if ranges.get(range_index) is None else ranges[range_index] + [pos]
    ris = list()
    for i in ranges.values():
        i.sort()
        range_interval = RangeInterval(min(i), max(i))
        ris.append(range_interval)
        add_lock(lock_list, range_interval, node_index)
    return ris


def compute_lock_range(tree, alignments, locks):
    # total_node_number = pt_number.apply(tree, 'D')
    index_t, mapping_t, label_t = dict(), dict(), dict()
    loop_ts, inverse_ts, ranges = list(), list(), list()
    init_tree_tables(tree, index_t, mapping_t, label_t)
    init_align_inverse_table(alignments, loop_ts, inverse_ts, mapping_t, label_t)
    for i, inverse_t in enumerate(inverse_ts):
        range_t, lock_list = dict(), dict()
        for j in range(1, len(index_t) + 1):
            if inverse_t.get(j) is None:
                pass
            elif j == 1:
                ri = RangeInterval(0, len(alignments[i]['alignment']) - 1)
                range_t[j] = [ri]
                add_lock(lock_list, ri, j)
            elif index_t[j].parent is not None and index_t[j].parent.operator == Operator.LOOP:
                for k in range(len(loop_ts[i].get(j)) // 2):
                    ri = RangeInterval(loop_ts[i][j][2 * k], loop_ts[i][j][2 * k + 1])
                    range_t[j] = [ri] if range_t.get(j) is None else range_t[j] + [ri]
            else:
                range_t[j] = compute_range(range_t[index_t[j].parent.index], inverse_t[j], lock_list, j)
        ranges.append(range_t)
        locks.append(lock_list)
    return ranges


def insert_lock_to_alignment(alignments, locks):
    for i in range(len(alignments)):
        align = alignments[i]
        if align.get("lock") is None:
            for pos in range(len(align['alignment']), -1, -1):
                if locks[i].get(pos) is not None:
                    for j in range(len(locks[i][pos])-1, -1, -1):
                        align['alignment'].insert(pos, ('>>', locks[i][pos][j]))
            align["lock"] = True
    for a in alignments:
        a.pop("lock") if a.get("lock") is not None else None


def apply(tree, alignments):
    locks = list()
    compute_lock_range(tree, alignments, locks)
    insert_lock_to_alignment(alignments, locks)
