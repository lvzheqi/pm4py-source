import copy
from pm4py.objects.log.log import Trace, EventLog

from repair_alignment.process_tree.operation import pt_number, pt_compare
from repair_alignment.algo.utils import tree_utils
from repair_alignment.algo.range_detection import rd_linear, se_rd_lock, rd_top_down, se_rd_top_down
from repair_alignment.algo.reassemble import reassemble
from repair_alignment.algo import alignments_on_pt
from repair_alignment.algo.repair.version import Version


def compute_repairing_alignments(state, com_res, log, alignments, tree_info, mapping_t, parameters, best_worst_cost):
    alignments = copy.deepcopy(alignments)
    stop_condition = tree_utils.detect_stop_condition(com_res.subtree1, tree_info)
    for i, alignment in enumerate(alignments):
        align = alignment['alignment']
        if alignment.get("repair") is None:
            ranges = list()
            if state == Version.AR_LINEAR:
                ranges = rd_linear.apply(align, tree_info, mapping_t, com_res, stop_condition, True)
            elif state == Version.IAR_LINEAR:
                ranges = se_rd_lock.apply(align, tree_info, mapping_t, com_res, True)
            elif state == Version.AR_TOP_DOWN:
                ranges = rd_top_down.apply(align, tree_info, mapping_t, com_res, True)
            elif state == Version.IAR_TOP_DOWN:
                ranges = se_rd_top_down.apply(align, tree_info, mapping_t, com_res, True)
            if len(ranges) != 0:
                reassemble.apply(alignment, log, ranges, mapping_t, com_res,
                                 tree_info[com_res.subtree1.index].tree_range, parameters,
                                 best_worst_cost)
            alignment["repair"] = True
    for a in alignments:
        a.pop("repair") if a.get("repair") is not None else None
    return alignments


def apply_with_alignments(tree, m_tree, log, alignments, state, parameters=None, option=1):
    pt_number.apply(tree, 'D')
    pt_number.apply(m_tree, 'D')
    com_res = pt_compare.apply(tree, m_tree, option)
    if com_res.value:
        return alignments, copy.deepcopy(alignments)
    else:
        mapping_t, tree_info = dict(), dict()
        tree_utils.recursively_init_tree_tables(tree, tree_info, mapping_t, [1])
        best_worst_cost = alignments_on_pt(EventLog([Trace()]), m_tree, parameters)[0]['cost']
        repairing_alignment = compute_repairing_alignments(state, com_res, log, alignments, tree_info, mapping_t,
                                                           parameters, best_worst_cost)
    return alignments, repairing_alignment


def apply(tree, m_tree, log, state, parameters=None, option=1):
    alignments = alignments_on_pt(log, tree, parameters)
    return apply_with_alignments(tree, m_tree, log, alignments, state, parameters, option)
