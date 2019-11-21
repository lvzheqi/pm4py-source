import pandas as pd
import random
import pm4py
from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.visualization.process_tree import factory as pt_vis_factory
from pm4py.objects.process_tree import util as pt_utils

from repair_alignment.evaluation import alignment_on_pt, create_event_log, get_best_cost_on_pt
from repair_alignment.process_tree.operation import pt_compare
from repair_alignment.evaluation.compare import apply_repair_align_on_one_pt
from repair_alignment.algo.repair.version import Version


PATH = "../../../data/reallife"
def xes_to_list(log):
    data = []
    for trace in log:
        trace_act = ""
        for event in trace:
            trace_act += event[pm4py.objects.log.util.xes.DEFAULT_NAME_KEY] + ", "
        data.append(trace_act[:-2])
    return data


def xes_to_csv(file):
    # "../../../data/hospital_billing_com.xes"
    log = xes_importer.apply(file)
    pd.DataFrame(xes_to_list(log), columns=["trace"]).to_csv("../../../data/reallife.csv", index=False)


def list_to_xes(log):
    # log = pd.read_csv("../../../data/reallife.csv")["trace"].tolist()
    traces = list()
    for t in log:
        trace = Trace()
        for e in t.split(", "):
            event = Event()
            event["concept:name"] = e
            trace.append(event)
        traces.append(trace)
    return EventLog(traces)


def inductive_to_petri_net(log):
    tree = inductive_miner.apply_tree(log)
    gviz = pt_vis_factory.apply(tree)
    pt_vis_factory.view(gviz)
    return tree


def split_real_life_data():
    logs = pd.read_csv("../../../data/reallife.csv")["trace"].tolist()
    log_test = random.sample(logs, len(logs) // 2)
    pd.DataFrame(log_test, columns=["trace"]).to_csv("../../../data/reallife_test.csv", index=False)
    log_tree = random.sample(logs, len(logs) // 3)
    pd.DataFrame(log_test, columns=["trace"]).to_csv("../../../data/reallife_tree.csv", index=False)
    tree = inductive_to_petri_net(list_to_xes(log_tree))
    m_trees = []
    for i in range(5):
        log_part = random.sample(logs, len(logs) // 3)
        pd.DataFrame(log_part, columns=["trace"]).to_csv(
            "../../../data/reallife_part" + str(i + 1) + ".csv", index=False)
        m_tree = inductive_to_petri_net(list_to_xes(log_part))
        m_trees.append(m_tree)
        print(str(tree) == str(m_tree))
        print(pt_compare.apply(tree, m_tree))


def compute_alignment():
    logs = pd.read_csv("../../../data/reallife.csv")["trace"].tolist()
    log = list_to_xes(random.sample(logs, len(logs) // 100))
    print(len(log))
    # log = pd.read_csv("../../../data/reallife_test.csv")["trace"].tolist()
    tree_log = pd.read_csv("../../../data/reallife_test.csv")["trace"].tolist()
    tree = inductive_miner.apply_tree(list_to_xes(tree_log))
    alignments = alignment_on_pt(tree, log)
    for i in range(2):
        m_tree_log = pd.read_csv("../../../data/reallife_part" + str(i + 1) + ".csv")["trace"].tolist()
        m_tree = inductive_miner.apply_tree(list_to_xes(m_tree_log))
        apply_repair_align_on_one_pt(tree, m_tree, log, alignments, Version.IAR_TOP_DOWN, 1)
        apply_repair_align_on_one_pt(tree, m_tree, log, alignments, Version.AR_LINEAR, 1)


if __name__ == "__main__":
    compute_alignment()
