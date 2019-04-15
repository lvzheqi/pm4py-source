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

from xlwt import Workbook


################################################################
# Compare Runtime of Alignment with/-out Lock


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


def plot_histogram_lock_runtime(list1, list2):
    """
    Compared the time of alignment of PT with lock and without lock
    :return:
    """
    label_list = ["10-15", "16-20", "21-25", "26-30"]
    # label_list = ["10-15", "16-20", "21-25", "26-30", "31-33", "34-35"]
    x = range(len(list1))
    rects1 = plt.bar(x=x, height=list1, width=0.4, alpha=0.8, color="red", label="without Lock")
    rects2 = plt.bar(x=[i + 0.4 for i in x], height=list2, width=0.4, color="green", label="with Lock")
    plt.xlabel("Number of Node")
    plt.ylabel("Time(Seconds)")
    plt.xticks([i + 0.2 for i in x], label_list)
    plt.title("Compare Runtime of Alignment with/-out Lock")
    plt.legend()
    # for rect in rects1:
    #     height = rect.get_height()
    #     plt.text(rect.get_x() + rect.get_width() / 2, height + 1, str(height), ha="center", va="bottom")
    # for rect in rects2:
    #     height = rect.get_height()
    #     plt.text(rect.get_x() + rect.get_width() / 2, height + 1, str(height), ha="center", va="bottom")
    plt.show()


def compare_run_time():
    no_tree = 10
    tree1 = [randomly_create_new_tree(random.randint(11, 15))[1] for _ in range(no_tree)]
    log1 = [create_non_fitting_eventlog(tree, 10, 0.8) for tree in tree1]
    tree2 = [randomly_create_new_tree(random.randint(16, 20))[1] for _ in range(no_tree)]
    log2 = [create_non_fitting_eventlog(tree, 10, 0.8) for tree in tree2]
    tree3 = [randomly_create_new_tree(random.randint(21, 25))[1] for _ in range(no_tree)]
    log3 = [create_non_fitting_eventlog(tree, 10, 0.8) for tree in tree3]
    tree4 = [randomly_create_new_tree(random.randint(26, 30))[1] for _ in range(no_tree)]
    log4 = [create_non_fitting_eventlog(tree, 10, 0.8) for tree in tree4]
    tree5 = [randomly_create_new_tree(random.randint(31, 33))[1] for _ in range(no_tree)]
    log5 = [create_non_fitting_eventlog(tree, 10, 0.8) for tree in tree5]
    tree6 = [randomly_create_new_tree(random.randint(34, 35))[1] for _ in range(no_tree)]
    log6 = [create_non_fitting_eventlog(tree, 10, 0.8) for tree in tree6]
    l_without_lock = list(map(lambda tree_log: avg_runtime_without_lock(tree_log[0], tree_log[1]),
                              [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4)]))
                            # [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4), (tree5, log5), (tree6, log6)]))
    l_with_lock = list(map(lambda tree_log: avg_runtime_with_lock(tree_log[0], tree_log[1]),
                           [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4)]))
                           # [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4), (tree5, log5), (tree6, log6)]))
    plot_histogram_lock_runtime(l_without_lock, l_with_lock)

#################################################################################


def plot_histogram_align_runtime(list1, list2, list3, list4):
    """
    Compared the time of alignment of PT with lock and without lock
    :return:
    """
    label_list = ["10-15", "16-20", "21-25", "26-30"]
    label_list = ["10-15", "16-20", "21-25", "26-30", "31-33", "34-35"]
    x = range(len(list1))
    rects1 = plt.bar(x=x, height=list1, width=0.3, alpha=0.8, color="red", label="A* without lock")
    rects2 = plt.bar(x=[i + 0.3 for i in x], height=list2, width=0.3, color="yellow", label="A* with lock")
    rects3 = plt.bar(x=[i + 0.6 for i in x], height=list3, width=0.3, color="green", label="Align Repair")
    rects4 = plt.bar(x=[i + 0.9 for i in x], height=list4, width=0.3, color="blue", label="Align Repair after Scope")

    plt.xlabel("Number of Node")
    plt.ylabel("Time(Seconds)")
    plt.xticks([i + 0.2 for i in x], label_list)
    plt.title("Compare Runtime of Alignment with different Methods")
    plt.legend()
    # for rect in rects1:
    #     height = rect.get_height()
    #     plt.text(rect.get_x() + rect.get_width() / 2, height + 1, str(height), ha="center", va="bottom")
    # for rect in rects2:
    #     height = rect.get_height()
    #     plt.text(rect.get_x() + rect.get_width() / 2, height + 1, str(height), ha="center", va="bottom")
    plt.show()


#################################################################################

def compute_cost_and_time(tree, m_tree, log):

    pt_number.dfs_number(tree)
    pt_number.dfs_number(m_tree)

    net, initial_marking, final_marking = pt_to_net_with_op.apply_with_operator(tree, {'PARAM_CHILD_LOCK': True})
    parameters = pt_to_net_with_op.get_parameters(net)
    parameters['PARAM_CHILD_LOCK'] = True
    alignments = align_factory.apply_log(log, net, initial_marking, final_marking, parameters)

    start = time.time()
    net2, initial_marking2, final_marking2 = pt_to_net_with_op.apply_with_operator(m_tree, {'PARAM_CHILD_LOCK': True})
    parameters = pt_to_net_with_op.get_parameters(net2)
    parameters['PARAM_CHILD_LOCK'] = True
    optimal_alignments = align_factory.apply_log(log, net2, initial_marking2, final_marking2, parameters)
    end = time.time()
    optimal_time = end - start
    optimal_cost = sum([align['cost'] for align in optimal_alignments])

    best_worst_cost = sum([ali.factory.VERSIONS_COST['state_equation_a_star'](net2, initial_marking2,
                                                                              final_marking2, parameters) * 2
                          + len(trace) * 5 for trace in log])

    start = time.time()
    repair_alignments = alignment_repair_with_operator_align(tree, m_tree, log, copy.deepcopy(alignments),
                                                             parameters=parameters)
    end = time.time()
    repaired_time = end - start
    repaired_cost = sum([align['cost'] for align in repair_alignments])

    start = time.time()
    scope_aligns = scope_expand(copy.deepcopy(alignments), tree, m_tree, True)
    scope_repaired_alignments = alignment_repair_with_operator_align(tree, m_tree, log, copy.deepcopy(scope_aligns),
                                                                     parameters=parameters)
    end = time.time()
    scope_repaired_time = end - start
    scope_repaired_cost = sum([align['cost'] for align in scope_repaired_alignments])

    print_intermediate_result(tree, m_tree, log, alignments, optimal_alignments, repair_alignments,
                              scope_repaired_alignments)

    grade1 = 1 - (repaired_cost - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1
    grade2 = 1 - (scope_repaired_cost - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1

    return {"best_worst_cost": best_worst_cost, "repaired_cost": repaired_cost,
            "repaired_time": repaired_time, "optimal_cost": optimal_cost,
            "optimal_time": optimal_time, "scope_repair_cost": scope_repaired_cost,
            "scope_repair_time": scope_repaired_time, "grade1": grade1, "grade2": grade2}


def alignment_quality_log_based_on_tree1():
    file = Workbook(encoding='utf-8')

    # creat_non_fitting_based_on_tree1(file, "Node11-15", [11, 15])
    # creat_non_fitting_based_on_tree1(file, "Node16-20", [16, 20])
    # creat_non_fitting_based_on_tree1(file, "Node21-25", [21, 25])
    creat_non_fitting_based_on_tree1(file, "Node26-30", [26, 30])

    file.save('L11_data.xls')


def creat_non_fitting_based_on_tree1(file, name, node_num):
    num = ["node", "best_worst_cost", "optimal_cost", "optimal_time", "repaired_cost", "repaired_time",
           "scope_repair_cost", "scope_repair_time", "grade1", "grade2"]
    tree_num, mutated_num, log_num, non_fit_pro = 1, 2, 10, 0.8
    row_index = 0
    table = file.add_sheet(name)
    tree = [randomly_create_new_tree(random.randint(node_num[0], node_num[1]))[1] for _ in range(tree_num)]
    m_tree = [[randomly_create_mutated_tree(tree) for _ in range(mutated_num)] for tree in tree]
    log = [create_non_fitting_eventlog(tree, log_num, non_fit_pro) for tree in tree]
    for i in range(len(tree)):
        node_num = len(pt_number.get_leaves_labels(tree[i]))
        for j in range(len(m_tree[0])):
            print_tree_and_trace(tree[i], m_tree[i][j], log[i])
            result = compute_cost_and_time(tree[i], m_tree[i][j], log[i])
            print_tree_align_compare(result)
            result["node"] = node_num
            for col in range(len(num)):
                table.write(row_index, col, result[num[col]])
            row_index += 1


def alignment_quality_log_based_on_tree2():
    # 5 * 10 * 20
    # file = Workbook(encoding='utf-8')
    #
    # # creat_non_fitting_based_on_tree2(file, "Node11-15", [11, 15])
    # # creat_non_fitting_based_on_tree2(file, "Node16-20", [16, 20])
    # # creat_non_fitting_based_on_tree2(file, "Node21-25", [21, 25])
    # creat_non_fitting_based_on_tree2(file, "Node26-30", [26, 30])
    #
    # file.save('L22_data.xls')
    example()


def creat_non_fitting_based_on_tree2(file, name, node_num):
    num = ["node", "best_worst_cost", "optimal_cost", "optimal_time", "repaired_cost", "repaired_time",
           "scope_repair_cost", "scope_repair_time", "grade1", "grade2"]
    tree_num, mutated_num, log_num, non_fit_pro = 1, 2, 10, 0.8
    row_index = 0
    table = file.add_sheet(name)
    tree = [randomly_create_new_tree(random.randint(node_num[0], node_num[1]))[1] for _ in range(tree_num)]
    m_tree = [[randomly_create_mutated_tree(tree) for _ in range(mutated_num)] for tree in tree]
    log = [[create_non_fitting_eventlog(m_tree, log_num, non_fit_pro) for m_tree in m_tr4] for m_tr4 in m_tree]
    for i in range(len(tree)):
        node_num = len(pt_number.get_leaves_labels(tree[i]))
        for j in range(len(m_tree[0])):
            print_tree_and_trace(tree[i], m_tree[i][j], log[i][j])
            result = compute_cost_and_time(tree[i], m_tree[i][j], log[i][j])
            print_tree_align_compare(result)
            result["node"] = node_num
            for col in range(len(num)):
                table.write(row_index, col, result[num[col]])
            row_index += 1


def create_event_log(log):
    traces = list()
    for events in log:
        trace = Trace()
        for e in list(events):
            event = Event()
            event["concept:name"] = e
            trace.append(event)
        traces.append(trace)
    return EventLog(traces)


def example():
    tree1 = pt_util.parse("X( *( X( c, d ), b, τ ), a )")
    tree2 = pt_util.parse("X( *( τ, b, τ ), a )")
    log = create_event_log(["ab"])
    # log = create_event_log([ "d"])
    # net, initial_marking, final_marking = pt_to_net_with_op.apply_with_operator(tree1, {'PARAM_CHILD_LOCK': True})
    # parameters = pt_to_net_with_op.get_parameters(net)
    # parameters['PARAM_CHILD_LOCK'] = True
    # alignments = align_factory.apply_log(log, net, initial_marking, final_marking, parameters)
    # print_short_alignment(alignments)

    # log = create_non_fitting_eventlog(tree2, 100, 0.7)
    result = compute_cost_and_time(tree1, tree2, log)
    print_tree_align_compare(result)


def print_tree_align_compare(result):
    print("optimal cost: " + str(result["optimal_cost"]), ", repaired cost: " + str(result["repaired_cost"]),
          ", scope repaired cost: " + str(result["scope_repair_cost"]))
    print("optimal time: " + str(result["optimal_time"]), ", repaired time: " + str(result["repaired_time"]),
          ", scope repaired time: " + str(result["scope_repair_time"]))
    print("repaired grade: " + str(result["grade1"]), ", scope repaired grade: " + str(result["grade2"]))


def is_slient_move(align):
    align = align[1]
    if align[0] == ">>" and (align[1] is None or align[1].endswith("_s") or align[1].endswith("_e")):
        return False
    return True


def print_short_alignment(alignments):
    for align in alignments:
        new_align = list(filter(is_slient_move, align['alignment']))
        align["alignment"] = list(map(lambda ali: ali[1], new_align))
    print(alignments)


def print_intermediate_result(tree, m_tree, log, alignments, optimal_alignments, repair_alignments,
                              scope_repaired_alignments):
    # print_tree_and_trace(tree, m_tree, log)
    print_short_alignment(alignments)
    print_short_alignment(optimal_alignments)
    print_short_alignment(repair_alignments)
    print_short_alignment(scope_repaired_alignments)


def print_tree_and_trace(tree, m_tree, log):
    print(tree)
    print(m_tree)
    for t in log:
        for e in t:
            import pm4py
            print(e[pm4py.objects.log.util.xes.DEFAULT_NAME_KEY], end="")
        print(end=", ")
    print("")




# X( *( b, ->( *( ->( o, p ), n, τ ), i, +( X( c, d ), ->( g, h ), X( j, k ), ->( X( e, f ), +( l, m ) ) ) ), τ ), a )
# X( *( b, ->( *( ->( o, p ), n, τ ), i, +( ->( g, h ), X( j, k ), ->( X( e, f ), +( l, m ) ) ) ), τ ), a )
# c, , bq, , , bknqoqpqnqo, d, , j, p
