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


def is_none_move(move, ret_tuple_as_trans_desc=False):
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[0] == align_utils.SKIP and move[1] is None


def model_label(move, ret_tuple_as_trans_desc=False):
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[1]


def log_label(move, ret_tuple_as_trans_desc=False):
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[0]


def node_index_for_silent_move(move, ret_tuple_as_trans_desc=False):
    align_name = move[0] if ret_tuple_as_trans_desc else move
    try:
        s_name = align_name[1].split("_")
        return s_name[0]
    except Exception as e:
        print(e)
        print("can't conclude the related tree for None label")


def compare_log_label(move1, move2, ret_tuple_as_trans_desc=False):
    move1 = move1[1] if ret_tuple_as_trans_desc else move1
    move2 = move2[1] if ret_tuple_as_trans_desc else move2
    return move1[0] == move2[0]


def move_index(move, mapping_t, ret_tuple_as_trans_desc):
    if is_none_move(move, ret_tuple_as_trans_desc):
        return int(node_index_for_silent_move(move, ret_tuple_as_trans_desc))
    else:
        label = model_label(move, ret_tuple_as_trans_desc)
        if label.endswith('_s') or label.endswith('_e'):
            return int(label[:-2])
        else:
            return mapping_t[label]


def move_in_subtree(move, tree_range, mapping_t):
    if is_log_move(move, True):
        return True
    return tree_range.is_in_range(move_index(move, mapping_t, True))


def check_model_label_belong_to_subtree(move, subtree_labels, ret_tuple_as_trans_desc=False):
    """
    Check, that alignment model label belongs to the subtree
    :return:
    """
    align_label = move[1] if ret_tuple_as_trans_desc else move
    align_name = move[0] if ret_tuple_as_trans_desc else move
    if align_label[1] in subtree_labels:
        return True
    if align_label[0] == align_utils.SKIP and ret_tuple_as_trans_desc:
        s_name = align_name[1].split("_")
        if len(s_name) == 3 and "".join([s_name[0], "_", s_name[1]]) in subtree_labels:
            return True
    if align_label[0] == align_utils.SKIP and not ret_tuple_as_trans_desc:
        return True
    return False


def alignment_parameters(net, std_mod_cost=2):
    model_cost_function, sync_cost_function = dict(), dict()
    for t in net.transitions:
        if t.label is not None and not t.label.endswith(LOCK_START) and not t.label.endswith(LOCK_END):
            model_cost_function[t] = std_mod_cost
            sync_cost_function[t] = STD_SYNC_COST
        else:
            model_cost_function[t] = STD_TAU_COST

    return {PARAM_MODEL_COST_FUNCTION: model_cost_function, PARAM_SYNC_COST_FUNCTION: sync_cost_function,
            PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE: True}
