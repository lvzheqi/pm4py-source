from repair_alignment.algo.utils import align_utils
from repair_alignment.algo.utils.tree_utils import RangeInterval


def remove_first_log_move(align, begin, mapping_t, subtree_range, ret_tuple_as_trans_desc):
    left_bound = begin
    while True:
        if left_bound == len(align):
            return None
        move = align[left_bound]
        if not align_utils.is_log_move(move, ret_tuple_as_trans_desc):
            move_cur_index = align_utils.move_index(move, mapping_t, ret_tuple_as_trans_desc)
            if subtree_range.is_in_range(move_cur_index):
                break
        left_bound += 1
    return RangeInterval(left_bound, len(align) - 1)


def apply(align, tree_info, mapping_t, com_res, stop_condition, ret_tuple_as_trans_desc):
    ranges = list()
    subtree_range = tree_info[com_res.subtree1.index].tree_range

    anchor = True
    range_interval = remove_first_log_move(align, 0, mapping_t, subtree_range, ret_tuple_as_trans_desc)
    if range_interval is not None:
        cur_index = left_bound = right_bound = range_interval.lower_bound
        while cur_index < len(align):
            move = align[cur_index]
            if align_utils.is_log_move(move, ret_tuple_as_trans_desc):
                if anchor:
                    right_bound += 1
            else:
                move_cur_index = align_utils.move_index(move, mapping_t, ret_tuple_as_trans_desc)
                if subtree_range.is_in_range(move_cur_index):
                    anchor = True
                    right_bound = cur_index
                elif stop_condition[0].is_in_range(move_cur_index) or stop_condition[1].is_in_range(move_cur_index):
                    ranges.append(RangeInterval(left_bound, right_bound))
                    anchor = True
                    range_interval = remove_first_log_move(align, cur_index, mapping_t, subtree_range,
                                                           ret_tuple_as_trans_desc)
                    if range_interval is None:
                        break
                    cur_index = left_bound = right_bound = range_interval.lower_bound
                else:
                    anchor = False
            if cur_index == len(align) - 1:
                ranges.append(RangeInterval(left_bound, right_bound))
            cur_index += 1
    return ranges
