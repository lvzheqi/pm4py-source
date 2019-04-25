from pm4py.algo.conformance.alignments import utils as align_utils
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_MODEL_COST_FUNCTION, \
    PARAM_SYNC_COST_FUNCTION, PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE
from pm4py.algo.conformance.alignments.utils import STD_SYNC_COST, STD_TAU_COST


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


def check_model_label_belong_to_subtree(move, subtree_labels, ret_tuple_as_trans_desc=False):
    """
    Check, that alignment model label belongs to the subtree
    :return:
    """
    align_label = move[1] if ret_tuple_as_trans_desc else move
    align_name = move[0] if ret_tuple_as_trans_desc else move
    if align_label[1] in subtree_labels:
        return True
    if align_label[0] == align_utils.SKIP:
        s_name = align_name[1].split("_")
        if len(s_name) == 3 and "".join([s_name[0], "_", s_name[1]]) in subtree_labels:
            return True
    return False


def alignment_parameters(net):
    model_cost_function, sync_cost_function = dict(), dict()
    for t in net.transitions:
        if t.label is not None and not t.label.endswith(LOCK_START) and not t.label.endswith(LOCK_END):
            model_cost_function[t] = 2
            sync_cost_function[t] = STD_SYNC_COST
        else:
            model_cost_function[t] = STD_TAU_COST

    return {PARAM_MODEL_COST_FUNCTION: model_cost_function, PARAM_SYNC_COST_FUNCTION: sync_cost_function,
            PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE: True}
