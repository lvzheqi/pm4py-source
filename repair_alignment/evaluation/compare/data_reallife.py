import pandas as pd
import random
import pm4py
from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.visualization.process_tree import factory as pt_vis_factory
from pm4py.objects.process_tree import util as pt_utils

from repair_alignment.process_tree.operation import pt_compare
from repair_alignment.evaluation.compare import compute_align_grade
from repair_alignment.process_tree.operation import utils as ra_pt_utils

PATH = "../../../data/D5/"


def xes_to_csv(file, file_to_write):
    log = xes_importer.apply(PATH + file)
    data = []
    for trace in log:
        trace_act = ""
        for event in trace:
            trace_act += event[pm4py.objects.log.util.xes.DEFAULT_NAME_KEY] + ", "
        data.append(trace_act[:-2])
    pd.DataFrame(data, columns=["trace"]).to_csv(PATH + file_to_write, index=False)


def list_to_xes(log):
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


def random_select_real_life_data(file):
    name = file.split(".")[0]
    logs = pd.read_csv(PATH + file)["trace"].tolist()
    # log_test = random.sample(logs, len(logs) // 2)
    # pd.DataFrame(log_test, columns=["trace"]).to_csv(PATH + name + "_test.csv", index=False)
    log_tree = random.sample(logs, len(logs) // 30)
    pd.DataFrame(log_tree, columns=["trace"]).to_csv(PATH + name + "_tree.csv", index=False)
    tree = inductive_miner.apply_tree(list_to_xes(log_tree))
    # tree_log = pd.read_csv(PATH + name + "_tree.csv")["trace"].tolist()
    # tree = inductive_miner.apply_tree(list_to_xes(tree_log))
    m_trees = []
    print(str(tree))
    for i in range(10):
        log_part = random.sample(logs, len(logs) // 30)
        pd.DataFrame(log_part, columns=["trace"]).to_csv(PATH + name + "_part" + str(i + 1) + ".csv", index=False)
        m_tree = inductive_miner.apply_tree(list_to_xes(log_part))
        m_trees.append(m_tree)
        print(str(tree) == str(m_tree))
        print(pt_compare.apply(tree, m_tree))


def split_real_life_data(file):
    name = file.split(".")[0]
    logs = pd.read_csv(PATH + file)["trace"].tolist()
    # log_test = random.sample(logs, len(logs) // 2)
    # pd.DataFrame(log_test, columns=["trace"]).to_csv(PATH + name + "_test.csv", index=False)
    log_tree = logs[0: len(logs)//10]
    pd.DataFrame(log_tree, columns=["trace"]).to_csv(PATH + name + "_tree.csv", index=False)
    tree = inductive_miner.apply_tree(list_to_xes(log_tree))
    m_trees = []
    print(str(tree))
    for i in range(1, 5):
        log_part = logs[i*len(logs)//10: len(logs)//10*(i+1)]
        pd.DataFrame(log_part, columns=["trace"]).to_csv(PATH + name + "_part" + str(i + 1) + ".csv", index=False)
        m_tree = inductive_miner.apply_tree(list_to_xes(log_part))
        m_trees.append(m_tree)
        print(str(tree) == str(m_tree))
        print(pt_compare.apply(tree, m_tree))


def result(file):
    name = file.split(".")[0]
    logs = pd.read_csv(PATH + file)["trace"].tolist()
    for rd in range(1):
        log = list_to_xes(random.sample(logs, len(logs)//10))
        # log = pd.read_csv("../../../data/reallife_test.csv")["trace"].tolist()
        tree_log = pd.read_csv(PATH + name + "_tree.csv")["trace"].tolist()
        tree = inductive_miner.apply_tree(list_to_xes(tree_log))
        print(ra_pt_utils.pt_depth(str(tree)))
        m_trees = []
        for i in range(4):
            m_tree_log = pd.read_csv(PATH + name + "_part" + str(i + 1) + ".csv")["trace"].tolist()
            m_tree = inductive_miner.apply_tree(list_to_xes(m_tree_log))
            print(ra_pt_utils.pt_depth(str(m_tree)))
            print(len(ra_pt_utils.parse_tree_to_a_bfs_sequence(m_tree)), "+")

            m_trees.append(m_tree)
            res_com = pt_compare.apply(tree, m_tree)
            print(len(ra_pt_utils.parse_tree_to_a_bfs_sequence(res_com.subtree1)),
                  len(ra_pt_utils.parse_tree_to_a_bfs_sequence(res_com.subtree2)))
        # res = compute_align_grade(log, tree, m_trees)
        # res.to_csv(PATH + name + str(rd) + "_result.csv")


if __name__ == "__main__":
    # file_name = "hbc.csv"
    # xes_to_csv("hospital_billing_com.xes", file_name)
    # split_real_life_data(file_name)
    # result(file_name)

    file_name = "bpi2019.csv"
    # 2,5,4,6,5
    # xes_to_csv("bpi2019.xes", file_name)
    # split_real_life_data(file_name)
    # random_select_real_life_data(file_name)
    result(file_name)
