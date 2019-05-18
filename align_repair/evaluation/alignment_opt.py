import time
import random

from pm4py.objects.process_tree import util as pt_utils

from align_repair.process_tree.stochastic_generation import stochastic_pt_mutate as pt_mutate
from align_repair.process_tree.stochastic_generation import non_fitting_log_create as log_create
from align_repair.process_tree.stochastic_generation import stochastic_pt_create as pt_create
from align_repair.evaluation.execl_operation import object_read
from align_repair.process_tree.alignments import detect_range
from align_repair.evaluation.config import PT_FILE_NAME, LOG_FILE_NAME, ALIGN_FILE_NAME, ALIGN_SHEET_NAME, \
    PT_NUM, REPAIR_SHEET_NAME, MPT_NUM
from align_repair.evaluation import alignment_on_pt, print_event_log, alignment_default_on_pt,\
    alignment_on_loop_lock_pt, alignment_on_lock_pt, create_event_log


def compute_alignment():
    """
    Create specified number of event logs of each tree, not including Empty Trace.

    The event log in the same column belong to the same process tree.

    Records Format (Column)
    ---------------
    Alignments, time without lock, time with lock, optimal cost, best_worst_cost
    """
    trees = object_read.read_trees_from_file('../'+PT_FILE_NAME, 0)
    m_trees = object_read.read_trees_from_file('../'+PT_FILE_NAME, 1)
    logs = object_read.read_logs_from_file('../'+LOG_FILE_NAME)
    for row, tree in enumerate(m_trees):
        if 62 >= row >= 61:
            log = logs[row // MPT_NUM]
            tree = trees[row // MPT_NUM]
            m_tree = m_trees[row]
            align_info(tree, m_tree, log)


def align_info(tree, m_tree, log):

    print(tree)
    print(m_tree)
    print_event_log(log)
    alignments = alignment_default_on_pt(m_tree, log)
    optimal_cost = sum([align['cost'] for align in alignments])
    print(alignments)
    print('optimal cost', optimal_cost)
    alignments = alignment_on_loop_lock_pt(m_tree, log)
    optimal_cost = sum([align['cost'] for align in alignments])
    print('optimal cost', optimal_cost)
    print(alignments)
    alignments = alignment_on_lock_pt(m_tree, log)
    optimal_cost = sum([align['cost'] for align in alignments])
    print('optimal cost', optimal_cost)
    print(alignments)

    start = time.time()
    alignment_on_pt(tree, log)
    alignments = alignment_on_pt(m_tree, log)
    end = time.time()
    print('optimal time:', end - start)
    optimal_cost = sum([align['cost'] for align in alignments])
    print('optimal cost', optimal_cost)

    start = time.time()
    alignments, repair_alignments = detect_range.apply(tree, m_tree, log)
    end = time.time()
    print('optimal time:', end - start)
    optimal_cost = sum([align['cost'] for align in repair_alignments])
    print('optimal cost', optimal_cost)
    print('---------------------------------')


def compute_alignment1():
    tree_num, mutated_num, log_num, non_fit_pro = 10, 1, 5, 0.9
    node_num = [20, 25]
    tree = [pt_create.apply(random.randint(node_num[0], node_num[1])) for _ in range(tree_num)]
    m_tree = [[pt_mutate.apply(tree) for _ in range(mutated_num)] for tree in tree]
    log = [log_create.apply(tree, log_num, non_fit_pro) for tree in tree]
    for i in range(len(tree)):
        for j in range(len(m_tree[0])):
            align_info(tree[i], m_tree[i][j], log[i])


if __name__ == "__main__":
    # compute_alignment()
    # tree1 = pt_utils.parse("X( +( j, k, a ), *( X( b, +( h, i ) ), *( X( c, d ), ->( +( f, g ), e ), τ ), τ ) )")
    # tree2 = pt_utils.parse("X( +( j, k, a ), *( X( b, +( h, i ) ), *( X( c, d ), ->( *( f, g, τ ), e ), τ ), τ ) )")
    # logs = create_event_log("chbdf")
    # # align_info(tree1, tree2, logs)
    # alignments = alignment_default_on_pt(tree2, logs)
    # optimal_cost = sum([align['cost'] for align in alignments])
    # print(list(map(lambda a: a[1], alignments[0]['alignment'])))
    # # print(alignments)
    # print('optimal cost', optimal_cost)
    # alignments = alignment_on_loop_lock_pt(tree2, logs)
    # # print(list(map(lambda a: a[1], alignments[0]['alignment'])))
    # print(alignments[0]['alignment'])
    # optimal_cost = sum([align['cost'] for align in alignments])
    # print('optimal cost', optimal_cost)
    tree1 = pt_utils.parse("X( ->( g, +( ->( i, j ), h ), k, l ), *( ->( e, f ), d, τ ), *( ->( b, c ), a, τ ) )")
    tree2 = pt_utils.parse("X( *( ->( b, c ), a, τ ), ->( g, +( j, h ), k, l ), *( ->( e, f ), d, τ ))")
    logs = create_event_log("bf, eog, jdof, ghglljo, mhaliol, boch, bc, efo, eof, hki, ")
    # align_info(tree1, tree2, logs)
    alignments = alignment_default_on_pt(tree2, logs)
    optimal_cost = sum([align['cost'] for align in alignments])
    print(list(map(lambda a: a[1], alignments[0]['alignment'])))
    # print(alignments)
    print('optimal cost', optimal_cost)
    alignments = alignment_on_pt(tree2, logs)
    # print(list(map(lambda a: a[1], alignments[0]['alignment'])))
    print(alignments[0]['alignment'])
    optimal_cost = sum([align['cost'] for align in alignments])
    print('optimal cost', optimal_cost)
