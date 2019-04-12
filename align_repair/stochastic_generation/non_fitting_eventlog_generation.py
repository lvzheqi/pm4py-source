import random

from align_repair.pt_manipulate import pt_number
from pm4py.objects.process_tree.semantics import generate_log
from pm4py.objects.log.log import Trace, EventLog, Event
from pm4py.objects.log.util import xes
from align_repair.stochastic_generation.stochastic_pt_generation import get_cur_label


def create_non_fitting_eventlog(tree, no, prob):
    """
    Returns non-fitting EventLog with fixed traces randomly created by the process tree.

    Parameters
    -----------
    tree
        Process Tree
    no
        Number of traces that will be in the event log
    prob
        Randomness of the traces

    Returns
    ------------
    EventLog
        Non-fitting Eventlog
    """
    log, non_fit_traces = generate_log(tree, no), list()
    label_num = len(pt_number.get_leaves_labels(tree))
    for trace in log:
        non_fit_t = Trace(attributes=log.attributes)
        for event in trace:
            if random.random() < prob:
                index = random.randint(0, 2)
                if index == 1:  # add a new event
                    non_fit_t.append(event)
                    new_event = Event()
                    new_event[xes.DEFAULT_NAME_KEY] = get_cur_label(label_num + 1)
                    non_fit_t.append(new_event)
                elif index == 2:    # replace with other event
                    new_event = Event()
                    new_event[xes.DEFAULT_NAME_KEY] = get_cur_label(random.randint(1, label_num))
                    non_fit_t.append(new_event)
            else:
                non_fit_t.append(event)
        non_fit_traces.append(non_fit_t)
    return EventLog(non_fit_traces, attributes=log.attributes, classifiers=log.classifiers,
                    omni_present=log.omni_present, extensions=log.extensions)






