import time
import random
import pandas as pd

from pm4py.objects.process_tree import util as pt_utils
from align_repair.process_tree.stochastic_generation import stochastic_pt_mutate as pt_mutate
from align_repair.process_tree.stochastic_generation import non_fitting_log_create as log_create
from align_repair.process_tree.stochastic_generation import stochastic_pt_create as pt_create
from align_repair.evaluation.execl_operation import object_read
from align_repair.repair.optimal import align_repair_opt
from align_repair.evaluation.config import PT_FILE_NAME, LOG_FILE_NAME, MPT_NUM
from align_repair.evaluation import alignment_on_pt, print_event_log, get_best_cost_on_pt, create_event_log


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
    df.to_csv("data/align_repair.csv")


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
    tree_num, mutated_num, log_num, non_fit_pro = 500, 5, 5, 0.2
    node_num = [20, 25]
    tree = [pt_create.apply(random.randint(node_num[0], node_num[1])) for _ in range(tree_num)]
    m_tree = [[pt_mutate.apply(tree) for _ in range(mutated_num)] for tree in tree]
    log = [log_create.apply(tree, log_num, non_fit_pro) for tree in tree]
    for i in range(len(tree)):
        for j in range(len(m_tree[0])):
            align_info(tree[i], m_tree[i][j], log[i], apply, option)


if __name__ == "__main__":
    # grade_compare()
    # time_compare()
    # two_method_compare()
    # compute_alignment(align_repair_opt.apply, 2)
    tree1 = pt_utils.parse("*( a, ->( X( b, ->( c, d ) ), e, f ), τ )")
    tree2 = pt_utils.parse("*( a, ->( *( b, ->( c, d ), τ ), e, f ), τ )")
    logs_ = log_create.apply(tree1, 1, 0.2)
    # logs_ = create_event_log("bedabefa")
    # deeef, dbhceh
    align_info(tree1, tree2, logs_, align_repair_opt.apply, 2)
