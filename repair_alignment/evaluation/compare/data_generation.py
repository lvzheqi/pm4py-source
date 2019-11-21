import pandas as pd
import random
import time

from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.process_tree import util as pt_utils

from repair_alignment.process_tree.generation import stochastic_pt_mutate as pt_mutate
from repair_alignment.process_tree.generation import stochastic_pt_create as pt_create
from repair_alignment.process_tree.generation import non_fitting_log_create as log_create
from repair_alignment.process_tree.operation import pt_number, utils as pt_mani_utils
from repair_alignment.evaluation import alignment_on_pt, create_event_log, get_best_cost_on_pt, print_event_log
from repair_alignment.algo.repair import repair
from repair_alignment.algo.repair.version import Version

PATH = '../../../data/D3/'
#
PT_RANGE = [(11, 15), (16, 18), (19, 21), (22, 24)]
# PT_RANGE = [(11, 15)]

SHEET_NAME = [str(i) + "-" + str(j) for (i, j) in PT_RANGE]
pt_num, mpt_num, trace_num, non_fit_pro = 5, 5, 50, 0.2
depths = [3, 4, 5]
# depths = [3]

tree_file = PATH + 'ProcessTree.xlsx'
m_tree_file = PATH + 'MProcessTree.xlsx'
log_file = PATH + '0.2/log.xlsx'
align_file = PATH + 'align_opt.xlsx'


def create_pts():
    pts = list()
    for node_num in PT_RANGE:
        trees = pd.DataFrame(columns=['tree', '#node', 'depth', 'root-op'])
        for i in range(pt_num):
            tree = pt_create.apply(random.randint(node_num[0], node_num[1]))
            num_nodes = pt_number.apply(tree, 'D')
            trees.loc[i] = [str(tree), num_nodes, pt_mani_utils.pt_depth(tree), str(tree.operator)]
        pts.append(trees)
    return pts


def create_m_pts(pts):
    m_pts = list()
    for trees in pts:
        m_trees = pd.DataFrame(columns=['tree', '#node', 'depth', 'root-op', 'm_tree', 'sub_depth'])
        for i, s_tree in enumerate(trees['tree']):
            tree = pt_utils.parse(s_tree)
            for depth in depths:
                for j in range(mpt_num):
                    m_tree = pt_mutate.apply(tree, depth)
                    m_trees.loc[len(m_trees.index)] = trees.loc[i].tolist() + [str(m_tree), depth]
        m_pts.append(m_trees)
    return m_pts


def parse_string_list(log):
    return ", ".join(["".join([event[DEFAULT_NAME_KEY] for event in trace]) for trace in log])


def create_logs(pts):
    logs_list = list()
    for trees in pts:
        logs = pd.DataFrame(columns=['log'])
        for i, s_tree in enumerate(trees['tree']):
            tree = pt_utils.parse(s_tree)
            logs.loc[i] = [parse_string_list(log_create.apply(tree, trace_num, non_fit_pro))]
        logs_list.append(logs)
    return logs_list


def random_create_dataset():
    p_trees = create_pts()
    mp_trees = create_m_pts(p_trees)
    logs = create_logs(p_trees)

    with pd.ExcelWriter(tree_file) as writer:
        for i, pt in enumerate(p_trees):
            pt.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)

    with pd.ExcelWriter(m_tree_file) as writer:
        for i, pt in enumerate(mp_trees):
            pt.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)

    # with pd.ExcelWriter(log_file) as writer:
    #     for i, log in enumerate(logs):
    #         log.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)

    for i, log in enumerate(logs):
        log.to_csv(PATH + '/0.2/log' + SHEET_NAME[i] + ".csv", index=False)


def apply_align_on_one_pt(tree, m_tree, log, version, option):
    print('-------------------------------------------------')
    best_worst_cost = get_best_cost_on_pt(m_tree, log)

    start = time.time()
    alignment_on_pt(tree, log)
    alignments = alignment_on_pt(m_tree, log)
    end = time.time()
    optimal_time = end - start
    print('optimal time:', end - start)
    optimal_cost = sum([align['cost'] for align in alignments])
    print('optimal cost', optimal_cost)

    start = time.time()
    parameters = {'ret_tuple_as_trans_desc': True}
    alignments, repair_alignments = repair.apply(tree, m_tree, log, version, parameters, option)
    end = time.time()
    ra_time = end - start
    print('repair time:', end - start)

    ra_cost = sum([align['cost'] for align in repair_alignments])
    grade = 1 - (ra_cost - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1
    print('repair cost', ra_cost)
    print('grade', grade)
    return [optimal_time, optimal_cost, ra_time, ra_cost, grade]


def compute_align_grade(num, version, option, file):
    mp_trees = pd.read_excel(m_tree_file, sheet_name=SHEET_NAME)
    # logs = pd.read_excel(log_file, sheet_name=SHEET_NAME)

    align_result = list()
    for i in mp_trees:
        # log_list = logs[i]['log'].tolist()
        log_list = pd.read_csv(PATH + '/0.2/log' + i + ".csv")['log'].tolist()
        tree_list = mp_trees[i]['tree'].tolist()
        mpt_list = mp_trees[i]['m_tree'].tolist()
        align_info = pd.DataFrame(columns=["optimal time", "optimal cost",
                                           "repair align time", "repair align cost", "grade"])
        for j, m_tree in enumerate(mpt_list):
            m_tree = pt_utils.parse(m_tree)
            tree = pt_utils.parse(tree_list[j])
            log = create_event_log(log_list[j // num])
            align_info.loc[len(align_info.index)] = apply_align_on_one_pt(tree, m_tree, log, version, option)
        align_result.append(align_info)
        return
    with pd.ExcelWriter(file) as writer:
        for i, align in enumerate(align_result):
            align.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)


def apply_align_on_one_pt2(tree, m_tree, log):
    best_worst_cost = get_best_cost_on_pt(m_tree, log)

    alignment_on_pt(tree, log)

    start = time.time()
    alignments = alignment_on_pt(m_tree, log)
    end = time.time()
    optimal_time = end - start
    print('optimal time:', optimal_time)
    optimal_cost = sum([align['cost'] for align in alignments])
    print('optimal cost', optimal_cost)

    parameters = {'ret_tuple_as_trans_desc': True}
    alignments = alignment_on_pt(tree, log)

    start = time.time()
    alignments1, repair_alignments1 = repair.apply_with_alignments(tree, m_tree, log, alignments, Version.AR_LINEAR,
                                                                   parameters, 1)
    end = time.time()
    ra_time1 = end - start

    start = time.time()
    alignments2, repair_alignments2 = repair.apply_with_alignments(tree, m_tree, log, alignments, Version.IAR_LINEAR,
                                                                   parameters, 1)
    end = time.time()
    ira_time2 = end - start

    start = time.time()
    alignments3, repair_alignments3 = repair.apply_with_alignments(tree, m_tree, log, alignments, Version.IAR_TOP_DOWN,
                                                                   parameters, 1)
    end = time.time()
    ira_time3 = end - start

    # start = time.time()
    # alignments4, repair_alignments4 = repair.apply_with_alignments(tree, m_tree, log, alignments, Version.IAR_TOP_DOWN,
    #                                                                parameters, 2)
    # end = time.time()
    # ira_time4 = end - start

    print('repair time:', ra_time1, ira_time2, ira_time3)
    # print('repair time:', ra_time1, ira_time2, ira_time3, ira_time4)

    ra_cost1 = sum([align['cost'] for align in repair_alignments1])
    grade1 = 1 - (ra_cost1 - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1

    ira_cost2 = sum([align['cost'] for align in repair_alignments2])
    grade2 = 1 - (ira_cost2 - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1

    ira_cost3 = sum([align['cost'] for align in repair_alignments3])
    grade3 = 1 - (ira_cost3 - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1

    # ira_cost4 = sum([align['cost'] for align in repair_alignments4])
    # grade4 = 1 - (ira_cost4 - optimal_cost) / (best_worst_cost - optimal_cost) \
    #     if best_worst_cost != optimal_cost else 1

    print('repair cost', ra_cost1, ira_cost2, ira_cost3)
    print('grade', grade1, grade2, grade3)

    # print('repair cost', ra_cost1, ira_cost2, ira_cost3, ira_cost4)
    # print('grade', grade1, grade2, grade3, grade4)
    return [[optimal_time*40, optimal_cost*40, ra_time1*40, ra_cost1*40, grade1],
            [optimal_time*40, optimal_cost*40, ira_time2*40, ira_cost2*40, grade2],
            [optimal_time*40, optimal_cost*40, ira_time3*40, ira_cost3*40, grade3]]
            # [optimal_time, optimal_cost, best_worst_cost, ira_time4, ira_cost4, grade4]


def compute_align_grade1(num):
    mp_trees = pd.read_excel(m_tree_file, sheet_name=SHEET_NAME)
    # logs = pd.read_excel(log_file, sheet_name=SHEET_NAME)

    align_result = list()
    align_result2 = list()
    align_result3 = list()
    # align_result4 = list()
    index = 1
    for i in mp_trees:
        if i != "22-24":
            print(i, index)
            continue

        log_list = pd.read_csv(PATH + 'log' + i + ".csv")['log'].tolist()
        # log_list = logs[i]['log'].tolist()
        tree_list = mp_trees[i]['tree'].tolist()
        mpt_list = mp_trees[i]['m_tree'].tolist()
        align_info = pd.DataFrame(columns=["optimal time", "optimal cost",
                                           "repair align time", "repair align cost", "grade"])
        align_info2 = pd.DataFrame(columns=["optimal time", "optimal cost",
                                            "repair align time", "repair align cost", "grade"])
        align_info3 = pd.DataFrame(columns=["optimal time", "optimal cost",
                                                "repair align time", "repair align cost", "grade"])
        # align_info4 = pd.DataFrame(columns=["optimal time", "optimal cost", "best worst cost",
        #                                     "repair align time", "repair align cost", "grade"])
        for j, m_tree in enumerate(mpt_list):
            if j < 61:
                continue
            print(j)
            m_tree = pt_utils.parse(m_tree)
            tree = pt_utils.parse(tree_list[j])
            log = create_event_log(log_list[j // num])
            info = apply_align_on_one_pt2(tree, m_tree, log)
            align_info.loc[len(align_info.index)] = info[0]
            align_info2.loc[len(align_info.index)] = info[1]
            align_info3.loc[len(align_info.index)] = info[2]
            # align_info4.loc[len(align_info.index)] = info[3]
        align_result.append(align_info)
        align_result2.append(align_info2)
        align_result3.append(align_info3)
        # align_result4.append(align_info4)

    with pd.ExcelWriter(PATH + 'ar1.xlsx') as writer:
        align_result[0].to_excel(writer, sheet_name="22-24", index=False)
        # for i, align in enumerate(align_result):
        #     align.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)

    with pd.ExcelWriter(PATH + 'iar1.xlsx') as writer:
        align_result[0].to_excel(writer, sheet_name="22-24", index=False)
        #
        # for i, align in enumerate(align_result2):
        #     align.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)

    with pd.ExcelWriter(PATH + 'iar_ud1.xlsx') as writer:
        align_result[0].to_excel(writer, sheet_name="22-24", index=False)
        # for i, align in enumerate(align_result3):
        #     align.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)

    # with pd.ExcelWriter(PATH + 'iar_ud2.xlsx') as writer:
    #     for i, align in enumerate(align_result4):
    #         align.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)


if __name__ == "__main__":
    # random_create_dataset()
    compute_align_grade1(len(depths) * mpt_num)
    # compute_align_grade(len(depths) * mpt_num, Version.AR_LINEAR, 1, PATH + 'align_opt1.xlsx')
    # compute_align_grade(len(depths) * mpt_num, Version.IAR_LINEAR, 2, PATH + 'align_opt2.xlsx')
    #
    # PATH = '../../../data/D6/'
    # tree_file = PATH + 'ProcessTree.xlsx'
    # m_tree_file = PATH + 'MProcessTree.xlsx'
    # log_file = PATH + '0.2/log.xlsx'
    # align_file = PATH + 'align_opt.xlsx'
    # random_create_dataset()
    # compute_align_grade1(len(depths) * mpt_num)
