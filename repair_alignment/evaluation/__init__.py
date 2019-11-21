import pm4py
from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.visualization.process_tree import factory as pt_vis_factory
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.objects.conversion.process_tree import factory as pt_to_net
from pm4py.algo.conformance.alignments import factory as align_factory
from pm4py.algo.conformance import alignments as ali

from repair_alignment.process_tree.conversion import to_petri_net as pt_to_lock_net
from repair_alignment.algo.utils import align_utils


def create_event_log(log):
    traces = list()
    for events in log.split(", "):
        trace = Trace()
        for e in list(events):
            event = Event()
            event["concept:name"] = e
            trace.append(event)
        traces.append(trace)
    return EventLog(traces)


def print_event_log(log):

    for trace in log:
        for event in trace:
            print(event[pm4py.objects.log.util.xes.DEFAULT_NAME_KEY], end='')
        print(end=" ")
    print()


def is_not_silent_move(align, ret_tuple_as_trans_desc):
    if ret_tuple_as_trans_desc:
        align = align[1]
    if align[0] == ali.utils.SKIP and (align[1] is None or align[1].endswith(align_utils.LOCK_START)
                                       or align[1].endswith(align_utils.LOCK_END)):
        return False
    return True


def print_short_alignment(alignments, ret_tuple_as_trans_desc, title="Align: "):
    for align in alignments:
        if align.get("print") is None:
            new_align = []
            for a in align['alignment']:
                if is_not_silent_move(a, ret_tuple_as_trans_desc):
                    if ret_tuple_as_trans_desc:
                        new_align.append(a[1])
                    else:
                        new_align.append(a)
            align["alignment"] = new_align
            align["print"] = True
    for align in alignments:
        if align.get("print") is not None:
            align.pop("print")
    print(title, alignments)


def alignment_default_on_pt(tree, log):
    net, initial_marking, final_marking = pt_to_net.apply(tree)
    parameters = align_utils.alignment_parameters(net)
    parameters['ret_tuple_as_trans_desc'] = True
    alignments = align_factory.apply_log(log, net, initial_marking, final_marking, parameters)
    return alignments


def alignment_on_pt(tree, log):
    net, initial_marking, final_marking = pt_to_lock_net.apply(tree)
    parameters = align_utils.alignment_parameters(net)
    alignments = align_factory.apply_log(log, net, initial_marking, final_marking, parameters)
    return alignments


def alignment_on_lock_pt(tree, log):
    net, initial_marking, final_marking = pt_to_lock_net.apply(tree, {'PARAM_CHILD_LOCK': True})
    parameters = align_utils.alignment_parameters(net)
    parameters['ret_tuple_as_trans_desc'] = True
    parameters['PARAM_CHILD_LOCK'] = True
    alignments = align_factory.apply_log(log, net, initial_marking, final_marking, parameters)
    return alignments


def alignment_on_loop_lock_pt(tree, log):
    net, initial_marking, final_marking = pt_to_lock_net.apply(tree, {'PARAM_LOOP_LOCK': True})
    parameters = align_utils.alignment_parameters(net)
    parameters['ret_tuple_as_trans_desc'] = False
    parameters['PARAM_LOOP_LOCK'] = True
    alignments = align_factory.apply_log(log, net, initial_marking, final_marking, parameters)
    return alignments


def get_best_cost_on_pt(tree, log):
    cost = alignment_on_lock_pt(tree, EventLog([Trace()]))[0]['cost']
    return sum([cost + len(trace) * ali.utils.STD_MODEL_LOG_MOVE_COST for trace in log])


def draw_normal_pn4pt(tree, parameters=None):
    net, initial_marking, final_marking = pt_to_net.apply(tree, parameters)
    gviz = pn_vis_factory.apply(net)
    pn_vis_factory.view(gviz)


def draw_lock_pn4pt(tree, parameters=None):
    net, initial_marking, final_marking = pt_to_lock_net.apply(tree, parameters)
    gviz = pn_vis_factory.apply(net)
    pn_vis_factory.view(gviz)


def draw_process_tree(tree):
    gvis = pt_vis_factory.apply(tree)
    pt_vis_factory.view(gvis)
