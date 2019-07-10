import copy

from pm4py.objects.log.log import Trace, EventLog
from pm4py.algo.conformance.alignments import factory as align_factory

from align_repair.process_tree.manipulation.pt_compare import CompareResult
from align_repair.process_tree.alignments import utils as pt_align_utils
from align_repair.process_tree.conversion import to_petri_net_with_lock as pt_to_lock_net
from align_repair.process_tree.manipulation import pt_number, pt_compare
from align_repair.repair.optimal.align_repair2 import detect_stop_condition, range_detect
from align_repair.repair.optimal.utils import recursively_init_tree_tables, RangeInterval
from align_repair.repair.lock_pt import scope_expand
from align_repair.repair.optimal import align_repair_opt
from pm4py.objects.process_tree.process_tree import ProcessTree

STD_MODEL_MOD_MOVE_COST = 2


def add_lock_for_each_node(tree: ProcessTree, align, tree_info, mapping_t):
    q = list()
    q.append(tree)
    node_list = list()
    while len(q) != 0:
        node = q.pop(0)
        node_list.append(node)
        for i in range(len(node.children)):
            q.append(node.children[i])
    for node in node_list:
        com_res = CompareResult(True, node, node)
        stop_condition = detect_stop_condition(node, tree_info)
        ranges = range_detect(align, tree_info, mapping_t, com_res, stop_condition)
        for ri in ranges[::-1]:
            move = ((">>", str(node.index) + '_e_1'), (">>", str(node.index) + '_e'))
            align.insert(ri.upper_bound + 1, move)
            move = ((">>", str(node.index) + '_s_1'), (">>", str(node.index) + '_s'))
            align.insert(ri.lower_bound, move)


def remove_lock(align, index):
    pos = len(index)
    for i in range(len(align) - 1, -1, -1):
        if align[i][1][1] is not None and (align[i][1][1].endswith('_s') or align[i][1][1].endswith('_e')):
            while pos - 1 >= 0 and index[pos - 1] >= i:
                pos -= 1
            for j in range(pos, len(index)):
                if j % 2 == 0 and index[j] == i:
                    pass
                else:
                    index[j] -= 1
            align.pop(i)
    return index


def compute_repairing_alignments(tree, com_res, log, alignments, tree_info, mapping_t, parameters, best_worst_cost):
    alignments = copy.deepcopy(alignments)
    for i, alignment in enumerate(alignments):
        align = alignment['alignment']
        if alignment.get("repair") is None:
            print(align)
            add_lock_for_each_node(tree, align, tree_info, mapping_t)
            scope_expand.scope_expand_trace(align, com_res.subtree1, True)
            index = scope_expand.search_scope_index(align, com_res.subtree1, True)
            index = remove_lock(align, index)
            print("index", index)
            ranges = list()
            for j in range(len(index)//2):
                ranges.append(RangeInterval(index[j * 2], index[j * 2 + 1]))

            if len(ranges) != 0:
                align_repair_opt.align_repair_one_trace(alignment, log, ranges, mapping_t, com_res,
                                                        tree_info[com_res.subtree1.index].tree_range, parameters,
                                                        best_worst_cost)
            alignment["repair"] = True
    for a in alignments:
        a.pop("repair") if a.get("repair") is not None else None
    return alignments


def apply_pt_alignments(log, tree, parameters):
    net, initial_marking, final_marking = pt_to_lock_net.apply(tree, parameters)
    new_parameters = pt_align_utils.alignment_parameters(net)
    return align_factory.apply_log(log, net, initial_marking, final_marking, new_parameters)


def apply(tree, m_tree, log, parameters=None, option=1):
    pt_number.apply(tree, 'D')
    pt_number.apply(m_tree, 'D')
    alignments = apply_pt_alignments(log, tree, parameters)
    com_res = pt_compare.apply(tree, m_tree, option)
    if com_res.value:
        return alignments, copy.deepcopy(alignments)
    else:
        mapping_t, tree_info = dict(), dict()
        recursively_init_tree_tables(tree, tree_info, mapping_t, [1])
        best_worst_cost = apply_pt_alignments(EventLog([Trace()]), m_tree, parameters)[0]['cost']
        repairing_alignment = compute_repairing_alignments(tree, com_res, log, alignments, tree_info, mapping_t,
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
        best_worst_cost = apply_pt_alignments(EventLog([Trace()]), m_tree, parameters)[0]['cost']
        repairing_alignment = compute_repairing_alignments(tree, com_res, log, alignments, tree_info, mapping_t,
                                                           parameters, best_worst_cost)
    return alignments, repairing_alignment
