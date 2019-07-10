from pm4py.objects.process_tree.pt_operator import Operator

from repair_alignment.algo.utils import align_utils
from repair_alignment.algo.utils.tree_utils import RangeInterval


def find_left_bound(range_interval, align, node_index, tree_info, mapping_t):
    left_bound = range_interval.lower_bound
    tree_range = tree_info[node_index].tree_range
    while True:
        if left_bound > range_interval.upper_bound:
            return -1
        move = align[left_bound]
        if not align_utils.is_log_move(move, True):
            model_index = align_utils.move_index(move, mapping_t, True)
            if tree_range.is_in_range(model_index):
                break
        left_bound += 1
    return left_bound


def find_right_bound(range_interval, align, node_index, tree_info, mapping_t):
    right_bound = cur_index = range_interval.upper_bound
    tree_range = tree_info[node_index].tree_range
    while True:
        if cur_index < range_interval.lower_bound:
            return -1
        move = align[cur_index]
        if not align_utils.is_log_move(move, True):
            model_index = align_utils.move_index(move, mapping_t, True)
            if tree_range.is_in_range(model_index):
                break
            else:
                right_bound = cur_index - 1
        cur_index -= 1
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
        ri = compute_one_range_for_sequence(align, tree_info, mapping_t, node_index, range_interval)
        if ri is not None:
            cur_pos = left_bound = ri.lower_bound
            while cur_pos <= ri.upper_bound:
                move = align[cur_pos]
                if not align_utils.is_log_move(move, True):
                    move_cur_index = align_utils.move_index(move, mapping_t, True)
                    move_in_nei = nei_ranges.is_in_range(move_cur_index)
                else:
                    move_in_nei = False
                if move_in_nei or cur_pos == ri.upper_bound:
                    new_ranges.append(compute_one_range_for_sequence(align, tree_info, mapping_t, node_index,
                                                                     RangeInterval(left_bound, cur_pos)))
                    ri = compute_one_range_for_sequence(align, tree_info, mapping_t, node_index,
                                                        RangeInterval(cur_pos + 1, ri.upper_bound))
                    if ri is None:
                        break
                    elif ri.upper_bound == ri.lower_bound:
                        new_ranges.append(RangeInterval(ri.lower_bound, ri.upper_bound))
                    left_bound = cur_pos = ri.lower_bound
                cur_pos += 1
    return new_ranges


def compute_one_range_for_sequence(align, tree_info, mapping_t, node_index, range_interval):
    left_bound = find_left_bound(range_interval, align, node_index, tree_info, mapping_t)
    if left_bound == -1:
        return None
    right_bound = find_right_bound(range_interval, align, node_index, tree_info, mapping_t)
    return RangeInterval(left_bound, right_bound)


def compute_ranges_for_xor_parallel(align, tree_info, mapping_t, node_index, ranges):
    return compute_ranges_for_sequence(align, tree_info, mapping_t, node_index, ranges)


def compute_ranges_for_sequence(align, tree_info, mapping_t, node_index, ranges):
    new_ranges = list()
    for ri in ranges:
        new_range = compute_one_range_for_sequence(align, tree_info, mapping_t, node_index, ri)
        if new_range is not None:
            new_ranges.append(new_range)
    return new_ranges


def remove_first_log_move(align):
    left_bound = 0
    while True:
        move = align[left_bound]
        if not align_utils.is_log_move(move, True):
            break
        left_bound += 1
    return [RangeInterval(left_bound, len(align) - 1)]


def apply(align, tree_info, mapping_t, com_res):
    ranges = list()
    for node_index in tree_info[com_res.subtree1.index].paths:
        node = tree_info[node_index].tree
        if node.parent is None:
            ranges = remove_first_log_move(align)
        elif node.parent.operator == Operator.LOOP:
            ranges = compute_ranges_for_loop(align, tree_info, mapping_t, node.index, ranges)
        elif node.parent.operator == Operator.SEQUENCE:
            ranges = compute_ranges_for_sequence(align, tree_info, mapping_t, node.index, ranges)
        elif node.parent.operator == Operator.XOR or node.parent.operator == Operator.PARALLEL:
            ranges = compute_ranges_for_xor_parallel(align, tree_info, mapping_t, node.index, ranges)
    return ranges
