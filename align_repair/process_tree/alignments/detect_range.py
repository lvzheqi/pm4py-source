import copy

from pm4py.objects.log.log import Trace, EventLog
from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.objects.process_tree import util as pt_utils

from align_repair.process_tree.alignments import utils as pt_align_utils
from align_repair.process_tree.manipulation import pt_number, pt_compare
from align_repair.evaluation import create_event_log, alignment_on_pt, alignment_on_loop_lock_pt, alignment_default_on_pt
from align_repair.process_tree.alignments.align_repair_opt import align_repair, apply_pt_alignments


class RangeInterval(object):
    def __init__(self, lower_bound, upper_bound):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def is_in_range(self, number):
        return True if self.lower_bound <= number <= self.upper_bound else False

    def __repr__(self):
        return '[' + str(self.lower_bound) + ', ' + str(self.upper_bound) + ']'


class TreeInfo(object):
    def __init__(self, tree, paths, tree_range):
        self.tree = tree
        self.paths = paths
        self.tree_range = tree_range

    def __repr__(self):
        return str(self.tree) + ', ' + str(self.paths) + ', ' + str(self.tree_range) + '\n'


def init_index_table(node, index_t):
    index_t[node.index] = node


def init_mapping_table(node, mapping_t):
    if node.label is not None:
        mapping_t[node.label] = node.index


def init_label_table(node, label_t):
    label_t[node.index] = [node.index]
    parent = node.parent
    while parent is not None:
        label_t[node.index] += [parent.index]
        parent = parent.parent


def init_tree_tables(tree):
    mapping_t, label_t = dict(), dict()
    q = [tree]
    while len(q) != 0:
        node = q.pop(0)

        init_mapping_table(node, mapping_t)
        init_label_table(node, label_t)

        for i in range(len(node.children)):
            q.append(node.children[i])
    return mapping_t, label_t


def recursively_init_tree_tables(tree, tree_info, mapping_t, paths):
    max_index = 0
    init_mapping_table(tree, mapping_t)

    if tree.operator is None:
        max_index = tree.index

    for child in tree.children:
        max_index = max(
            recursively_init_tree_tables(child, tree_info, mapping_t, paths + [child.index]),
            max_index)

    tree_info[tree.index] = TreeInfo(tree, paths, RangeInterval(tree.index, max_index))
    return max_index


def move_move(align, cur_pos, index):
    """
    Pop the align-move at position cur_pos and insert into position index

    Parameters
    ------------
    align
        alignment
    cur_pos
        current position
    index
        the position that will be insert after pop
    """
    move = align.pop(cur_pos)
    align.insert(index, move)


def find_left_bound(range_interval, align, node_index, tree_info, mapping_t, neighbors_ranges):
    left_bound = cur_pos = range_interval.lower_bound
    while True:
        if cur_pos > range_interval.upper_bound:
            return -1
        move = align[cur_pos]
        if not pt_align_utils.is_log_move(move, True):
            if pt_align_utils.move_in_subtree(move, tree_info[node_index].tree_range, mapping_t):
                break
            move_in_left_neighbors = neighbors_ranges.is_in_range(pt_align_utils.move_index(move, mapping_t, True))
            if pt_align_utils.is_sync_move(move, True) and move_in_left_neighbors:
                left_bound = cur_pos + 1
            elif pt_align_utils.is_model_move(move, True) and move_in_left_neighbors:
                if cur_pos != left_bound:
                    move_move(align, cur_pos, left_bound)
                left_bound += 1
        cur_pos += 1
    return left_bound


def find_right_bound(range_interval, align, node_index, tree_info, mapping_t, neighbors_ranges):
    right_bound = cur_pos = range_interval.upper_bound
    while True:
        if cur_pos < range_interval.lower_bound:
            return -1
        move = align[cur_pos]
        if not pt_align_utils.is_log_move(move, True):
            if pt_align_utils.move_in_subtree(move, tree_info[node_index].tree_range, mapping_t):
                break
            move_in_right_neighbors = neighbors_ranges.is_in_range(pt_align_utils.move_index(move, mapping_t, True))

            if pt_align_utils.is_sync_move(move, True) and move_in_right_neighbors:
                right_bound = cur_pos - 1
            elif pt_align_utils.is_model_move(move, True) and move_in_right_neighbors:
                if cur_pos != right_bound:
                    move_move(align, cur_pos, right_bound)
                right_bound -= 1
        cur_pos -= 1
    return right_bound


def compute_ranges_for_loop(align, tree_info, mapping_t, node_index, ranges):
    parent_node_index = tree_info[node_index].tree.parent.index
    if node_index == parent_node_index + 1:
        ub = tree_info[parent_node_index].tree_range.upper_bound
        nei_ranges = RangeInterval(tree_info[node_index].tree_range.upper_bound + 1, ub)
    else:
        lb = tree_info[parent_node_index].tree_range.lower_bound
        nei_ranges = RangeInterval(lb, tree_info[node_index].tree_range.lower_bound - 1)

    new_ranges = list()
    for range_interval in ranges:
        ri = compute_one_range_for_sequence(align, tree_info, mapping_t, node_index, range_interval,
                                            nei_ranges, nei_ranges)
        if ri is not None:
            left_bound = cur_pos = ri.lower_bound
            scatter_align = False
            while cur_pos <= ri.upper_bound:
                move = align[cur_pos]
                move_in_nei = True
                if not pt_align_utils.is_log_move(move, True):
                    move_cur_index = pt_align_utils.move_index(move, mapping_t, True)
                    move_in_nei = nei_ranges.is_in_range(move_cur_index)
                    scatter_align = True if move_in_nei else scatter_align
                    if scatter_align and pt_align_utils.move_in_subtree(move, tree_info[node_index].tree_range,
                                                                        mapping_t):
                        new_ranges.append(compute_one_range_for_sequence(align, tree_info, mapping_t, node_index,
                                                                         RangeInterval(left_bound, cur_pos - 1),
                                                                         nei_ranges, nei_ranges))
                        ri = compute_one_range_for_sequence(align, tree_info, mapping_t, node_index,
                                                            RangeInterval(cur_pos, ri.upper_bound),
                                                            nei_ranges, nei_ranges)
                        if ri is None:
                            break
                        left_bound = cur_pos = ri.lower_bound
                        scatter_align = False
                if (pt_align_utils.is_sync_move(move, True) and move_in_nei) or cur_pos == ri.upper_bound:
                    new_ranges.append(compute_one_range_for_sequence(align, tree_info, mapping_t, node_index,
                                                                     RangeInterval(left_bound, cur_pos),
                                                                     nei_ranges, nei_ranges))
                    ri = compute_one_range_for_sequence(align, tree_info, mapping_t, node_index,
                                                        RangeInterval(cur_pos + 1, ri.upper_bound),
                                                        nei_ranges, nei_ranges)
                    if ri is None:
                        break
                    left_bound = cur_pos = ri.lower_bound
                    scatter_align = False
                cur_pos += 1
    return new_ranges


def compute_one_range_for_sequence(align, tree_info, mapping_t, node_index, range_interval, left_nei, right_nei):
    left_bound = find_left_bound(range_interval, align, node_index, tree_info, mapping_t, left_nei)
    if left_bound == -1:
        return None
    right_bound = find_right_bound(range_interval, align, node_index, tree_info, mapping_t, right_nei)
    return RangeInterval(left_bound, right_bound)


def compute_ranges_for_xor(align, tree_info, mapping_t, node_index, ranges):
    return compute_ranges_for_sequence(align, tree_info, mapping_t, node_index, ranges)


def compute_ranges_for_sequence(align, tree_info, mapping_t, node_index, ranges):
    lb, ub = tree_info[node_index].tree.parent.index, tree_info[node_index].tree_range.lower_bound - 1
    left_nei = RangeInterval(lb, ub)
    lb = tree_info[node_index].tree_range.upper_bound + 1
    ub = tree_info[tree_info[node_index].tree.parent.index].tree_range.upper_bound
    right_nei = RangeInterval(lb, ub)
    new_ranges = list()
    for ri in ranges:
        new_range = compute_one_range_for_sequence(align, tree_info, mapping_t, node_index, ri, left_nei, right_nei)
        if new_range is not None:
            new_ranges.append(new_range)
    return new_ranges


def compute_repairing_alignments(com_res, log, alignments, tree_info, mapping_t, parameters, best_worst_cost):
    alignments = copy.deepcopy(alignments)
    for i, alignment in enumerate(alignments):
        align = alignment['alignment']
        if alignment.get("repair") is None:
            ranges = list()
            for node_index in tree_info[com_res.subtree1.index].paths:
                node = tree_info[node_index].tree
                if node_index == 1:
                    ranges = [RangeInterval(0, len(align) - 1)]
                elif node.parent.operator == Operator.LOOP:
                    ranges = compute_ranges_for_loop(align, tree_info, mapping_t, node.index, ranges)
                elif node.parent.operator == Operator.SEQUENCE:
                    ranges = compute_ranges_for_sequence(align, tree_info, mapping_t, node.index, ranges)
                elif node.parent.operator == Operator.XOR:
                    ranges = compute_ranges_for_xor(align, tree_info, mapping_t, node.index, ranges)

            if len(ranges) != 0:
                align_repair(alignment, log, ranges, mapping_t, com_res, tree_info[com_res.subtree1.index].tree_range,
                             parameters, best_worst_cost)
            alignment["repair"] = True
    for a in alignments:
        a.pop("repair") if a.get("repair") is not None else None
    return alignments


def apply(tree, m_tree, log, parameters=None):
    pt_number.apply(tree, 'D')
    pt_number.apply(m_tree, 'D')
    alignments = alignment_on_pt(tree, log)
    com_res = pt_compare.apply(tree, m_tree, 1)
    if com_res.value:
        return alignments, copy.deepcopy(alignments)
    else:
        mapping_t, tree_info = dict(), dict()
        recursively_init_tree_tables(tree, tree_info, mapping_t, [1])
        best_worst_cost = apply_pt_alignments(EventLog([Trace()]), m_tree, parameters)[0]['cost']
        repairing_alignment = compute_repairing_alignments(com_res, log, alignments, tree_info, mapping_t,
                                                           parameters, best_worst_cost)

        # opt_align = alignment_on_pt(m_tree, log)
        # print(list(map(lambda a: a[1], opt_align[0]['alignment'])))
        # print('opt_cost:', opt_align[0]['cost'])
        # print(list(map(lambda a: a[1], repairing_alignment[0]['alignment'])))
        # print('rep_cost:', repairing_alignment[0]['cost'])
        return alignments, repairing_alignment


if __name__ == "__main__":
    tree1 = pt_utils.parse("X( +( j, k, a ), *( X( b, +( h, i ) ), *( X( c, d ), ->( +( f, g ), e ), τ ), τ ) )")
    tree2 = pt_utils.parse("X( +( j, k, a ), *( X( b, +( h, i ) ), *( X( c, d ), ->( *( f, g, τ ), e ), τ ), τ ) )")
    logs = create_event_log("bn, mj, bcni, hncmf, h, ffjn, i, kj, fkn, lchbdf")

    alignments = alignment_default_on_pt(tree2, logs)
    optimal_cost = sum([align['cost'] for align in alignments])
    # print(list(map(lambda a: a[1], alignments[0]['alignment'])))
    print('optimal cost', optimal_cost)
    alignments = alignment_on_loop_lock_pt(tree2, logs)
    # print(list(map(lambda a: a[1], alignments[0]['alignment'])))
    print('optimal cost', optimal_cost)
    print(alignments)
    # apply(tree1, tree2, logs)
