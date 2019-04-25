import copy

from pm4py.objects.process_tree.pt_operator import Operator

from align_repair.process_tree.manipulation import pt_compare, utils as pt_mani_utils
from align_repair.process_tree.alignments import utils as pt_align_utils


def search_scope_index(align, node):
    """
    Return the border index list of the node in alignment.

    Parameters
    ------------
    ------------
    align
        alignment on the original process tree of one trace
    node
        `Process tree` the subtree that to detect

    Returns
    ---------
    index
        `list()` [start_pos, end_pos, start_pos, end_pos....]
    """
    index = list()
    for i, move in enumerate(align):
        index.append(i) if pt_align_utils.is_node_start(move, node, True) or \
                           pt_align_utils.is_node_end(move, node, True) else None
    return index


def find_next_left_border(align, index, node, start_or_end, bound):
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

    Returns
    -----------
    index
        the position of the next left border
    """

    if start_or_end == 1:
        while not pt_align_utils.is_node_start(align[index], node, True):
            index -= 1
    else:
        while not pt_align_utils.is_node_end(align[index], node, True):
            index -= 1
    return find_left_border(node, align, index, bound)


def find_left_border(node, align, cur_pos, bound):
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

    if pt_align_utils.is_node_end(align[index], node, True):
        while not pt_align_utils.is_node_start(align[index], node, True):
            index -= 1

        index_s = find_left_border(node, align, index, bound) if index > bound else bound

        index = cur_pos
        children = pt_mani_utils.lock_tree_labels(node)
        while index != index_s:
            if not pt_align_utils.check_model_label_belong_to_subtree(align[index], children, True):
                move_move(align, index, cur_pos)
                cur_pos -= 1
            elif pt_align_utils.is_sync_move(align[index], True):
                break
            index -= 1
        return cur_pos

    elif pt_align_utils.is_node_start(align[index], node, True):
        # parent is not NONE, otherwise index = 0
        if node.parent.operator == Operator.PARALLEL or node.parent.operator == Operator.XOR:
            index = find_next_left_border(align, index, node.parent, 1, bound)

        elif node.parent.operator == Operator.SEQUENCE:
            child_no = 0
            for i in range(len(node.parent.children)):
                if node.parent.children[i].index == node.index:
                    child_no = i
                    break
            if child_no == 0:
                index = find_next_left_border(align, index, node.parent, 1, bound)
            else:
                index = find_next_left_border(align, index, node.parent.children[child_no - 1], 0, bound)

        elif node.parent.operator == Operator.LOOP:

            if node.parent.children[0].index == node.index:    # first child
                while not pt_align_utils.is_node_end(align[index], node.parent.children[1], True) and \
                        not pt_align_utils.is_node_start(align[index], node.parent, True):
                    index -= 1
                if pt_align_utils.is_node_end(align[index], node.parent.children[1], True):
                    index = find_left_border(node.parent.children[1], align, index, bound)
                else:
                    index = find_left_border(node.parent, align, index, bound)

            else:   # second child
                index = find_next_left_border(align, index, node.parent.children[0], 0, bound)

    move_move(align, cur_pos, index + 1)
    return index + 1


def find_next_right_border(align, index, node, start_or_end, border):
    if start_or_end == 1:
        while not pt_align_utils.is_node_start(align[index], node, True):
            index += 1
    else:
        while not pt_align_utils.is_node_end(align[index], node, True):
            index += 1
    return find_right_border(node, align, index, border)


def find_right_border(node, align, cur_pos, bound):
    index = cur_pos
    if index == bound:
        return index
    elif index > bound:
        return bound

    if node.parent is None:
        move_move(align, cur_pos, len(align) - 1)
        return len(align) - 1

    if pt_align_utils.is_node_start(align[index], node, True):
        while not pt_align_utils.is_node_end(align[index], node, True):
            index += 1

        index_s = find_right_border(node, align, index, bound) if index < bound else bound

        flag, index = 0, cur_pos
        children = pt_mani_utils.lock_tree_labels(node)
        while index != index_s:
            if not pt_align_utils.check_model_label_belong_to_subtree(align[index], children, True):
                move_move(align, index, cur_pos)
                cur_pos += 1
            elif pt_align_utils.is_sync_move(align[index], True):
                break
            index += 1
        return cur_pos

    elif pt_align_utils.is_node_end(align[index], node, True):
        # parent is not NONE, otherwise index = 0

        if node.parent.operator == Operator.PARALLEL or node.parent.operator == Operator.XOR:
            index = find_next_right_border(align, index, node.parent, 0, bound)

        elif node.parent.operator == Operator.SEQUENCE:
            child_no = 0
            for i in range(len(node.parent.children)):
                if node.parent.children[i].index == node.index:
                    child_no = i
                    break
            if child_no == len(node.parent.children) - 1:
                index = find_next_right_border(align, index, node.parent, 0, bound)
            else:
                index = find_next_right_border(align, index, node.parent.children[child_no + 1], 1, bound)

        elif node.parent.operator == Operator.LOOP:
            if node.parent.children[0].index == node.index:  # first child
                while not pt_align_utils.is_node_start(align[index], node.parent.children[1], True) and \
                        not pt_align_utils.is_node_start(align[index], node.parent.children[2], True):
                    index += 1
                if pt_align_utils.is_node_start(align[index], node.parent.children[1], True):
                    index = find_right_border(node.parent.children[1], align, index, bound)
                else:
                    index = find_right_border(node.parent.children[2], align, index, bound)
            elif node.parent.children[1].index == node.index:    # second child
                index = find_next_right_border(align, index, node.parent.children[0], 1, bound)
            else:
                index = find_next_right_border(align, index, node.parent, 0, bound)
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


def scope_expand_trace(align, subtree):
    index = search_scope_index(align, subtree)
    left_border = -1
    for i in range(len(index)//2):
        right_border = min(len(align), index[(i+1) * 2]) if (i + 1) * 2 < len(index) else len(align)
        find_left_border(subtree, align, index[i * 2], left_border)
        left_border = find_right_border(subtree, align, index[i * 2 + 1], right_border)
    return align


def apply(alignments, tree, m_tree):
    alignments = copy.deepcopy(alignments)
    com_res = pt_compare.apply(tree, m_tree)
    if not com_res.value:
        for align in alignments:
            if align.get("expand") is None:
                scope_expand_trace(align["alignment"], com_res.subtree1)
                align["expand"] = True
        for a in alignments:
            a.pop("expand") if a.get("expand") is not None else None
    return alignments
