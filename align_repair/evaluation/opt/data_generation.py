import pandas as pd
import random
import time

from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.process_tree import util as pt_utils

from align_repair.process_tree.stochastic_generation import stochastic_pt_mutate as pt_mutate
from align_repair.process_tree.stochastic_generation import stochastic_pt_create as pt_create
from align_repair.process_tree.stochastic_generation import non_fitting_log_create as log_create
from align_repair.process_tree.manipulation import pt_number, utils as pt_mani_utils
from align_repair.evaluation import alignment_on_pt, create_event_log, get_best_cost_on_pt
from align_repair.repair.optimal import align_repair_opt

PATH = '../../data/'
PT_RANGE = [(11, 15), (16, 18), (19, 21), (22, 24)]
SHEET_NAME = [str(i) + "-" + str(j) for (i, j) in PT_RANGE]
pt_num, mpt_num, trace_num, non_fit_pro = 2, 2, 5, 0.2
depths = [3, 4]
tree_file = PATH + 'ProcessTree.xlsx'
m_tree_file = PATH + 'MProcessTree.xlsx'
log_file = PATH + 'log.xlsx'
align_file = PATH + 'align_opt.xlsx'


def create_pts():
    pts = list()
    for node_num in PT_RANGE:
        trees = pd.DataFrame(columns=['tree', '#node', 'depth', 'root-op'])
        for i in range(pt_num):
            tree = pt_create.apply(random.randint(node_num[0], node_num[1]))
            num_nodes = pt_number.apply(tree, 'D')
            trees.loc[i] = [str(tree), num_nodes, pt_mani_utils.pt_depth(tree), str(tree.operator)]
            # print(type(trees.loc[i]))
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
                    m_trees.loc[len(m_trees.index)] = trees.loc[i].tolist() + [str(m_tree), depths]
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

    with pd.ExcelWriter(log_file) as writer:
        for i, log in enumerate(logs):
            log.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)


def apply_align_on_one_pt(tree, m_tree, log, apply, option):
    best_worst_cost = get_best_cost_on_pt(tree, log)

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
    alignments, repair_alignments = apply(tree, m_tree, log, parameters, option)
    end = time.time()
    print(repair_alignments)
    ra_time = end - start
    print('repair time:', end - start)
    ra_cost = sum([align['cost'] for align in repair_alignments])
    grade = 1 - (ra_cost - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1
    print('repair cost', ra_cost)
    print('grade', grade)
    return [optimal_time, optimal_cost, best_worst_cost, ra_time, ra_cost, grade]


def compute_align_grade(num, apply, option):
    mp_trees = pd.read_excel(m_tree_file, sheet_name=SHEET_NAME)
    logs = pd.read_excel(log_file, sheet_name=SHEET_NAME)
    align_result = list()
    for i in mp_trees:
        log_list = logs[i]['log'].tolist()
        tree_list = mp_trees[i]['tree'].tolist()
        mpt_list = mp_trees[i]['m_tree'].tolist()
        align_info = pd.DataFrame(columns=["optimal time", "optimal cost", "best worst cost",
                                           "repair align time", "repair align cost", "grade"])
        for j, m_tree in enumerate(mpt_list):
            m_tree = pt_utils.parse(m_tree)
            tree = pt_utils.parse(tree_list[j // num])
            log = create_event_log(log_list[j // num])
            align_info.loc[len(align_info.index)] = apply_align_on_one_pt(tree, m_tree, log, apply, option)
        align_result.append(align_info)

    with pd.ExcelWriter(align_file) as writer:
        for i, align in enumerate(align_result):
            align.to_excel(writer, sheet_name=SHEET_NAME[i], index=False)


if __name__ == "__main__":
    random_create_dataset()
    compute_align_grade(len(depths) * mpt_num, align_repair_opt.apply, 2)
