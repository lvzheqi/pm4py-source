import random

from pm4py.objects.process_tree.semantics import generate_log
from pm4py.objects.log.log import Trace, EventLog, Event
from pm4py.objects.log.util import xes

from align_repair.process_tree.stochastic_generation import utils as pt_gene_utils
from align_repair.process_tree.manipulation import utils as pt_mani_utils


def apply(tree, no, prob):
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
        Non-fitting event log
    """
    log, non_fit_traces = generate_log(tree, no), list()
    label_num = pt_mani_utils.non_none_leaves_number(tree)
    for trace in log:
        non_fit_t = Trace(attributes=log.attributes)
        for event in trace:
            if random.random() < prob:
                index = random.randint(0, 2)
                if index == 1:  # add a new event
                    non_fit_t.append(event)
                    new_event = Event()
                    new_event[xes.DEFAULT_NAME_KEY] = pt_gene_utils.get_cur_label(label_num + 1)
                    non_fit_t.append(new_event)
                elif index == 2:    # replace with other event
                    new_event = Event()
                    new_event[xes.DEFAULT_NAME_KEY] = pt_gene_utils.get_cur_label(random.randint(1, label_num))
                    non_fit_t.append(new_event)
            else:
                non_fit_t.append(event)
        non_fit_traces.append(non_fit_t)
    return EventLog(non_fit_traces, attributes=log.attributes, classifiers=log.classifiers,
                    omni_present=log.omni_present, extensions=log.extensions)
