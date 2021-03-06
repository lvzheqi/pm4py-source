from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.algo.conformance.alignments import factory as align_factory

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
