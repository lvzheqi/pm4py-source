"""
This module provides the methods of alignment repair.
'ret_tuple_as_trans_desc' state of the given alignment should be True.
In that way we distinguish the status of silent transition. The repaired Alignment could then make sense.
"""
import copy

from pm4py.algo.conformance.alignments import factory as align_factory
from pm4py.objects.log.log import Trace, EventLog
from pm4py.algo.conformance import alignments as ali
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE

from align_repair.process_tree.manipulation import pt_compare, pt_number
from align_repair.process_tree.manipulation import utils as pt_mani_utils
from align_repair.process_tree.alignments import utils as pt_align_utils
from align_repair.process_tree.conversion import to_petri_net_with_lock as pt_to_lock_net


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


def detect_change_scope(align, subtree, trace):
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

    Returns
    -----------
    index_anchor
        `list()` Store the index of anchor in alignments e.g,[1, 3, 5, 9]

    """

    scope, index, e_index = Scope(), 0, 0
    children = pt_mani_utils.non_none_leaves_labels(subtree)
    while True:
        if index == len(align):
            break

        if pt_align_utils.is_node_start(align[index], subtree, True):
            scope.index_append(index)
            new_trace = Trace()
            while not pt_align_utils.is_node_end(align[index], subtree, True):
                if pt_align_utils.is_log_move(align[index], True) or \
                    (pt_align_utils.check_model_label_belong_to_subtree(align[index], children, True)
                     and not pt_align_utils.is_model_move(align[index], True)):
                    new_trace.append(trace[e_index])
                e_index = e_index + 1 if not pt_align_utils.is_model_move(align[index], True) else e_index
                index += 1
            scope.traces_append(new_trace)
        e_index = e_index + 1 if not pt_align_utils.is_model_move(align[index], True) else e_index
        index += 1
    return scope


def alignment_reassemble(align, sub_aligns, anchor_index, subtree1):
    for i in range(len(anchor_index) - 1, -1, -1):
        sub_aligns[i] = copy.deepcopy(sub_aligns[i])
        sub_align = sub_aligns[i]['alignment']
        index = anchor_index[i]
        align[index] = sub_align.pop(0)
        index += 1
        while True:
            labels_in_subtree1 = pt_mani_utils.lock_tree_labels(subtree1)
            if len(sub_align) <= 1:
                while not pt_align_utils.is_node_end(align[index], subtree1, True):
                    if pt_align_utils.is_log_move(align[index], True) or \
                            pt_align_utils.check_model_label_belong_to_subtree(align[index], labels_in_subtree1, True):
                        align.pop(index)
                    else:
                        index += 1
                align[index] = sub_align.pop(0) if len(sub_align) == 1 else None
                break

            if pt_align_utils.is_node_end(align[index], subtree1, True):
                while len(sub_align) > 1:
                    align.insert(index, sub_align.pop(0))
                    index += 1
                align[index] = sub_align.pop(0)
                break

            if pt_align_utils.is_model_move(sub_align[0], True):
                align.insert(index, sub_align.pop(0))
                index += 1
            elif pt_align_utils.compare_log_label(align[index], sub_align[0], True):
                align[index] = sub_align.pop(0)
                index += 1
            elif pt_align_utils.check_model_label_belong_to_subtree(align[index], labels_in_subtree1, True):
                align.pop(index)
            else:
                index += 1


def recompute_cost(align, sub_aligns_before, sub_aligns_after):
    for i in range(len(sub_aligns_after)):
        align['cost'] += sub_aligns_after[i]['cost'] - sub_aligns_before[i]['cost']
        align['visited_states'] += sub_aligns_after[i]['visited_states'] - sub_aligns_before[i]['visited_states']
        align['queued_states'] += sub_aligns_after[i]['queued_states'] - sub_aligns_before[i]['queued_states']
        align['traversed_arcs'] += sub_aligns_after[i]['traversed_arcs'] - sub_aligns_before[i]['traversed_arcs']


def recompute_fitness(align, trace, best_worst_cost):
    unfitness_upper_part = align['cost']
    if unfitness_upper_part == 0:
        align['fitness'] = 1
    elif (len(trace) + best_worst_cost) > 0:
        align['fitness'] = 1 - align['cost'] / (
                len(trace) * ali.utils.STD_MODEL_LOG_MOVE_COST + best_worst_cost)
    else:
        align['fitness'] = 0


def apply_pt_alignments(log, tree):
    net, initial_marking, final_marking = pt_to_lock_net.apply(tree)
    new_parameters = pt_align_utils.alignment_parameters(net)
    new_parameters[PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE] = True
    return align_factory.apply_log(log, net, initial_marking, final_marking, new_parameters)


def apply(tree1, tree2, log, alignments, parameters=None):
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
        alignments
            related alignment of log on tree1
        parameters

    Returns
    ------------
    alignments
        repaired alignments
    """
    parameters = {} if parameters is None else parameters
    parameters['COMPARE_OPTION'] = 1 if parameters.get('COMPARE_OPTION') is None else parameters['COMPARE_OPTION']
    # TODO: if the given alignment is not True, try-catch
    alignments = copy.deepcopy(alignments)
    com_res = pt_compare.apply(tree1, tree2, parameters['COMPARE_OPTION'])
    print(com_res.subtree1, com_res.subtree2)
    if com_res.value:
        return alignments
    else:
        tree1_total_number = pt_mani_utils.nodes_number(tree1)
        pt_number.apply(com_res.subtree2, 'D', tree1_total_number + 1)
        best_worst_cost = apply_pt_alignments(EventLog([Trace()]), tree2)[0]['cost']
        for i in range(len(alignments)):
            align = alignments[i]
            if align.get("repair") is None:
                scope = detect_change_scope(align['alignment'], com_res.subtree1, log[i])
                if not len(scope.traces) == 0:
                    sub_aligns_before = apply_pt_alignments(EventLog(scope.traces), com_res.subtree1)
                    sub_aligns_after = apply_pt_alignments(EventLog(scope.traces), com_res.subtree2)
                    alignment_reassemble(align['alignment'], sub_aligns_after, scope.anchor_index, com_res.subtree1)
                    recompute_cost(align, sub_aligns_before, sub_aligns_after)
                    recompute_fitness(align, log[i], best_worst_cost)
                align["repair"] = True
        for a in alignments:
            a.pop("repair") if a.get("repair") is not None else None
    return alignments
