import time
import random
# import copy

from pm4py.algo.conformance import alignments as ali
from pm4py.objects.process_tree import util as pt_util

from align_repair.stochastic_generation.stochastic_pt_generation import randomly_create_new_tree
from align_repair.stochastic_generation.non_fitting_eventlog_generation import create_non_fitting_eventlog
from align_repair.stochastic_generation.stochastic_mutated_pt import randomly_create_mutated_tree
from align_repair.pt_manipulate import pt_number, utils as pt_man_util
from align_repair.repair.align_repair import alignment_repair_with_operator_align
from align_repair.repair.scope_expand import scope_expand
from align_repair.repair.general_scope_expand import general_scope_expand
from align_repair.evaluation import create_event_log, print_short_alignment, \
    alignment_on_lock_pt, get_best_cost_on_pt, print_event_log

from xlwt import Workbook


def compute_cost_and_time(tree, m_tree, log):

    pt_number.pt_number(tree, 'D', 1)
    pt_number.pt_number(m_tree, 'D', 1)

    alignments = alignment_on_lock_pt(tree, log)

    start = time.time()
    optimal_alignments = alignment_on_lock_pt(m_tree, log)
    end = time.time()
    optimal_time = end - start
    optimal_cost = sum([align['cost'] for align in optimal_alignments])

    best_worst_cost = sum([get_best_cost_on_pt(tree) + len(trace) * ali.utils.STD_MODEL_LOG_MOVE_COST for trace in log])

    start = time.time()
    repair_alignments = alignment_repair_with_operator_align(tree, m_tree, log, alignments)
    end = time.time()
    repaired_time = end - start
    repaired_cost = sum([align['cost'] for align in repair_alignments])

    start = time.time()
    scope_aligns = scope_expand(alignments, tree, m_tree)
    scope_repaired_alignments = alignment_repair_with_operator_align(tree, m_tree, log, scope_aligns)
    end = time.time()
    scope_repaired_time = end - start
    scope_repaired_cost = sum([align['cost'] for align in scope_repaired_alignments])

    start = time.time()
    scope_aligns = general_scope_expand(alignments, tree, m_tree)
    g_scope_repaired_alignments = alignment_repair_with_operator_align(tree, m_tree, log, scope_aligns)
    end = time.time()
    g_scope_repaired_time = end - start
    g_scope_repaired_cost = sum([align['cost'] for align in g_scope_repaired_alignments])
    print(g_scope_repaired_time, g_scope_repaired_cost)

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

    creat_non_fitting_based_on_tree1(file, "Node11-15", [11, 15])
    # creat_non_fitting_based_on_tree1(file, "Node16-20", [16, 20])
    # creat_non_fitting_based_on_tree1(file, "Node21-25", [21, 25])
    # creat_non_fitting_based_on_tree1(file, "Node26-30", [26, 30])

    # file.save('L11_data.xls')


def creat_non_fitting_based_on_tree1(file, name, node_num):
    num = ["node", "best_worst_cost", "optimal_cost", "optimal_time", "repaired_cost", "repaired_time",
           "scope_repair_cost", "scope_repair_time", "grade1", "grade2"]
    tree_num, mutated_num, log_num, non_fit_pro = 5, 1, 5, 0.8
    row_index = 0
    table = file.add_sheet(name)
    tree = [randomly_create_new_tree(random.randint(node_num[0], node_num[1])) for _ in range(tree_num)]
    m_tree = [[randomly_create_mutated_tree(tree) for _ in range(mutated_num)] for tree in tree]
    log = [create_non_fitting_eventlog(tree, log_num, non_fit_pro) for tree in tree]
    for i in range(len(tree)):
        node_num = pt_man_util.get_non_none_leaves_number(tree[i])
        for j in range(len(m_tree[0])):
            result = compute_cost_and_time(tree[i], m_tree[i][j], log[i])
            print_tree_align_compare(result)
            result["node"] = node_num
            for col in range(len(num)):
                table.write(row_index, col, result[num[col]])
            row_index += 1


def alignment_quality_log_based_on_tree2():
    # 5 * 10 * 20
    file = Workbook(encoding='utf-8')

    creat_non_fitting_based_on_tree2(file, "Node11-15", [11, 15])
    # creat_non_fitting_based_on_tree2(file, "Node16-20", [16, 20])
    # creat_non_fitting_based_on_tree2(file, "Node21-25", [21, 25])
    # creat_non_fitting_based_on_tree2(file, "Node26-30", [26, 30])

    # file.save('L22_data.xls')
    # example()


def creat_non_fitting_based_on_tree2(file, name, node_num):
    num = ["node", "best_worst_cost", "optimal_cost", "optimal_time", "repaired_cost", "repaired_time",
           "scope_repair_cost", "scope_repair_time", "grade1", "grade2"]
    tree_num, mutated_num, log_num, non_fit_pro = 5, 1, 5, 0.8
    row_index = 0
    table = file.add_sheet(name)
    tree = [randomly_create_new_tree(random.randint(node_num[0], node_num[1])) for _ in range(tree_num)]
    m_tree = [[randomly_create_mutated_tree(tree) for _ in range(mutated_num)] for tree in tree]
    log = [[create_non_fitting_eventlog(m_tree, log_num, non_fit_pro) for m_tree in m_tr4] for m_tr4 in m_tree]
    for i in range(len(tree)):
        node_num = pt_man_util.get_non_none_leaves_number(tree[i])
        for j in range(len(m_tree[0])):
            result = compute_cost_and_time(tree[i], m_tree[i][j], log[i][j])
            print_tree_align_compare(result)
            result["node"] = node_num
            for col in range(len(num)):
                table.write(row_index, col, result[num[col]])
            row_index += 1


def test_compute_cost_time():
    tree1 = pt_util.parse("*( a, X( f, g, +( c, X( d, e ) ), b ), τ )")
    tree2 = pt_util.parse("*( a, X( f, g, k, +( c, X( d, e ) ), b ), τ )")
    log = create_event_log("ak")

    result = compute_cost_and_time(tree1, tree2, log)
    print_tree_align_compare(result)


def print_tree_align_compare(result):
    print("optimal cost: " + str(result["optimal_cost"]), ", repaired cost: " + str(result["repaired_cost"]),
          ", scope repaired cost: " + str(result["scope_repair_cost"]))
    print("optimal time: " + str(result["optimal_time"]), ", repaired time: " + str(result["repaired_time"]),
          ", scope repaired time: " + str(result["scope_repair_time"]))
    print("repaired grade: " + str(result["grade1"]), ", scope repaired grade: " + str(result["grade2"]))


def print_intermediate_result(tree, m_tree, log, alignments, optimal_alignments, repair_alignments,
                              scope_repaired_alignments):

    print("Tree1:", tree)
    print("Tree2:", m_tree)
    print_event_log(log)
    print_short_alignment(alignments, "AlignOnTree1: ")
    print_short_alignment(optimal_alignments, "AlignOnTree2: ")
    print_short_alignment(repair_alignments, "RepairAlign: ")
    print_short_alignment(scope_repaired_alignments, "ScopeExpand: ")


if __name__ == "__main__":
    alignment_quality_log_based_on_tree1()
    alignment_quality_log_based_on_tree2()
