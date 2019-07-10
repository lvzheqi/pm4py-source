import copy

from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE

from repair_alignment.process_tree.operation import pt_compare, utils as pt_mani_utils
from repair_alignment.algo.utils import align_utils


def search_scope_index(align, node, ret_tuple_as_trans_desc):
    """
    Return the border index list of the node in alignment.

    Parameters
    ------------
    align
        alignment on the original process tree of one trace
    node
        `Process tree` the subtree that to detect
    ret_tuple_as_trans_desc
        True or False

    Returns
    ---------
    index
        `list()` [start_pos, end_pos, start_pos, end_pos....]
    """
    index = list()
    for i, move in enumerate(align):
        index.append(i) if align_utils.is_node_start(move, node, ret_tuple_as_trans_desc) or \
                           align_utils.is_node_end(move, node, ret_tuple_as_trans_desc) else None
    return index


def find_next_left_border(align, index, node, start_or_end, bound, ret_tuple_as_trans_desc):
    """
    Return the position of next left border

    Parameters
    -------------
    align
        alignment on the original process tree of one trace
    index
        the current position
    node
        the related node of next left border
    start_or_end
        start=1 and end=0
    bound
        the leftest boundary that muss stop
    ret_tuple_as_trans_desc
        True or False

    Returns
    -----------
    index
        the position of the next left border
    """

    if start_or_end == 1:
        while not align_utils.is_node_start(align[index], node, ret_tuple_as_trans_desc):
            index -= 1
    else:
        while not align_utils.is_node_end(align[index], node, ret_tuple_as_trans_desc):
            index -= 1
    return find_left_border(node, align, index, bound, ret_tuple_as_trans_desc)


def find_left_border(node, align, cur_pos, bound, ret_tuple_as_trans_desc):
    """
    Iteratively move the left border(align[cur_pos]) util meet the stop condition and
    return the the leftest border of the scope for the given subtree
    Stop condition:
        1. meet boundary
        2. meet the sync-move if the alignment-move is node-end

    Parameters
    -----------
    node
        `Process Tree` the related subtree of the current alignment-move
    align
        `list()` alignment on the original process tree of one trace
    cur_pos
        the position of the border that need to expand
    bound
        the leftest boundary that muss stop
    ret_tuple_as_trans_desc
        True or False

    Returns
    -----------
    index
        The current position of the left border
    """

    index = cur_pos
    if index <= bound:
        return bound

    if node.parent is None:
        move_move(align, cur_pos, 0)
        return 0

    if align_utils.is_node_end(align[index], node, ret_tuple_as_trans_desc):
        while not align_utils.is_node_start(align[index], node, ret_tuple_as_trans_desc):
            index -= 1

        index_s = find_left_border(node, align, index, bound, ret_tuple_as_trans_desc) if index > bound else bound

        index = cur_pos
        children = pt_mani_utils.lock_tree_labels(node)
        while index != index_s:
            if not align_utils.check_model_label_belong_to_subtree(align[index], children, ret_tuple_as_trans_desc):
                move_move(align, index, cur_pos)
                cur_pos -= 1
            elif align_utils.is_sync_move(align[index], ret_tuple_as_trans_desc):
                break
            index -= 1
        return cur_pos

    elif align_utils.is_node_start(align[index], node, ret_tuple_as_trans_desc):
        # parent is not NONE, otherwise index = 0
        if node.parent.operator == Operator.PARALLEL or node.parent.operator == Operator.XOR:
            index = find_next_left_border(align, index, node.parent, 1, bound, ret_tuple_as_trans_desc)

        elif node.parent.operator == Operator.SEQUENCE:
            child_no = 0
            for i in range(len(node.parent.children)):
                if node.parent.children[i].index == node.index:
                    child_no = i
                    break
            if child_no == 0:
                index = find_next_left_border(align, index, node.parent, 1, bound, ret_tuple_as_trans_desc)
            else:
                index = find_next_left_border(align, index, node.parent.children[child_no - 1], 0, bound,
                                              ret_tuple_as_trans_desc)

        elif node.parent.operator == Operator.LOOP:

            if node.parent.children[0].index == node.index:  # first child
                while not align_utils.is_node_end(align[index], node.parent.children[1],
                                                  ret_tuple_as_trans_desc) and \
                        not align_utils.is_node_start(align[index], node.parent, ret_tuple_as_trans_desc):
                    index -= 1
                if align_utils.is_node_end(align[index], node.parent.children[1], ret_tuple_as_trans_desc):
                    index = find_left_border(node.parent.children[1], align, index, bound, ret_tuple_as_trans_desc)
                else:
                    index = find_left_border(node.parent, align, index, bound, ret_tuple_as_trans_desc)

            else:  # second child
                index = find_next_left_border(align, index, node.parent.children[0], 0, bound, ret_tuple_as_trans_desc)

    move_move(align, cur_pos, index + 1)
    return index + 1


def find_next_right_border(align, index, node, start_or_end, border, ret_tuple_as_trans_desc):
    if start_or_end == 1:
        while not align_utils.is_node_start(align[index], node, ret_tuple_as_trans_desc):
            index += 1
    else:
        while not align_utils.is_node_end(align[index], node, ret_tuple_as_trans_desc):
            index += 1
    return find_right_border(node, align, index, border, ret_tuple_as_trans_desc)


def find_right_border(node, align, cur_pos, bound, ret_tuple_as_trans_desc):
    index = cur_pos
    if index == bound:
        return index
    elif index > bound:
        return bound

    if node.parent is None:
        move_move(align, cur_pos, len(align) - 1)
        return len(align) - 1

    if align_utils.is_node_start(align[index], node, ret_tuple_as_trans_desc):
        while not align_utils.is_node_end(align[index], node, ret_tuple_as_trans_desc):
            index += 1

        index_s = find_right_border(node, align, index, bound, ret_tuple_as_trans_desc) if index < bound else bound

        flag, index = 0, cur_pos
        children = pt_mani_utils.lock_tree_labels(node)
        while index != index_s:
            if not align_utils.check_model_label_belong_to_subtree(align[index], children, ret_tuple_as_trans_desc):
                move_move(align, index, cur_pos)
                cur_pos += 1
            elif align_utils.is_sync_move(align[index], ret_tuple_as_trans_desc):
                break
            index += 1
        return cur_pos

    elif align_utils.is_node_end(align[index], node, ret_tuple_as_trans_desc):
        # parent is not NONE, otherwise index = 0

        if node.parent.operator == Operator.PARALLEL or node.parent.operator == Operator.XOR:
            index = find_next_right_border(align, index, node.parent, 0, bound, ret_tuple_as_trans_desc)

        elif node.parent.operator == Operator.SEQUENCE:
            child_no = 0
            for i in range(len(node.parent.children)):
                if node.parent.children[i].index == node.index:
                    child_no = i
                    break
            if child_no == len(node.parent.children) - 1:
                index = find_next_right_border(align, index, node.parent, 0, bound, ret_tuple_as_trans_desc)
            else:
                index = find_next_right_border(align, index, node.parent.children[child_no + 1], 1, bound,
                                               ret_tuple_as_trans_desc)

        elif node.parent.operator == Operator.LOOP:
            if node.parent.children[0].index == node.index:  # first child
                while not align_utils.is_node_start(align[index], node.parent.children[1], ret_tuple_as_trans_desc) \
                        and not align_utils.is_node_start(align[index], node.parent.children[2],
                                                          ret_tuple_as_trans_desc):
                    index += 1
                if align_utils.is_node_start(align[index], node.parent.children[1], ret_tuple_as_trans_desc):
                    index = find_right_border(node.parent.children[1], align, index, bound, ret_tuple_as_trans_desc)
                else:
                    index = find_right_border(node.parent.children[2], align, index, bound, ret_tuple_as_trans_desc)
            elif node.parent.children[1].index == node.index:  # second child
                index = find_next_right_border(align, index, node.parent.children[0], 1, bound, ret_tuple_as_trans_desc)
            else:
                index = find_next_right_border(align, index, node.parent, 0, bound, ret_tuple_as_trans_desc)
    move_move(align, cur_pos, index - 1)
    return index - 1


def move_move(align, cur_pos, index):
    """
    Pop the align-move at position cur_pos and insert into position index

    Parameters
    ------------
    align
        alignment
    cur_pos
        current position
    index
        the position that will be insert after pop
    """
    move = align.pop(cur_pos)
    align.insert(index, move)


def scope_expand_trace(align, subtree, ret_tuple_as_trans_desc):
    index = search_scope_index(align, subtree, ret_tuple_as_trans_desc)
    left_border = -1
    for i in range(len(index) // 2):
        right_border = min(len(align), index[(i + 1) * 2]) if (i + 1) * 2 < len(index) else len(align)
        find_left_border(subtree, align, index[i * 2], left_border, ret_tuple_as_trans_desc)
        left_border = find_right_border(subtree, align, index[i * 2 + 1], right_border, ret_tuple_as_trans_desc)
    return align


def apply(alignments, tree, m_tree, parameters=None):
    parameters = {} if parameters is None else parameters
    parameters['COMPARE_OPTION'] = 1 if parameters.get('COMPARE_OPTION') is None else parameters['COMPARE_OPTION']
    ret_tuple_as_trans_desc = False if parameters.get(PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE) is None else \
        parameters[PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE]
    alignments = copy.deepcopy(alignments)
    com_res = pt_compare.apply(tree, m_tree, parameters['COMPARE_OPTION'])
    if not com_res.value:
        for align in alignments:
            if align.get("expand") is None:
                scope_expand_trace(align["alignment"], com_res.subtree1, ret_tuple_as_trans_desc)
                align["expand"] = True
        for a in alignments:
            a.pop("expand") if a.get("expand") is not None else None
    return alignments
