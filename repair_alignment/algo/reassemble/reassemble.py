from pm4py.objects.log.log import Trace, EventLog, Event
from pm4py.algo.conformance.alignments.utils import STD_MODEL_LOG_MOVE_COST

from repair_alignment.algo import alignments_on_pt
from repair_alignment.algo.utils import align_utils

STD_MODEL_MOD_MOVE_COST = 2


def detect_sub_trace(align, ranges, subtree_range, mapping_t):
    traces = list()
    for ri in ranges:
        trace = Trace()
        for pos in range(ri.lower_bound, ri.upper_bound + 1):
            move = align[pos]
            if (align_utils.is_sync_move(move, True) and
                subtree_range.is_in_range(align_utils.move_index(move, mapping_t, True))) \
                    or align_utils.is_log_move(move, True) or align_utils.is_log_move(move, True):
                event = Event()
                event["concept:name"] = align_utils.log_label(move, True)
                trace.append(event)
        traces.append(trace)
    return traces


def alignment_reassemble(alignment, sub_aligns, ranges, subtree_range, mapping_t):
    new_align, pos = list(), 0
    align, cost = alignment['alignment'], alignment['cost']
    for i, ri in enumerate(ranges):
        sub_align, sub_pos = sub_aligns[i]['alignment'], 0
        new_align += align[pos: ri.lower_bound]
        pos = ri.lower_bound
        while pos <= ri.upper_bound:

            while sub_pos < len(sub_align) and align_utils.is_model_move(sub_align[sub_pos], True):
                new_align.append(sub_align[sub_pos])
                sub_pos += 1

            move = align[pos]
            if align_utils.is_log_move(move, True):
                cost -= STD_MODEL_LOG_MOVE_COST
                new_align.append(sub_align[sub_pos])
                sub_pos += 1
            else:
                move_in_subtree = subtree_range.is_in_range(align_utils.move_index(move, mapping_t, True))
                if not move_in_subtree:
                    new_align.append(align[pos])
                else:
                    if align_utils.is_sync_move(move, True):
                        new_align.append(sub_align[sub_pos])
                        sub_pos += 1
                    else:
                        cost = cost - STD_MODEL_MOD_MOVE_COST if not align_utils.is_none_move(move, True) else cost
            pos += 1
        if sub_pos != len(sub_align) - 1:
            new_align += sub_align[sub_pos:]
        cost += sub_aligns[i]['cost']
    new_align += align[pos:]
    alignment['alignment'] = new_align
    alignment['cost'] = cost


def recompute_fitness(align, trace, best_worst_cost):
    unfitness_upper_part = align['cost']
    if unfitness_upper_part == 0:
        align['fitness'] = 1
    elif (len(trace) + best_worst_cost) > 0:
        align['fitness'] = 1 - align['cost'] / (len(trace) * 5 + best_worst_cost)
    else:
        align['fitness'] = 0


def apply(alignment, log, ranges, mapping_t, com_res, subtree_range, parameters, best_worst_cost):
    traces = detect_sub_trace(alignment['alignment'], ranges, subtree_range, mapping_t)
    sub_aligns = alignments_on_pt(EventLog(traces), com_res.subtree2, parameters)
    alignment_reassemble(alignment, sub_aligns, ranges, subtree_range, mapping_t)
    recompute_fitness(alignment, log, best_worst_cost)
