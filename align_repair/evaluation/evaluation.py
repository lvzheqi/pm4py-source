import time
import matplotlib.pyplot as plt
import random
import copy

from align_repair.stochastic_generation.stochastic_pt_generation import randomly_create_new_tree
from align_repair.stochastic_generation.non_fitting_eventlog_generation import create_non_fitting_eventlog
from pm4py.objects.conversion.process_tree import factory as pt_to_net
from align_repair.pt_align import to_petri_net_with_operator as pt_to_net_with_op
from pm4py.algo.conformance.alignments import factory as align_factory
from align_repair.stochastic_generation.stochastic_mutated_pt import randomly_create_mutated_tree
from pm4py.algo.conformance import alignments as ali
from align_repair.pt_manipulate import pt_number
from align_repair.repair.align_repair import alignment_repair_with_operator_align
from align_repair.repair.scope_expand import scope_expand
from align_repair.pt_manipulate.pt_compare import pt_compare
from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.objects.process_tree import util as pt_util


def avg_runtime_without_lock(trees, logs):
    start = time.time()
    for i, tree in enumerate(trees):
        net, initial_marking, final_marking = pt_to_net.apply(tree)
        align_factory.apply_log(logs[i], net, initial_marking, final_marking)
    end = time.time()
    print((end - start) / len(trees))
    return (end - start) / len(trees)


def avg_runtime_with_lock(trees, logs):
    start = time.time()
    for i, tree in enumerate(trees):
        net, initial_marking, final_marking = pt_to_net_with_op.apply_with_operator(tree)
        parameters = pt_to_net_with_op.get_parameters(net)
        parameters['PARAM_CHILD_LOCK'] = True
        align_factory.apply_log(logs[i], net, initial_marking, final_marking, parameters)
    end = time.time()
    print((end - start) / len(trees))
    return (end - start) / len(trees)


def compare_run_time(no_tree):
    tree1 = [randomly_create_new_tree(random.randint(11, 15))[1] for _ in range(no_tree)]
    log1 = [create_non_fitting_eventlog(tree, 1, 0.8) for tree in tree1]
    tree2 = [randomly_create_new_tree(random.randint(16, 20))[1] for _ in range(no_tree)]
    log2 = [create_non_fitting_eventlog(tree, 1, 0.8) for tree in tree2]
    tree3 = [randomly_create_new_tree(random.randint(21, 25))[1] for _ in range(no_tree)]
    log3 = [create_non_fitting_eventlog(tree, 1, 0.8) for tree in tree3]
    tree4 = [randomly_create_new_tree(random.randint(26, 30))[1] for _ in range(no_tree)]
    log4 = [create_non_fitting_eventlog(tree, 1, 0.8) for tree in tree4]
    tree5 = [randomly_create_new_tree(random.randint(31, 33))[1] for _ in range(no_tree)]
    log5 = [create_non_fitting_eventlog(tree, 1, 0.8) for tree in tree5]
    tree6 = [randomly_create_new_tree(random.randint(34, 35))[1] for _ in range(no_tree)]
    log6 = [create_non_fitting_eventlog(tree, 1, 0.8) for tree in tree6]
    l_without_lock = list(map(lambda tree_log: avg_runtime_without_lock(tree_log[0], tree_log[1]),
                              # [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4)]))
                            [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4), (tree5, log5), (tree6, log6)]))
    l_with_lock = list(map(lambda tree_log: avg_runtime_with_lock(tree_log[0], tree_log[1]),
                           # [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4)]))
                           [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4), (tree5, log5), (tree6, log6)]))
    plot_histogram_runtime(l_without_lock, l_with_lock)


def plot_histogram_runtime(list1, list2):
    """
    Compared the time of alignment of PT with lock and without lock
    :return:
    """
    label_list = ["10-15", "16-20", "21-25", "26-30"]
    label_list = ["10-15", "16-20", "21-25", "26-30", "31-33", "34-35"]
    x = range(len(list1))
    rects1 = plt.bar(x=x, height=list1, width=0.4, alpha=0.8, color="red", label="without Lock")
    rects2 = plt.bar(x=[i + 0.4 for i in x], height=list2, width=0.4, color="green", label="with Lock")
    plt.xlabel("Number of Node")
    plt.ylabel("Time(Seconds)")
    plt.xticks([i + 0.2 for i in x], label_list)
    plt.title("Compare Runtime of alignment with-out Lock")
    plt.legend()
    # for rect in rects1:
    #     height = rect.get_height()
    #     plt.text(rect.get_x() + rect.get_width() / 2, height + 1, str(height), ha="center", va="bottom")
    # for rect in rects2:
    #     height = rect.get_height()
    #     plt.text(rect.get_x() + rect.get_width() / 2, height + 1, str(height), ha="center", va="bottom")
    plt.show()

#################################################################################


def is_start_lock():
    return False


def is_end_lock():
    return False


def print_short_alignment(alignments):
    for align in alignments:
        # new_align = list(map(lambda ali: ali[1] == ">>", align['alignment'])
        # align["alignment"] = new_align
        pass


def compute_cost_and_time(tree, m_tree, log):
    print(tree)
    print(m_tree)
    # for t in log:
    #     for e in t:
    #         import pm4py
    #         print(e[pm4py.objects.log.util.xes.DEFAULT_NAME_KEY], end=", ")
    # print()
    pt_number.dfs_number(tree)
    pt_number.dfs_number(m_tree)

    _, sub1, sub2 = pt_compare(tree, m_tree)

    net, initial_marking, final_marking = pt_to_net_with_op.apply_with_operator(tree, {'PARAM_CHILD_LOCK': True})
    parameters = pt_to_net_with_op.get_parameters(net)
    parameters['PARAM_CHILD_LOCK'] = True
    alignments = align_factory.apply_log(log, net, initial_marking, final_marking, parameters)
    print(alignments)

    start = time.time()
    net2, initial_marking2, final_marking2 = pt_to_net_with_op.apply_with_operator(m_tree, {'PARAM_CHILD_LOCK': True})
    parameters = pt_to_net_with_op.get_parameters(net2)
    parameters['PARAM_CHILD_LOCK'] = True
    optimal_alignments = align_factory.apply_log(log, net2, initial_marking2, final_marking2, parameters)
    end = time.time()
    optimal_time = end - start
    optimal_cost = sum([align['cost'] for align in optimal_alignments])
    print(optimal_alignments)

    best_worst_cost = sum([(ali.factory.VERSIONS_COST['state_equation_a_star'](net2, initial_marking2,
                                                                               final_marking2, parameters)
                           + len(trace)) * 10000 for trace in log])

    start = time.time()
    repair_alignments = alignment_repair_with_operator_align(sub1, sub2, log, copy.deepcopy(alignments), parameters=parameters)
    end = time.time()
    repaired_time = end - start
    repaired_cost = sum([align['cost'] for align in repair_alignments])
    print(repair_alignments)

    start = time.time()
    scope_aligns = scope_expand(copy.deepcopy(alignments), sub1, True)
    scope_repaired_alignments = alignment_repair_with_operator_align(sub1, sub2, log, copy.deepcopy(scope_aligns), parameters=parameters)
    end = time.time()
    scope_repaired_time = end - start
    scope_repaired_cost = sum([align['cost'] for align in scope_repaired_alignments])
    print(scope_repaired_alignments)

    grade1 = 1 - (repaired_cost - optimal_cost) / (best_worst_cost - optimal_cost)
    grade2 = 1 - (scope_repaired_cost - optimal_cost) / (best_worst_cost - optimal_cost)
    return {"best_worst_cost": best_worst_cost, "repaired_cost": repaired_cost,
            "repaired_time": repaired_time, "optimal_cost": optimal_cost,
            "optimal_time": optimal_time, "scope_repair_cost": scope_repaired_cost,
            "scope_repair_time": scope_repaired_time, "grade1": grade1, "grade2": grade2}


def _11_15_mutated():
    pass


def _16_20_mutated():
    pass


def _21_25_mutated():
    pass


def _26_28_mutated():
    pass


def _29_30_mutated():
    pass


def alignment_quality():
    # 5 * 10 * 20
    tree1 = [randomly_create_new_tree(random.randint(15, 20))[1] for _ in range(5)]
    log1 = [create_non_fitting_eventlog(tree, 2, 0.7) for tree in tree1]
    m_tree1 = [[randomly_create_mutated_tree(tree) for _ in range(5)] for tree in tree1]
    for i in range(len(tree1)):
        for j in range(len(m_tree1[0])):
            result = compute_cost_and_time(tree1[i], m_tree1[i][j], log1[i])
            print(result)
    # example()


def create_event_log(events):
    trace = Trace()
    for e in list(events):
        event = Event()
        event["concept:name"] = e
        trace.append(event)
    return EventLog([trace])


def example():
    tree1 = pt_util.parse("->( +( ->( c, *( +( g, h ), d, τ ) ), X( a, b ) ), *( e, f, τ ) )")
    tree2 = pt_util.parse("->( +( ->( c, *( +( g, h ), d, τ ) ), X( a, b ) ), *( e, f, τ ), k )")
    log = create_event_log("chekekfefkek")
    result = compute_cost_and_time(tree1, tree2, log)
    print(result)
