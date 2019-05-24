"""
This module compares the time of alignment on PetriNet with Lock or without Lock.
And returns the histogram of the comparison.
"""
import time
import random

from align_repair.process_tree.stochastic_generation import stochastic_pt_create as pt_create
from align_repair.process_tree.stochastic_generation import non_fitting_log_create as log_create
from align_repair.process_tree.alignments import to_lock_align
from align_repair.evaluation import alignment_on_lock_pt, alignment_on_pt, alignment_on_loop_lock_pt
from align_repair.process_tree.manipulation import pt_number


def avg_runtime_without_lock(trees, logs):
    start = time.time()
    for i, tree in enumerate(trees):
        alignment_on_pt(tree, logs[i])
    end = time.time()
    print((end - start) / len(trees))
    return (end - start) / len(trees)


def avg_runtime_with_lock(trees, logs):
    start = time.time()
    for i, tree in enumerate(trees):
        alignment_on_loop_lock_pt(tree, logs[i])
    end = time.time()
    print((end - start) / len(trees))
    return (end - start) / len(trees)


def avg_runtime_with_add_lock(trees, logs):
    start = time.time()
    for i, tree in enumerate(trees):
        alignments = alignment_on_loop_lock_pt(tree, logs[i])
        pt_number.apply(tree)
        to_lock_align.apply(tree, alignments)
    end = time.time()
    print((end - start) / len(trees))
    return (end - start) / len(trees)


def plot_histogram_lock_runtime(list1, list2):
    """
    Compared the time of alignment of PT with lock and without lock
    """
    import matplotlib.pyplot as plt

    # label_list = ["10-15", "16-20", "21-25", "26-30"]
    label_list = ["10-15", "16-20", "21-25", "26-30", "31-33", "34-35"]
    x = range(len(list1))
    plt.bar(x=x, height=list1, width=0.4, alpha=0.8, color="red", label="without Lock")
    plt.bar(x=[i + 0.4 for i in x], height=list2, width=0.4, color="green", label="with Lock")
    plt.xlabel("Number of Node")
    plt.ylabel("Time(Seconds)")
    plt.xticks([i + 0.2 for i in x], label_list)
    plt.title("Compare Runtime of Alignment with/-out Lock")
    plt.legend()
    # for rect in rects1:
    #     height = rect.get_height()
    #     plt.text(rect.get_x() + rect.get_width() / 2, height + 1, str(height), ha="center", va="bottom")
    # for rect in rects2:
    #     height = rect.get_height()
    #     plt.text(rect.get_x() + rect.get_width() / 2, height + 1, str(height), ha="center", va="bottom")
    plt.savefig("ComparePNTime")


def compute_run_time():
    no_tree, no_event, pro = 10, 10, 0.8
    tree1 = [pt_create.apply(random.randint(11, 15)) for _ in range(no_tree)]
    log1 = [log_create.apply(tree, no_event, pro) for tree in tree1]
    tree2 = [pt_create.apply(random.randint(16, 20)) for _ in range(no_tree)]
    log2 = [log_create.apply(tree, no_event, pro) for tree in tree2]
    tree3 = [pt_create.apply(random.randint(21, 25)) for _ in range(no_tree)]
    log3 = [log_create.apply(tree, no_event, pro) for tree in tree3]
    tree4 = [pt_create.apply(random.randint(26, 30)) for _ in range(no_tree)]
    log4 = [log_create.apply(tree, no_event, pro) for tree in tree4]
    # tree5 = [pt_create.apply(random.randint(31, 33)) for _ in range(no_tree)]
    # log5 = [log_create.apply(tree, no_event, pro) for tree in tree5]
    # tree6 = [pt_create.apply(random.randint(34, 35)) for _ in range(no_tree)]
    # log6 = [log_create.apply(tree, no_event, pro) for tree in tree6]
    # l_without_lock = list(map(lambda tree_log: avg_runtime_without_lock(tree_log[0], tree_log[1]),
    #                           [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4)]))
    # [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4), (tree5, log5), (tree6, log6)]))
    l_with_lock = list(map(lambda tree_log: avg_runtime_with_lock(tree_log[0], tree_log[1]),
                           [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4)]))
                           # [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4), (tree5, log5), (tree6, log6)]))

    l_add_lock = list(map(lambda tree_log: avg_runtime_with_add_lock(tree_log[0], tree_log[1]),
                          [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4)]))
                          # [(tree1, log1), (tree2, log2), (tree3, log3), (tree4, log4), (tree5, log5), (tree6, log6)]))
    # plot_histogram_lock_runtime(l_without_lock, l_with_lock)
    plot_histogram_lock_runtime(l_with_lock, l_add_lock)


if __name__ == "__main__":
    compute_run_time()
