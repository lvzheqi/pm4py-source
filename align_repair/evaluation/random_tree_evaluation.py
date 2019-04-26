import random

from align_repair.process_tree.stochastic_generation import stochastic_pt_create as pt_create
from align_repair.process_tree.stochastic_generation import stochastic_pt_mutate as pt_mutate
from align_repair.process_tree.manipulation import utils as pt_mani_utils
from align_repair.evaluation.execl_operation import utils as excel_utils
from align_repair.evaluation.execl_operation.excel_table import ExcelTable


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
    mutate_tree_number = 10
    original_e_tab = ExcelTable(base.add_sheet("PT"))
    mutate_tree_level = [3, 4, 5, 6]
    mutate_e_tabs = []
    for i in mutate_tree_level:
        mutate_e_tab = ExcelTable(base.add_sheet("MPT" + str(i)))
        mutate_e_tabs.append(mutate_e_tab)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 150, 11, 15, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 150, 16, 18, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 150, 19, 21, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 150, 22, 24, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 150, 25, 27, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 150, 28, 30, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 150, 31, 33, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 10, 34, 45, mutate_tree_number, mutate_tree_level)
    excel_utils.save(base, 'ProcessTree.xls')


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
            m_trees.append(str(m_tree))
    return m_trees


def mutate_tree_write_to_table(tab, m_tree, tree_info):
    excel_utils.write_row_to_table(tab.table, tab.row, tree_info + [pt_mani_utils.nodes_number(m_tree),
                                                                    " " + str(m_tree),
                                                                    pt_mani_utils.leaves_number(m_tree),
                                                                    pt_mani_utils.pt_depth(m_tree)])


def test_avg_mutate_tree_size():
    diff_m = 0
    for i in range(100):
        tree = pt_create.apply(10)
        # trees = [str(tree)]
        trees = []
        while len(trees) < 10:
            if str(tree) not in trees:
                m_tree = pt_mutate.apply(tree, 3)
                trees.append(str(m_tree))
            # else:
            #     break
        diff_m += len(trees)
    print(len(trees))


if __name__ == "__main__":
    # create_tree()
    test_avg_mutate_tree_size()
