import random

from xlwt import Workbook

from align_repair.process_tree.stochastic_generation import stochastic_pt_create as pt_create
from align_repair.process_tree.stochastic_generation import stochastic_pt_mutate as pt_mutate
from align_repair.process_tree.manipulation import utils as pt_mani_utils


class ExcelTable(object):
    def __init__(self, table):
        self._row = 0
        self._table = table

    def _get_row(self):
        self._row += 1
        return self._row - 1

    def _get_table(self):
        return self._table

    row = property(_get_row)
    table = property(_get_table)


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
    Records
    ---------
    Number of nodes, Number of leaves, Depth of PT, Operator of root, Process Tree
    """
    file = Workbook(encoding='utf-8')
    table = file.add_sheet("PT")
    mutate_tree_number = 7
    original_e_tab = ExcelTable(table)
    mutate_tree_level = [3, 4, 5, 6]
    mutate_e_tabs = []
    for i in mutate_tree_level:
        m_table = file.add_sheet("MPT"+str(i))
        mutate_e_tab = ExcelTable(m_table)
        mutate_e_tabs.append(mutate_e_tab)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 10, 11, 15, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 10, 16, 18, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 10, 19, 21, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 10, 22, 24, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 10, 25, 27, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 10, 28, 30, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 10, 31, 33, mutate_tree_number, mutate_tree_level)
    pt_write_to_table(original_e_tab, mutate_e_tabs, 10, 34, 45, mutate_tree_number, mutate_tree_level)
    file.save('ProcessTree.xls')


def pt_write_to_table(tab, mutate_tabs, num, l, u, mutate_num, mutate_level):
    for _ in range(num):
        no_node = random.randint(l, u)
        tree = pt_create.apply(no_node)
        row = tab.row
        info = [no_node, " " + str(tree), pt_mani_utils.leaves_number(tree), pt_mani_utils.pt_depth(tree)]
        for i, mutate_tab in enumerate(mutate_tabs):
            for _ in range(mutate_num):
                mutate_tree_write_to_table(mutate_tab, tree, [row] + info, mutate_level[i])
        write_to_table(tab.table, row, info)


def mutate_tree_write_to_table(tab, tree, tree_info, mutate_tree_level):
    m_tree = pt_mutate.apply(tree, mutate_tree_level)
    write_to_table(tab.table, tab.row, tree_info + [pt_mani_utils.nodes_number(m_tree), " " + str(m_tree),
                                                    pt_mani_utils.leaves_number(m_tree),
                                                    pt_mani_utils.pt_depth(m_tree)])


def write_to_table(table, row, info):
    for i in range(len(info)):
        table.write(row, i, info[i])


def test_avg_mutate_tree_size():
    diff_m = 0
    for i in range(1):
        trees = []
        while True:
            # m_tree = pt_mutate.apply(tree, 7)
            tree = pt_create.apply(15)
            if str(tree) not in trees:
                trees.append(str(tree))
            else:
                break
        diff_m += len(trees)
    print(diff_m / 1)


if __name__ == "__main__":
    create_tree()
    # test_avg_mutate_tree_size()
