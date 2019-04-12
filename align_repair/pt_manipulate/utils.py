from pm4py.algo.conformance.alignments import utils as align_utils


LOCK_END = "_e"
LOCK_START = "_s"


def is_node_start(move, node, ret_tuple_as_trans_desc=False):
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[0] == align_utils.SKIP and move[1] == str(node.index) + LOCK_START


def is_node_end(move, node, ret_tuple_as_trans_desc=False):
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[0] == align_utils.SKIP and move[1] == str(node.index) + LOCK_END


def is_move_log(move, ret_tuple_as_trans_desc=False):  # (a, >>)
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[0] != align_utils.SKIP and move[1] == align_utils.SKIP


def is_move_model(move, ret_tuple_as_trans_desc=False):     # (>>, a)
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[0] == align_utils.SKIP and move[1] != align_utils.SKIP


def is_sync_move(move, ret_tuple_as_trans_desc=False):
    move = move[1] if ret_tuple_as_trans_desc else move
    return move[0] == move[1]


def compare_log_move(move1, move2, ret_tuple_as_trans_desc=False):
    move1 = move1[1] if ret_tuple_as_trans_desc else move1
    move2 = move2[1] if ret_tuple_as_trans_desc else move2
    return move1[0] == move2[0]


def check_tuple_belong_to_subtree(move, children, ret_tuple_as_trans_desc=False):
    """
    Check, that alignment tuple belongs to the subtree1
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


# def check_tuple_belong_to_subtree(move, children):
#     """
#     Check, that alignment tuple belongs to the subtree1
#     :return:
#     """
#     align_label = move[1]
#     align_name = move[0]
#     if align_label[1] == align_utils.SKIP or align_label[1] in children:
#         return True
#     if align_label[0] == align_utils.SKIP:
#         s_name = align_name[1].split("_")
#         if len(s_name) == 3 and "".join([s_name[0], "_", s_name[1]]) in children:
#             return True
#     return False
