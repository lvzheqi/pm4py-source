import time
import random

from repair_alignment.process_tree.generation import stochastic_pt_create as pt_create
from repair_alignment.process_tree.generation import non_fitting_log_create as log_create
from repair_alignment.process_tree.generation import stochastic_pt_mutate as pt_mutate
from repair_alignment.repair.optimal import align_repair_opt
from repair_alignment.evaluation import alignment_on_pt


def avg_runtime_without_lock(trees, m_trees, logs):
    start = time.time()
    for i in range(len(trees)):
        for j in range(len(m_trees[0])):
            alignment_on_pt(trees[i], logs[i])
            alignment_on_pt(m_trees[i][j], logs[i])
    end = time.time()
    print((end - start) / (len(trees) * len(m_trees[0])))
    return (end - start) / (len(trees) * len(m_trees[0]))


def avg_runtime_with_lock(trees, m_trees, logs):
    start = time.time()
    for i in range(len(trees)):
        for j in range(len(m_trees[0])):
            align_repair_opt.apply(trees[i], m_trees[0][j], logs[i], {'ret_tuple_as_trans_desc': True})
    end = time.time()
    print((end - start) / (len(trees) * len(m_trees[0])))
    return (end - start) / (len(trees) * len(m_trees[0]))


def plot_histogram_lock_runtime(list1, list2):
    """
    Compared the time of alignment of PT with lock and without lock
    """
    import matplotlib.pyplot as plt

    # label_list = ["10-15", "16-20", "21-25", "26-30"]
    label_list = ["10-15", "16-20", "21-25", "26-30", "31-33", "34-35"]
    x = range(len(list1))
    plt.bar(x=x, height=list1, width=0.4, alpha=0.8, color="red", label="Optimal Alignment")
    plt.bar(x=[i + 0.4 for i in x], height=list2, width=0.4, color="green", label="Alignment Repair")
    plt.xlabel("Number of Node")
    plt.ylabel("Time(Seconds)")
    plt.xticks([i + 0.2 for i in x], label_list)
    plt.title("Compare Runtime of Alignment/ Repaired Alignment 10X10X5")
    plt.legend()
    plt.savefig("ComparePNTime")


def compute_run_time():
    no_tree, no_event, pro, mutated_num = 10, 10, 0.9, 5
    tree1 = [pt_create.apply(random.randint(11, 15)) for _ in range(no_tree)]
    m_tree1 = [[pt_mutate.apply(tree) for _ in range(mutated_num)] for tree in tree1]
    log1 = [log_create.apply(tree, no_event, pro) for tree in tree1]
    tree2 = [pt_create.apply(random.randint(16, 20)) for _ in range(no_tree)]
    m_tree2 = [[pt_mutate.apply(tree) for _ in range(mutated_num)] for tree in tree2]
    log2 = [log_create.apply(tree, no_event, pro) for tree in tree2]
    tree3 = [pt_create.apply(random.randint(21, 25)) for _ in range(no_tree)]
    m_tree3 = [[pt_mutate.apply(tree) for _ in range(mutated_num)] for tree in tree3]
    log3 = [log_create.apply(tree, no_event, pro) for tree in tree3]
    tree4 = [pt_create.apply(random.randint(26, 30)) for _ in range(no_tree)]
    log4 = [log_create.apply(tree, no_event, pro) for tree in tree4]
    m_tree4 = [[pt_mutate.apply(tree) for _ in range(mutated_num)] for tree in tree4]
    tree5 = [pt_create.apply(random.randint(31, 33)) for _ in range(no_tree)]
    log5 = [log_create.apply(tree, no_event, pro) for tree in tree5]
    m_tree5 = [[pt_mutate.apply(tree) for _ in range(mutated_num)] for tree in tree5]
    tree6 = [pt_create.apply(random.randint(34, 35)) for _ in range(no_tree)]
    log6 = [log_create.apply(tree, no_event, pro) for tree in tree6]
    m_tree6 = [[pt_mutate.apply(tree) for _ in range(mutated_num)] for tree in tree6]

    l_without_lock = list(map(lambda tree_log: avg_runtime_without_lock(tree_log[0], tree_log[1], tree_log[2]),
                              [(tree1, m_tree1, log1), (tree2, m_tree2, log2), (tree3, m_tree3, log3),
                               (tree4, m_tree4, log4), (tree5, m_tree5, log5), (tree6, m_tree6, log6)]))
    # [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4), (tree5, log5), (tree6, log6)]))
    l_with_lock = list(map(lambda tree_log: avg_runtime_with_lock(tree_log[0], tree_log[1], tree_log[2]),
                           [(tree1, m_tree1, log1), (tree2, m_tree2, log2), (tree3, m_tree3, log3),
                            (tree4, m_tree4, log4), (tree5, m_tree5, log5), (tree6, m_tree6, log6)]))
    # [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4), (tree5, log5), (tree6, log6)]))
    plot_histogram_lock_runtime(l_without_lock, l_with_lock)


if __name__ == "__main__":
    compute_run_time()
