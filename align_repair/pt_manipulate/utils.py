from pm4py.algo.conformance.alignments import utils as align_utils
from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.objects.process_tree.process_tree import ProcessTree


LOCK_END = "_e"
LOCK_START = "_s"


def is_node_start(move, node, ret_tuple_as_trans_desc=False):
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[0] == align_utils.SKIP and move[1] == str(node.index) + LOCK_START


def is_node_end(move, node, ret_tuple_as_trans_desc=False):
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[0] == align_utils.SKIP and move[1] == str(node.index) + LOCK_END


def is_log_move(move, ret_tuple_as_trans_desc=False):  # (a, >>)
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[0] != align_utils.SKIP and move[1] == align_utils.SKIP


def is_model_move(move, ret_tuple_as_trans_desc=False):     # (>>, a)
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[0] == align_utils.SKIP and move[1] != align_utils.SKIP


def is_sync_move(move, ret_tuple_as_trans_desc=False):
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[0] == move[1]


def compare_log_label(move1, move2, ret_tuple_as_trans_desc=False):
    move1 = move1[1] if ret_tuple_as_trans_desc else move1
    move2 = move2[1] if ret_tuple_as_trans_desc else move2
    return move1[0] == move2[0]


def check_model_label_belong_to_subtree(move, children, ret_tuple_as_trans_desc=False):
    """
    Check, that alignment model label belongs to the subtree1
    :return:
    """
    align_label = move[1] if ret_tuple_as_trans_desc else move
    align_name = move[0] if ret_tuple_as_trans_desc else move
    if align_label[1] in children:
        return True
    if align_label[0] == align_utils.SKIP:
        s_name = align_name[1].split("_")
        if len(s_name) == 3 and "".join([s_name[0], "_", s_name[1]]) in children:
            return True
    return False


def get_non_none_leaves_labels(tree: ProcessTree):
    q, labels = list(), list()
    q.append(tree)
    while len(q) != 0:
        node = q.pop(0)
        for i in range(len(node.children)):
            q.append(node.children[i])
        labels.append(node.label) if node.operator is None else None
    return labels


def get_non_none_leaves_number(tree):
    return len(get_non_none_leaves_labels(tree))


def get_lock_tree_labels(tree: ProcessTree):
    q, labels = list(), list()
    q.append(tree)
    while len(q) != 0:
        node = q.pop(0)
        labels += [str(node.index) + "_s", str(node.index) + "_e"]
        for i in range(len(node.children)):
            q.append(node.children[i])
        if node.operator is None and node.label is not None:
            labels.append(node.label)
        elif node.operator is None and node.label is None:
            labels.append(str(node.index) + "_skip")
        elif node.operator is not None:
            labels.append(str(node.index) + "_tau") if node.operator == Operator.PARALLEL else None
    return labels


def parse_tree_to_a_bfs_sequence(tree: ProcessTree):
    q, sequence = list(), list()
    q.append(tree)
    while len(q) != 0:
        node = q.pop(0)
        sequence.append(node)
        for i in range(len(node.children)):
            q.append(node.children[i])
    return sequence


def get_pt_nodes_number(tree):
    return len(parse_tree_to_a_bfs_sequence(tree))
