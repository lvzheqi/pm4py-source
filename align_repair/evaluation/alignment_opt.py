import time
import random
import pandas as pd

from pm4py.objects.process_tree import util as pt_utils
from align_repair.process_tree.stochastic_generation import stochastic_pt_mutate as pt_mutate
from align_repair.process_tree.stochastic_generation import non_fitting_log_create as log_create
from align_repair.process_tree.stochastic_generation import stochastic_pt_create as pt_create
from align_repair.evaluation.execl_operation import object_read
from align_repair.repair.optimal import align_repair_opt, align_repair, align_repair2
from align_repair.evaluation.config import PT_FILE_NAME, LOG_FILE_NAME, MPT_NUM
from align_repair.evaluation import alignment_on_pt, print_event_log, create_event_log, alignment_default_on_pt, \
    get_best_cost_on_pt


def compute_alignment(apply, option):
    """
    Create specified number of event logs of each tree, not including Empty Trace.

    The event log in the same column belong to the same process tree.

    Records Format (Column)
    ---------------
    Alignments, time without lock, time with lock, optimal cost, best_worst_cost
    """
    optimal_time, optimal_cost, best_worst_cost = list(), list(), list()
    ra_time, ra_cost, grade = list(), list(), list()
    trees = object_read.read_trees_from_file(PT_FILE_NAME, 0)
    m_trees = object_read.read_trees_from_file(PT_FILE_NAME, 1)
    logs = object_read.read_logs_from_file(LOG_FILE_NAME)
    for row, tree in enumerate(m_trees):
        if row == 6:
            print(row)
            log = logs[row // MPT_NUM]
            tree = trees[row // MPT_NUM]
            m_tree = m_trees[row]
            info = align_info(tree, m_tree, log, apply, option)
            optimal_time.append(info[0])
            optimal_cost.append(info[1])
            best_worst_cost.append(info[2])
            ra_time.append(info[3])
            ra_cost.append(info[4])
            grade.append(info[5])
    df = pd.DataFrame({"optimal time": optimal_time, "optimal cost": optimal_cost, "best worst cost": best_worst_cost,
                       "repair align time": ra_time, "repair align cost": ra_cost, "grade": grade})
    df.to_csv("xls/align_repair.csv")


def align_info(tree, m_tree, log, apply, option):
    print(tree)
    print(m_tree)
    print_event_log(log)

    start = time.time()
    alignment_on_pt(tree, log)
    alignments = alignment_on_pt(m_tree, log)
    print(alignments)
    end = time.time()
    optimal_time = end - start
    print('optimal time:', end - start)
    optimal_cost = sum([align['cost'] for align in alignments])
    print('optimal cost', optimal_cost)

    best_worst_cost = get_best_cost_on_pt(tree, log)

    start = time.time()
    parameters = {'ret_tuple_as_trans_desc': True}
    alignments, repair_alignments = apply(tree, m_tree, log, parameters, option)
    end = time.time()
    print(repair_alignments)
    ra_time = end - start
    print('optimal time:', end - start)
    ra_cost = sum([align['cost'] for align in repair_alignments])
    grade = 1 - (ra_cost - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1
    print('optimal cost', ra_cost)
    print('grade', grade)
    # print('---------------------------------')
    # optimal_time, optimal_cost, best_worse_cost, ra_time, ra_cost, grade
    return optimal_time, optimal_cost, best_worst_cost, ra_time, ra_cost, grade


def compute_alignment1(option, apply):
    tree_num, mutated_num, log_num, non_fit_pro = 3, 1, 5, 0.9
    node_num = [20, 25]
    tree = [pt_create.apply(random.randint(node_num[0], node_num[1])) for _ in range(tree_num)]
    m_tree = [[pt_mutate.apply(tree) for _ in range(mutated_num)] for tree in tree]
    log = [log_create.apply(tree, log_num, non_fit_pro) for tree in tree]
    for i in range(len(tree)):
        for j in range(len(m_tree[0])):
            align_info(tree[i], m_tree[i][j], log[i], apply, option)


def two_method_compare():
    pf0 = pd.read_csv("xls/align_repair.csv", header=0)
    pf1 = pd.read_csv("xls/align_repair2.csv", header=0)
    time_com = pd.DataFrame({"method1": pf0['repair align time'], "method2": pf1['repair align time']})
    # grade = pd.DataFrame({"method1": pf0['grade'], "method2": pf1['grade']})

    import matplotlib.pyplot as plt
    time_com.plot()
    plt.ylabel("Time")
    # grade.plot()
    plt.title("Compare Time with Different Option")
    plt.savefig("xls/TwoMethodCompare")


def grade_compare():
    import matplotlib.pyplot as plt
    pf0 = pd.read_csv("xls/align_repair.csv", header=0)
    pf1 = pd.read_csv("xls/opt_align.csv", header=0)
    pf2 = pd.read_csv("xls/opt_align_option2.csv", header=0)
    grade = pd.DataFrame({"align repair": pf0['grade'], "expand align repair grade1": pf1['grade'],
                          "expand align repair grade2": pf2['grade']})
    grade.plot()
    plt.ylabel("Grade")
    plt.title("Compare Grade with Different Option")
    # plt.ylim(0.6, 1)
    plt.savefig("xls/CompareGrade1")


def time_compare():
    import matplotlib.pyplot as plt
    pf0 = pd.read_csv("xls/align_repair.csv", header=0)
    pf1 = pd.read_csv("xls/opt_align.csv", header=0)
    pf2 = pd.read_csv("xls/opt_align_option2.csv", header=0)
    grade = pd.DataFrame({"optimal align time": pf0['optimal time'],
                          "repair align time": pf0['repair align time'],
                          "expand repair align time option1": pf1['repair align time'],
                          "expand repair align time option2": pf2['repair align time']})
    grade.plot()
    plt.ylabel("Time")
    plt.title("Compare Time with Different Option")
    plt.savefig("xls/CompareTime1")


if __name__ == "__main__":
    # grade_compare()
    # time_compare()
    # two_method_compare()
    # compute_alignment(align_repair_opt.apply, 2)
    tree1 = pt_utils.parse("*( a, ->( X( b, ->( c, d ) ), e, f ), τ )")
    tree2 = pt_utils.parse("*( a, ->( *( b, ->( c, d ), τ ), e, f ), τ )")
    logs_ = create_event_log("fchbcfbeahbbfhb")
    # deeef, dbhceh
    align_info(tree1, tree2, logs_, align_repair_opt.apply, 2)
    # align_info(tree1, tree2, logs_, align_repair2.apply, 1)
    # alignments = alignment_on_pt(tree2, logs)
    # optimal_cost = sum([align['cost'] for align in alignments])
    # print(list(map(lambda a: a[1], alignments[0]['alignment'])))
    # # print(alignments)
    # print('optimal cost', optimal_cost)
    # alignments = alignment_on_loop_lock_pt(tree2, logs)
    # # print(list(map(lambda a: a[1], alignments[0]['alignment'])))
    # print(alignments[0]['alignment'])
    # optimal_cost = sum([align['cost'] for align in alignments])
    # print('optimal cost', optimal_cost)
    # alignments = alignment_on_lock_pt(tree2, logs)
    # # print(list(map(lambda a: a[1], alignments[0]['alignment'])))
    # print(alignments[0]['alignment'])
    # optimal_cost = sum([align['cost'] for align in alignments])
    # print('optimal cost', optimal_cost)
