import copy
from typing import Any

import pm4py
from align_repair.pt_manipulate import pt_number, pt_compare
from align_repair.pt_align import to_petri_net_with_operator as process_to_net_wo
from pm4py.algo.conformance.alignments import factory as align_factory
from pm4py.objects.log.log import Trace, EventLog
from pm4py.algo.conformance import alignments as ali
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE
from align_repair.pt_manipulate.utils import is_node_end, is_node_start, is_move_model, is_move_log,\
    compare_log_move, check_tuple_belong_to_subtree


class Scope(object):
    def __init__(self):
        self._traces = list()
        self._anchor_index = list()

    def traces_append(self, trace):
        self._traces.append(trace)

    def index_append(self, index):
        self._anchor_index.append(index)

    def _get_traces(self):
        return self._traces

    def _get_anchor_index(self):
        return self._anchor_index

    traces = property(_get_traces)
    anchor_index = property(_get_anchor_index)


def detect_change_scope(align, subtree, trace, ret_tuple_as_trans_desc):
    """
    Return the change scope in the alignment

    Parameters
    ------------
    align
        alignment on the original process tree of one trace
    subtree
        the subtree that need to be detected
    trace
        the original trace
    ret_tuple_as_trans_desc

    Returns
    -----------
    index_anchor
        `list()` Store the index of anchor in alignments e.g,[1, 3, 5, 9]

    """

    scope, index, e_index = Scope(), 0, 0
    children = pt_number.get_leaves_labels(subtree)
    while True:
        if index == len(align):
            break

        if is_node_start(align[index], subtree, ret_tuple_as_trans_desc):
            scope.index_append(index)
            new_trace = Trace()
            while not is_node_end(align[index], subtree, ret_tuple_as_trans_desc):
                if is_move_log(align[index], ret_tuple_as_trans_desc) or \
                    (check_tuple_belong_to_subtree(align[index], children, ret_tuple_as_trans_desc)
                     and not is_move_model(align[index], ret_tuple_as_trans_desc)):
                    new_trace.append(trace[e_index])
                e_index = e_index + 1 if not is_move_model(align[index], ret_tuple_as_trans_desc) else e_index
                index += 1
            scope.traces_append(new_trace)
        e_index = e_index + 1 if not is_move_model(align[index], ret_tuple_as_trans_desc) else e_index
        index += 1
    return scope


def alignment_reassemble(align, sub_aligns, anchor_index, subtree1, ret_tuple_as_trans_desc):
    for i in range(len(anchor_index) - 1, -1, -1):
        sub_align = sub_aligns[i]['alignment']
        index = anchor_index[i]

        align[index] = sub_align.pop(0)
        index += 1
        while True:
            children = pt_number.get_all_labels(subtree1)
            if len(sub_align) <= 1:
                while not is_node_end(align[index], subtree1, ret_tuple_as_trans_desc):
                    if is_move_log(align[index], ret_tuple_as_trans_desc) \
                            or check_tuple_belong_to_subtree(align[index], children, ret_tuple_as_trans_desc):
                        align.pop(index)
                    else:
                        index += 1
                if len(sub_align) == 1:
                    align[index] = sub_align.pop(0)
                break

            if is_node_end(align[index], subtree1, ret_tuple_as_trans_desc):
                while len(sub_align) > 1:
                    align.insert(index, sub_align.pop(0))
                    index += 1
                align[index] = sub_align.pop(0)
                break

            if is_move_model(sub_align[0], ret_tuple_as_trans_desc):
                align.insert(index, sub_align.pop(0))
                index += 1
            elif compare_log_move(align[index], sub_align[0], ret_tuple_as_trans_desc):
                align[index] = sub_align.pop(0)
                index += 1
            elif check_tuple_belong_to_subtree(align[index], children, ret_tuple_as_trans_desc):
                align.pop(index)
            else:
                index += 1


def recompute_cost(align, sub_aligns_before, sub_aligns_after):
    for i in range(len(sub_aligns_after)):
        align['cost'] = align['cost'] - sub_aligns_before[i]['cost'] + sub_aligns_after[i]['cost']
        align['visited_states'] = align['visited_states'] - sub_aligns_before[i]['visited_states'] + sub_aligns_after[i][
            'visited_states']
        align['queued_states'] = align['queued_states'] - sub_aligns_before[i]['queued_states'] + sub_aligns_after[i][
            'queued_states']
        align['traversed_arcs'] = align['traversed_arcs'] - sub_aligns_before[i]['traversed_arcs'] + sub_aligns_after[i][
            'traversed_arcs']


def recompute_fitness(alignments, log, tree, parameters, version='state_equation_a_star'):
    net, initial_marking, final_marking = process_to_net_wo.apply_with_operator(tree, parameters)
    best_worst_cost = ali.factory.VERSIONS_COST[version](net, initial_marking, final_marking, parameters)
    for index, align in enumerate(alignments):
        align['fitness'] = 1 - (
                (align['cost'] // ali.utils.STD_MODEL_LOG_MOVE_COST) / (len(log[index]) + best_worst_cost))
        # align['fitness'] = 1 - align['cost'] / (len(log[index]) * 5 + best_worst_cost * 2) if \
        #     not (len(log[index]) == 0 and best_worst_cost == 0) else 1

def apply_pt_alignments(log, tree, parameters):
    net, initial_marking, final_marking = process_to_net_wo.apply_with_operator(tree, parameters)
    parameters = process_to_net_wo.get_parameters(net) if parameters is not None else None
    return align_factory.apply_log(log, net, initial_marking, final_marking, parameters=parameters)


def alignment_repair_with_operator(tree1, tree2, log, parameters=None):
    """
    Alignment repair on tree2 based on the alignment of log on tree1

    Parameters
    -----------
        tree1
            Process Tree
        tree2
            Process Tree
        log
            EventLog
        parameters
            Parameters for alignment

    Returns
    ------------
    alignments
        repaired alignments
    """
    # RELABEL
    pt_number.dfs_number(tree1)
    pt_number.dfs_number(tree2)
    alignments = apply_pt_alignments(log, tree1, parameters)
    align_orig = copy.deepcopy(alignments)
    same, subtree1, subtree2 = pt_compare.pt_compare(tree1, tree2)
    # pt_number.dfs_number(subtree2, n1 + 1)
    ret_tuple_as_trans_desc = parameters[PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE] if parameters is not None else False
    if same:
        return alignments
    else:
        for i, align in enumerate(alignments):
            scope = detect_change_scope(align['alignment'], subtree1, log[i], ret_tuple_as_trans_desc)
            sub_aligns_before = apply_pt_alignments(EventLog(scope.traces), subtree1, parameters)
            sub_aligns_after = apply_pt_alignments(EventLog(scope.traces), subtree2, parameters)
            alignment_reassemble(align['alignment'], sub_aligns_after, scope.anchor_index, subtree1, ret_tuple_as_trans_desc)
            recompute_cost(align, sub_aligns_before, sub_aligns_after)
    recompute_fitness(alignments, log, tree2, parameters)
    # for i in range(len(alignments)):
    #     for t in log:
    #         for e in t:
    #             print(e[pm4py.objects.log.util.xes.DEFAULT_NAME_KEY], end=", ")
    #     print()
    #     print(align_orig[i])
    #     print(alignments[i])
    #     print()
    return alignments


def alignment_repair_with_operator_align(subtree1, subtree2, log, alignments, parameters=None):
    """
    Alignment repair on tree2 based on the alignment of log on tree1

    Parameters
    -----------
        tree1
            Process Tree
        tree2
            Process Tree
        log
            EventLog
        parameters
            Parameters for alignment

    Returns
    ------------
    alignments
        repaired alignments
    """
    # RELABEL
    # pt_number.dfs_number(subtree2, n1 + 1)
    ret_tuple_as_trans_desc = parameters[PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE] if parameters is not None else False
# <<<<<<< HEAD
    same, subtree1, subtree2 = pt_compare.pt_compare(tree1, tree2)
    if same:
        return alignments
    else:
        for i, align in enumerate(alignments):
            scope = detect_change_scope(align['alignment'], subtree1, log[i], ret_tuple_as_trans_desc)
            # case 1: len(scope.traces) == 0
            # case 2: scope.traces = None and subtree = None
            if not (len(scope.traces) == 0 or
                    (len(scope.traces[0]) == 0 and subtree2.operator is None and subtree2.label is None)):
                sub_aligns_before = apply_pt_alignments(EventLog(scope.traces), subtree1, parameters)
                sub_aligns_after = apply_pt_alignments(EventLog(scope.traces), subtree2, parameters)
                alignment_reassemble(align['alignment'], sub_aligns_after, scope.anchor_index, subtree1, ret_tuple_as_trans_desc)
                recompute_cost(align, sub_aligns_before, sub_aligns_after)
        recompute_fitness(alignments, log, tree2, parameters)
# =======
#     # if same:
#     #     return alignments
#     # else:
#     for i, align in enumerate(alignments):
#         scope = detect_change_scope(align['alignment'], subtree1, log[i], ret_tuple_as_trans_desc)
#         sub_aligns_before = apply_pt_alignments(EventLog(scope.traces), subtree1, parameters)
#         sub_aligns_after = apply_pt_alignments(EventLog(scope.traces), subtree2, parameters)
#         alignment_reassemble(align['alignment'], sub_aligns_after, scope.anchor_index, subtree1, ret_tuple_as_trans_desc)
#         recompute_cost(align, sub_aligns_before, sub_aligns_after)
#     # recompute_fitness(alignments, log, tree2, parameters)
# >>>>>>> origin/master
    # for i in range(len(alignments)):
    #     for t in log:
    #         for e in t:
    #             print(e[pm4py.objects.log.util.xes.DEFAULT_NAME_KEY], end=", ")
    #     print()
    #     print(align_orig[i])
    #     print(alignments[i])
    #     print()
    return alignments


def alignment_repair_wo_operator(tree1, tree2, log):
    pass
