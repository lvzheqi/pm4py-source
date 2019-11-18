import time
import pandas as pd

from pm4py.objects.process_tree import util as pt_utils
from repair_alignment.deprecation.execl_operation import object_read
from repair_alignment.algo.repair import repair
from repair_alignment.algo.repair.version import Version
from repair_alignment.deprecation.execl_operation.config import PT_FILE_NAME, LOG_FILE_NAME, MPT_NUM
from repair_alignment.evaluation import alignment_on_pt, print_event_log, get_best_cost_on_pt, create_event_log

PATH = '../../data/D1/'
PT_RANGE = [(11, 15), (16, 18), (19, 21), (22, 24)]
SHEET_NAME = [str(i) + "-" + str(j) for (i, j) in PT_RANGE]


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
    df.to_csv("data/repair_alignment.csv")


def align_info(tree, m_tree, log, version, option):
    print(tree)
    print(m_tree)
    print_event_log(log)

    start = time.time()
    alignment_on_pt(tree, log)
    alignments = alignment_on_pt(m_tree, log)
    end = time.time()
    print(alignments)
    optimal_time = end - start
    print('optimal time:', end - start)
    optimal_cost = sum([align['cost'] for align in alignments])
    print('optimal cost', optimal_cost)

    best_worst_cost = get_best_cost_on_pt(m_tree, log)
    print('best worst:', best_worst_cost)
    start = time.time()
    parameters = {'ret_tuple_as_trans_desc': True}
    alignments, repair_alignments = repair.apply(tree, m_tree, log, version, parameters, option)
    end = time.time()
    print(alignments)
    print(repair_alignments)
    ra_time = end - start
    print('optimal time:', end - start)
    ra_cost = sum([align['cost'] for align in repair_alignments])
    grade = 1 - (ra_cost - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1
    print('optimal cost', ra_cost)
    print('grade:', grade)
    # print('---------------------------------')
    # optimal_time, optimal_cost, best_worse_cost, ra_time, ra_cost, grade
    return optimal_time, optimal_cost, best_worst_cost, ra_time, ra_cost, grade


def repair_align_compare(tree, m_tree, log):
    alignment_on_pt(tree, log)
    alignments = alignment_on_pt(m_tree, log)
    optimal_cost = sum([align['cost'] for align in alignments])
    print('optimal cost', optimal_cost)

    best_worst_cost = get_best_cost_on_pt(m_tree, log)

    alignments = alignment_on_pt(tree, log)

    parameters = {'ret_tuple_as_trans_desc': True}
    alignments, repair_alignments = repair.apply_with_alignments(tree, m_tree, log, alignments,
                                                                 Version.IAR_LINEAR, parameters, 1)
    print(repair_alignments)
    alignments2, repair_alignments2 = repair.apply_with_alignments(tree, m_tree, log, alignments,
                                                                   Version.IAR_TOP_DOWN, parameters, 1)
    print(repair_alignments2)

    ra_cost = sum([align['cost'] for align in repair_alignments])
    grade = 1 - (ra_cost - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1
    print('repair1 cost', ra_cost)

    ra_cost2 = sum([align['cost'] for align in repair_alignments2])
    grade2 = 1 - (ra_cost2 - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1
    print('repair2 cost', ra_cost2)

    if grade != grade2:
        print(grade, grade2)
        print(tree)
        print(m_tree)
        print_event_log(log)
        print("Oh my God")
        exit(-1)
    # print('---------------------------------')
    # optimal_time, optimal_cost, best_worse_cost, ra_time, ra_cost, grade


def compute_alignment1(version, option):
    # tree_num, mutated_num, log_num, non_fit_pro = 10, 5, 5, 0.2
    # node_num = [20, 25]
    # tree = [pt_create.apply(random.randint(node_num[0], node_num[1])) for _ in range(tree_num)]
    # m_tree = [[pt_mutate.apply(tree) for _ in range(mutated_num)] for tree in tree]
    # log = [log_create.apply(tree, log_num, non_fit_pro) for tree in tree]
    # for i in range(len(tree)):
    #     for j in range(len(m_tree[0])):
    #         optimal_time, optimal_cost, best_worst_cost, ra_time, ra_cost, grade = \
    #             align_info(tree[i], m_tree[i][j], log[i], apply, option)
    data = pd.read_excel(PATH + "MProcessTree.xlsx", sheet_name='16-18', header=0)
    log_d = pd.read_excel(PATH + "0.2/log.xlsx", sheet_name='16-18', header=0)
    trees = data['tree']
    m_trees = data['m_tree']
    logs = log_d['log']
    optimal_time, optimal_cost, best_worst_cost = list(), list(), list()
    ra_time, ra_cost, grade = list(), list(), list()
    for i in range(len(trees)):
        info = align_info(pt_utils.parse(trees[i]), pt_utils.parse(m_trees[i]), create_event_log(logs[i // 15]),
                          version, option)
        optimal_time.append(info[0])
        optimal_cost.append(info[1])
        best_worst_cost.append(info[2])
        ra_time.append(info[3])
        ra_cost.append(info[4])
        grade.append(info[5])
        if i > 200:
            repair_align_compare(pt_utils.parse(trees[i]), pt_utils.parse(m_trees[i]), create_event_log(logs[i // 15]))
    df = pd.DataFrame({"optimal time": optimal_time, "optimal cost": optimal_cost, "best worst cost": best_worst_cost,
                       "repair align time": ra_time, "repair align cost": ra_cost, "grade": grade})
    df.to_csv(PATH + "align_repair_opt2.csv")


def pie():

    grade = pd.read_excel(PATH + "0.2/align_opt1.xlsx", sheet_name='total', header=0)['grade']

    from repair_alignment.process_tree.operation import pt_compare
    from pm4py.objects.process_tree.pt_operator import Operator
    opt, labels = [0, 0, 0, 0], ["Xor", "Sequence", "Parallel", "Loop"]
    for sn in SHEET_NAME:
        data = pd.read_excel(PATH + "MProcessTree.xlsx", sheet_name=sn, header=0)
        trees = data['tree']
        m_trees = data['m_tree']
        for index, tree in enumerate(trees):
            com_res = pt_compare.apply(pt_utils.parse(tree), pt_utils.parse(m_trees[index]))
            if grade[index] != 1 :
                # and com_res.subtree1.parent is not None
                if com_res.subtree1.operator == Operator.XOR:
                    opt[0] += 1
                if com_res.subtree1.operator == Operator.SEQUENCE:
                    opt[1] += 1
                if com_res.subtree1.operator == Operator.PARALLEL:
                    opt[2] += 1
                if com_res.subtree1.operator == Operator.LOOP:
                    opt[3] += 1
    import matplotlib.pyplot as plt
    # explode = (0.1, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
    plt.pie(opt, labels=labels, autopct='%1.01f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.plot()
    plt.savefig("pie.png", dpi=300)
    print(sum(opt))


if __name__ == "__main__":
    # grade_compare()
    # time_compare()
    # two_method_compare()
    # compute_alignment1(align_repair_lock.apply, 1)
    # tree1 = pt_utils.parse("*( X( ->( b, c ), +( X( i, j ), X( g, h, ->( d, e, f ) ) ) ), a, τ )")
    # tree2 = pt_utils.parse("*( X( ->( b, c ), +( X( i, j ), X( g, h, ->( d, e, f, l ) ) ) ), a, τ )")
    # logs_ = create_event_log("jfljgabc")
    # # align_repair_lock.apply(tree1, tree2, logs_)
    # # align_info(tree1, tree2, logs_, align_repair_opt.apply, 1)
    # repair_align_compare(tree1, tree2, logs_)
    pie()
    #
    # f_trees = pd.read_csv("sub_trees.csv")
    # f_logs = pd.read_csv("sub_logs.csv")
    # trees = f_trees['tree'].values
    # m_trees = f_trees['m_tree'].values
    # logs = f_logs['log'].values
    # for index, i in enumerate(trees):
    #     align_info(pt_utils.parse(trees[index]), pt_utils.parse(m_trees[index]),
    #                create_event_log(logs[index // 15]), align_repair_opt.apply, 1)


def create_file_with_different_grade_by_align1_and_align2():
    p_align1 = PATH + '0.2/align1_repair1.xlsx'
    p_align2 = PATH + '0.2/align2_repair1.xlsx'
    align1 = pd.read_excel(p_align1, sheet_name=SHEET_NAME)
    align2 = pd.read_excel(p_align2, sheet_name=SHEET_NAME)
    mp_trees = pd.read_excel(PATH + 'MProcessTree.xlsx', sheet_name=SHEET_NAME)
    logs = pd.read_excel(PATH + '0.2/log.xlsx', sheet_name=SHEET_NAME)
    sub_tree = []
    sub_align1 = []
    sub_align2 = []
    sub_log = []
    for i in align1:
        grade1 = align1[i]['grade'].tolist()
        grade2 = align2[i]['grade'].tolist()
        log_list = logs[i]['log'].values
        tree_list = mp_trees[i].values
        for j, m_tree in enumerate(tree_list):
            if grade1[j] != grade2[j]:
                print(grade1[j], grade2[j])
                sub_tree.append(tree_list[j])
                sub_log.append(log_list[j // 15])
                sub_align1.append(align1[i].values[j])
                sub_align2.append(align2[i].values[j])
    pd.DataFrame(sub_align1, columns=align1['11-15'].columns).to_csv('sub_align1.csv')
    pd.DataFrame(sub_align2, columns=align1['11-15'].columns).to_csv('sub_align2.csv')
    pd.DataFrame(sub_log, columns=logs['11-15'].columns).to_csv('sub_log.csv')
    pd.DataFrame(sub_tree, columns=mp_trees['11-15'].columns).to_csv('sub_tree.csv')
