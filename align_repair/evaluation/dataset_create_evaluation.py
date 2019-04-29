import random

from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY

from align_repair.process_tree.stochastic_generation import stochastic_pt_create as pt_create
from align_repair.process_tree.stochastic_generation import stochastic_pt_mutate as pt_mutate
from align_repair.process_tree.manipulation import utils as pt_mani_utils
from align_repair.evaluation.execl_operation import utils as excel_utils, object_read
from align_repair.evaluation.execl_operation.excel_table import ExcelTable
from align_repair.process_tree.stochastic_generation import non_fitting_log_create as log_create
from align_repair.evaluation import alignment_on_lock_pt
from align_repair.evaluation.config import PT_NUM, LOG_SHEET_NAME, ALIGN_SHEET_NAME, TRACE_NUM, \
    PT_FILE_NAME, LOG_FILE_NAME, ALIGN_FILE_NAME, MPT_NUM, MTP_LEVEL, PT_RANGE


def create_tree():
    """
    Create totally 80 process trees, in which
        10 trees with 11-15 nodes
        10 trees with 16-18 nodes
        10 trees with 19-21 nodes
        10 trees with 22-24 nodes
        10 trees with 25-27 nodes
        10 trees with 28-30 nodes
        10 trees with 31-33 nodes
        10 trees with 34-45 nodes

    Worksheet
    -----------
    Base worksheet:
        Store Information of based Process Tree

    Other Worksheet:
        Store Information of mutated process tree with based process tree
        The worksheet differs based on the size of mutated sub process tree.
        e.g. For "MPT4", only the depth of Sub PT less or equal than 4 can mutate.

    Records Format For base Worksheet
    ---------
    Number of nodes, Process Tree, Number of leaves, Depth of PT, Operator of root


    Records Format For other Worksheet
    ---------
    Row number in base worksheet, (content in that row), Number of nodes of MPT, Mutated Process Tree (MPT)
     Number of leaves of MPT, Depth of MPT, Operator of the root of MPT,

    """
    base = excel_utils.create_workbook()
    original_e_tab = ExcelTable(base.add_sheet("PT"))
    mutate_e_tabs = []
    for level in MTP_LEVEL:
        mutate_e_tab = ExcelTable(base.add_sheet("MPT" + str(level)))
        mutate_e_tabs.append(mutate_e_tab)
    for i in range(len(PT_NUM)):
        pt_write_to_table(original_e_tab, mutate_e_tabs, PT_NUM[i], PT_RANGE[i][0], PT_RANGE[i][0], MPT_NUM, MTP_LEVEL)
    excel_utils.save(base, PT_FILE_NAME)


def pt_write_to_table(tab, mutate_tabs, num, l, u, mutate_num, mutate_level):
    for _ in range(num):
        row = tab.row
        # TODO: 一定时间内没有找到
        no_node = random.randint(l, u)
        tree = pt_create.apply(no_node)
        info = [no_node, " " + str(tree), pt_mani_utils.leaves_number(tree), pt_mani_utils.pt_depth(tree)]
        for i, mutate_tab in enumerate(mutate_tabs):
            for m_tree in uniq_mutate_tree(tree, mutate_num, mutate_level[i]):
                mutate_tree_write_to_table(mutate_tab, m_tree, [row] + info)
        excel_utils.write_row_to_table(tab.table, row, info)


def uniq_mutate_tree(tree, mutate_num, mutate_tree_level):
    m_trees = list()
    while len(m_trees) < mutate_num:
        if str(tree) not in m_trees:
            m_tree = pt_mutate.apply(tree, mutate_tree_level)
            m_trees.append(m_tree)
    return m_trees


def mutate_tree_write_to_table(tab, m_tree, tree_info):
    excel_utils.write_row_to_table(tab.table, tab.row, tree_info + [pt_mani_utils.nodes_number(m_tree),
                                                                    " " + str(m_tree),
                                                                    pt_mani_utils.leaves_number(m_tree),
                                                                    pt_mani_utils.pt_depth(m_tree)])


def create_log():
    """
    Create specified number of event logs of each tree, not including Empty Trace.

    The event log in the same column belong to the same process tree.
    """
    base = excel_utils.create_workbook()
    trees = object_read.read_trees_from_file(PT_FILE_NAME)
    log_e_table = None
    for row, tree in enumerate(trees):
        if row % PT_NUM[0] == 0:
            log_e_table = ExcelTable(base.add_sheet(LOG_SHEET_NAME[row // PT_NUM[0]]))
        log = log_create.apply(tree, TRACE_NUM, 0.8)
        trace_list = [[event[DEFAULT_NAME_KEY] for event in trace] for trace in log]
        excel_utils.write_column_to_table(log_e_table.table, log_e_table.column, trace_list)
    excel_utils.save(base, LOG_FILE_NAME)


def compute_alignment():
    """
    Create specified number of event logs of each tree, not including Empty Trace.

    The event log in the same column belong to the same process tree.
    """
    trees = object_read.read_trees_from_file(PT_FILE_NAME)
    logs = object_read.read_logs_from_file(LOG_FILE_NAME)
    base = excel_utils.create_workbook()
    align_e_table = None
    for row, tree in enumerate(trees):
        if row % PT_NUM[0] == 0:
            align_e_table = ExcelTable(base.add_sheet(ALIGN_SHEET_NAME[row // PT_NUM[0]]))
        alignments = alignment_on_lock_pt(tree, logs[row])
        align_list = list(map(str, alignments))
        excel_utils.write_column_to_table(align_e_table.table, align_e_table.column, align_list)
    excel_utils.save(base, ALIGN_FILE_NAME)


if __name__ == "__main__":
    compute_alignment()


def test_avg_mutate_tree_size():
    trees = []
    for i in range(100):
        tree = pt_create.apply(10)
        # trees = [str(tree)]
        while len(trees) < 10:
            if str(tree) not in trees:
                m_tree = pt_mutate.apply(tree, 3)
                trees.append(str(m_tree))
            # else:
            #     break
    print(len(trees))
