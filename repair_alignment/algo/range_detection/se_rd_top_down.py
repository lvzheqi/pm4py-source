from pm4py.objects.process_tree.pt_operator import Operator

from repair_alignment.algo.utils import align_utils
from repair_alignment.algo.utils.tree_utils import RangeInterval


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


def find_left_bound(range_interval, align, node_index, tree_info, mapping_t, neighbors_ranges, ret_tuple_as_trans_desc):
    left_bound = cur_pos = range_interval.lower_bound
    while True:
        if cur_pos > range_interval.upper_bound:
            return -1
        move = align[cur_pos]
        if not align_utils.is_log_move(move, ret_tuple_as_trans_desc):
            if align_utils.move_in_subtree(move, tree_info[node_index].tree_range, mapping_t):
                break
            move_in_left_neighbors = neighbors_ranges.is_in_range(
                align_utils.move_index(move, mapping_t, ret_tuple_as_trans_desc))
            if align_utils.is_sync_move(move, ret_tuple_as_trans_desc) and move_in_left_neighbors:
                left_bound = cur_pos + 1
            elif align_utils.is_model_move(move, ret_tuple_as_trans_desc) and move_in_left_neighbors:
                if cur_pos != left_bound:
                    move_move(align, cur_pos, left_bound)
                left_bound += 1
        cur_pos += 1
    return left_bound


def find_right_bound(range_interval, align, node_index, tree_info, mapping_t, neighbors_ranges,
                     ret_tuple_as_trans_desc):
    right_bound = cur_pos = range_interval.upper_bound
    while True:
        if cur_pos < range_interval.lower_bound:
            return -1
        move = align[cur_pos]
        if not align_utils.is_log_move(move, ret_tuple_as_trans_desc):
            if align_utils.move_in_subtree(move, tree_info[node_index].tree_range, mapping_t):
                break
            move_in_right_neighbors = neighbors_ranges.is_in_range(
                align_utils.move_index(move, mapping_t, ret_tuple_as_trans_desc))

            if align_utils.is_sync_move(move, ret_tuple_as_trans_desc) and move_in_right_neighbors:
                right_bound = cur_pos - 1
            elif align_utils.is_model_move(move, ret_tuple_as_trans_desc) and move_in_right_neighbors:
                if cur_pos != right_bound:
                    move_move(align, cur_pos, right_bound)
                right_bound -= 1
        cur_pos -= 1
    return right_bound


def compute_ranges_for_loop(align, tree_info, mapping_t, node_index, ranges, ret_tuple_as_trans_desc):
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
                                            nei_ranges, nei_ranges, ret_tuple_as_trans_desc)
        if ri is not None:
            left_bound = cur_pos = ri.lower_bound
            scatter_align = False
            while cur_pos <= ri.upper_bound:
                move = align[cur_pos]
                move_in_nei = True
                if not align_utils.is_log_move(move, ret_tuple_as_trans_desc):
                    move_cur_index = align_utils.move_index(move, mapping_t, ret_tuple_as_trans_desc)
                    move_in_nei = nei_ranges.is_in_range(move_cur_index)
                    scatter_align = True if move_in_nei else scatter_align
                    if scatter_align and align_utils.move_in_subtree(move, tree_info[node_index].tree_range, mapping_t):
                        new_ranges.append(compute_one_range_for_sequence(align, tree_info, mapping_t, node_index,
                                                                         RangeInterval(left_bound, cur_pos - 1),
                                                                         nei_ranges, nei_ranges,
                                                                         ret_tuple_as_trans_desc))
                        ri = compute_one_range_for_sequence(align, tree_info, mapping_t, node_index,
                                                            RangeInterval(cur_pos, ri.upper_bound),
                                                            nei_ranges, nei_ranges, ret_tuple_as_trans_desc)
                        if ri is None:
                            break
                        left_bound = cur_pos = ri.lower_bound
                        scatter_align = False
                if (align_utils.is_sync_move(move, True) and move_in_nei) or cur_pos == ri.upper_bound:
                    new_ranges.append(compute_one_range_for_sequence(align, tree_info, mapping_t, node_index,
                                                                     RangeInterval(left_bound, cur_pos),
                                                                     nei_ranges, nei_ranges, ret_tuple_as_trans_desc))
                    ri = compute_one_range_for_sequence(align, tree_info, mapping_t, node_index,
                                                        RangeInterval(cur_pos + 1, ri.upper_bound),
                                                        nei_ranges, nei_ranges, ret_tuple_as_trans_desc)
                    if ri is None:
                        break
                    left_bound = cur_pos = ri.lower_bound
                    scatter_align = False
                else:
                    cur_pos += 1
    return new_ranges


def compute_one_range_for_sequence(align, tree_info, mapping_t, node_index, range_interval, left_nei, right_nei,
                                   ret_tuple_as_trans_desc):
    left_bound = find_left_bound(range_interval, align, node_index, tree_info, mapping_t, left_nei,
                                 ret_tuple_as_trans_desc)
    if left_bound == -1:
        return None
    right_bound = find_right_bound(range_interval, align, node_index, tree_info, mapping_t, right_nei,
                                   ret_tuple_as_trans_desc)
    return RangeInterval(left_bound, right_bound)


def compute_ranges_for_xor(align, tree_info, mapping_t, node_index, ranges, ret_tuple_as_trans_desc):
    return compute_ranges_for_sequence(align, tree_info, mapping_t, node_index, ranges, ret_tuple_as_trans_desc)


def compute_ranges_for_sequence(align, tree_info, mapping_t, node_index, ranges, ret_tuple_as_trans_desc):
    lb, ub = tree_info[node_index].tree.parent.index, tree_info[node_index].tree_range.lower_bound - 1
    left_nei = RangeInterval(lb, ub)
    lb = tree_info[node_index].tree_range.upper_bound + 1
    ub = tree_info[tree_info[node_index].tree.parent.index].tree_range.upper_bound
    right_nei = RangeInterval(lb, ub)
    new_ranges = list()
    for ri in ranges:
        new_range = compute_one_range_for_sequence(align, tree_info, mapping_t, node_index, ri, left_nei, right_nei,
                                                   ret_tuple_as_trans_desc)
        if new_range is not None:
            new_ranges.append(new_range)
    return new_ranges


def apply(align, tree_info, mapping_t, com_res, ret_tuple_as_trans_desc):
    ranges = list()
    for node_index in tree_info[com_res.subtree1.index].paths:
        node = tree_info[node_index].tree
        if node_index == 1:
            ranges = [RangeInterval(0, len(align) - 1)]
        elif node.parent.operator == Operator.LOOP:
            ranges = compute_ranges_for_loop(align, tree_info, mapping_t, node.index, ranges, ret_tuple_as_trans_desc)
        elif node.parent.operator == Operator.SEQUENCE:
            ranges = compute_ranges_for_sequence(align, tree_info, mapping_t, node.index, ranges,
                                                 ret_tuple_as_trans_desc)
        elif node.parent.operator == Operator.XOR:
            ranges = compute_ranges_for_xor(align, tree_info, mapping_t, node.index, ranges, ret_tuple_as_trans_desc)
        else:
            pass
    return ranges
