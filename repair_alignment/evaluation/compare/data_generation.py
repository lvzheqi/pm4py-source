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
from repair_alignment.evaluation.compare import apply_align_on_one_pt, apply_align_on_one_pt2


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


def compute_align_grade1(num):
    trees = pd.read_excel(tree_file, sheet_name=SHEET_NAME)
    mp_trees = pd.read_excel(m_tree_file, sheet_name=SHEET_NAME)
    # logs = pd.read_excel(log_file, sheet_name=SHEET_NAME)

    align_result = list()
    align_result2 = list()
    align_result3 = list()
    # align_result4 = list()
    for i in trees:
        itree_list = trees[i]['tree'].tolist()
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
        for k, tree in enumerate(tree_list):
            log = create_event_log(log_list[k])
            alignments = alignment_on_pt(tree, log)
            for j in range(num):
                m_tree = pt_utils.parse(mpt_list[k * num + j])
                info = apply_align_on_one_pt2(tree, m_tree, log, alignments)
                align_info.loc[len(align_info.index)] = info[0]
                align_info2.loc[len(align_info.index)] = info[1]
                align_info3.loc[len(align_info.index)] = info[2]
            # align_info4.loc[len(align_info.index)] = info[3]
        align_result.append(align_info)
        align_result2.append(align_info2)
        align_result3.append(align_info3)
        # align_result4.append(align_info4)

    with pd.ExcelWriter(PATH + 'ar.xlsx') as writer:
        for i, align in enumerate(align_result):
            align.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)

    with pd.ExcelWriter(PATH + 'iar.xlsx') as writer:
        for i, align in enumerate(align_result2):
            align.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)

    with pd.ExcelWriter(PATH + 'iar_ud.xlsx') as writer:
        for i, align in enumerate(align_result3):
            align.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)

    # with pd.ExcelWriter(PATH + 'iar_ud2.xlsx') as writer:
    #     for i, align in enumerate(align_result4):
    #         align.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)


if __name__ == "__main__":
    # random_create_dataset()
    compute_align_grade1(len(depths) * mpt_num)
    compute_align_grade(len(depths) * mpt_num, Version.AR_LINEAR, 1, PATH + 'align_opt1.xlsx')
    # compute_align_grade(len(depths) * mpt_num, Version.IAR_LINEAR, 2, PATH + 'align_opt2.xlsx')
    #
    # PATH = '../../../data/D6/'
    # tree_file = PATH + 'ProcessTree.xlsx'
    # m_tree_file = PATH + 'MProcessTree.xlsx'
    # log_file = PATH + '0.2/log.xlsx'
    # align_file = PATH + 'align_opt.xlsx'
    # random_create_dataset()
    # compute_align_grade1(len(depths) * mpt_num)
