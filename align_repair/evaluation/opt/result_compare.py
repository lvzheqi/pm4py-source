import pandas as pd
from pm4py.objects.process_tree import util as pt_utils
from align_repair.process_tree.manipulation import pt_compare
from align_repair.process_tree.manipulation import utils as pt_mani_utils


PATH = '../../data/D1/'


def compare_runtime_box():
    data_opt1 = pd.read_excel(PATH + "0.2/align_opt1.xlsx", sheet_name='total', header=0)
    data_tree = pd.read_excel(PATH + "MProcessTree.xlsx", sheet_name='total', header=0)
    trees = data_tree['tree'].tolist()
    m_trees = data_tree['m_tree'].tolist()
    depths = []
    for i in range(len(trees)):
        pt = pt_utils.parse(trees[i])
        m_pt = pt_utils.parse(m_trees[i])
        com_res = pt_compare.apply(pt, m_pt, 1)
        depth = pt_mani_utils.pt_depth(str(com_res.subtree1))
        depths.append(depth)
    print(set(depths))


if __name__ == "__main__":
    compare_runtime_box()
