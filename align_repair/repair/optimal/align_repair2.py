import copy
from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.objects.log.log import Trace, EventLog

from align_repair.process_tree.alignments import utils as pt_align_utils
from align_repair.process_tree.manipulation import pt_number, pt_compare
from align_repair.repair.optimal.utils import RangeInterval, recursively_init_tree_tables
from align_repair.repair.optimal import align_repair_opt


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


def remove_first_log_move(align, begin, mapping_t, subtree_range):
    left_bound = begin
    while True:
        if left_bound == len(align):
            return None
        move = align[left_bound]
        if not pt_align_utils.is_log_move(move, True):
            move_cur_index = pt_align_utils.move_index(move, mapping_t, True)
            if subtree_range.is_in_range(move_cur_index):
                break
        left_bound += 1
    return RangeInterval(left_bound, len(align) - 1)


def range_detect(align, tree_info, mapping_t, com_res, stop_condition):
    ranges = list()
    subtree_range = tree_info[com_res.subtree1.index].tree_range

    anchor = True
    range_interval = remove_first_log_move(align, 0, mapping_t, subtree_range)
    if range_interval is not None:
        cur_index = left_bound = right_bound = range_interval.lower_bound
        while cur_index < len(align):
            move = align[cur_index]
            if pt_align_utils.is_log_move(move, True):
                if anchor:
                    right_bound += 1
            else:
                move_cur_index = pt_align_utils.move_index(move, mapping_t, True)
                if subtree_range.is_in_range(move_cur_index):
                    anchor = True
                    right_bound = cur_index
                elif stop_condition[0].is_in_range(move_cur_index) or stop_condition[1].is_in_range(move_cur_index) :
                    ranges.append(RangeInterval(left_bound, right_bound))
                    anchor = True
                    range_interval = remove_first_log_move(align, cur_index, mapping_t, subtree_range)
                    if range_interval is None:
                        break
                    cur_index = left_bound = right_bound = range_interval.lower_bound
                else:
                    anchor = False
            if cur_index == len(align) - 1:
                ranges.append(RangeInterval(left_bound, right_bound))
            cur_index += 1
    return ranges


def compute_repairing_alignments(com_res, log, alignments, tree_info, mapping_t, parameters, best_worst_cost):
    alignments = copy.deepcopy(alignments)
    stop_condition = detect_stop_condition(com_res.subtree1, tree_info)
    for i, alignment in enumerate(alignments):
        align = alignment['alignment']
        if alignment.get("repair") is None:
            ranges = range_detect(align, tree_info, mapping_t, com_res, stop_condition)
            # print(ranges)
            # from align_repair.repair.optimal import align_repair
            # ranges2 = align_repair.range_detect(align, tree_info, mapping_t, com_res)
            # print(ranges2)
            # if str(ranges) != str(ranges2):
            #     exit(-1)
            if len(ranges) != 0:
                align_repair_opt.align_repair_one_trace(alignment, log, ranges, mapping_t, com_res,
                                                        tree_info[com_res.subtree1.index].tree_range, parameters,
                                                        best_worst_cost)
            alignment["repair"] = True
    for a in alignments:
        a.pop("repair") if a.get("repair") is not None else None
    return alignments


def apply(tree, m_tree, log, parameters=None, option=1):
    pt_number.apply(tree, 'D')
    pt_number.apply(m_tree, 'D')
    alignments = align_repair_opt.apply_pt_alignments(log, tree, parameters)
    com_res = pt_compare.apply(tree, m_tree, option)
    if com_res.value:
        return alignments, copy.deepcopy(alignments)
    else:
        mapping_t, tree_info = dict(), dict()
        recursively_init_tree_tables(tree, tree_info, mapping_t, [1])
        best_worst_cost = align_repair_opt.apply_pt_alignments(EventLog([Trace()]), m_tree, parameters)[0]['cost']
        repairing_alignment = compute_repairing_alignments(com_res, log, alignments, tree_info, mapping_t,
                                                           parameters, best_worst_cost)
    return alignments, repairing_alignment


def apply_with_alignments(tree, m_tree, log, alignments, parameters=None, option=1):
    pt_number.apply(tree, 'D')
    pt_number.apply(m_tree, 'D')
    com_res = pt_compare.apply(tree, m_tree, option)
    if com_res.value:
        return alignments, copy.deepcopy(alignments)
    else:
        mapping_t, tree_info = dict(), dict()
        recursively_init_tree_tables(tree, tree_info, mapping_t, [1])
        best_worst_cost = align_repair_opt.apply_pt_alignments(EventLog([Trace()]), m_tree, parameters)[0]['cost']
        repairing_alignment = compute_repairing_alignments(com_res, log, alignments, tree_info, mapping_t,
                                                           parameters, best_worst_cost)
    return alignments, repairing_alignment
