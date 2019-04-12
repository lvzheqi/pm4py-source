from pm4py.objects.process_tree.pt_operator import Operator
from align_repair.pt_manipulate import pt_number
from align_repair.pt_manipulate.utils import is_node_start, is_node_end, is_sync_move, check_tuple_belong_to_subtree


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

    Returns
    ---------
    index
        `list()` [start_pos, end_pos, start_pos, end_pos....]
    """
    index = list()
    for i, move in enumerate(align):
        if is_node_start(move, node, ret_tuple_as_trans_desc) or is_node_end(move, node, ret_tuple_as_trans_desc):
            index.append(i)
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

    Returns
    -----------
    index
        the position of the next left border
    """

    if start_or_end == 1:
        while not is_node_start(align[index], node, ret_tuple_as_trans_desc):
            index -= 1
    else:
        while not is_node_end(align[index], node, ret_tuple_as_trans_desc):
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

    Returns
    -----------
    index
        The current position of the left border
    """

    index = cur_pos
    if index == bound:
        return index

    if node.parent is None:
        move_move(align, cur_pos, 0)
        return 0

    if is_node_end(align[index], node, ret_tuple_as_trans_desc):
        flag = 0
        children = pt_number.get_all_labels(node)
        while not is_node_start(align[index], node, ret_tuple_as_trans_desc):
            if not check_tuple_belong_to_subtree(align[index], children, ret_tuple_as_trans_desc):
                move_move(align, index, cur_pos)
                cur_pos -= 1
            elif is_sync_move(align[index], ret_tuple_as_trans_desc):
                flag = 1
                break
            index -= 1
        if flag == 0:
            block_length = cur_pos - index
            index = find_left_border(node, align, index, bound, ret_tuple_as_trans_desc)
            for i in range(block_length):
                move_move(align, cur_pos, index + 1)
            return index + block_length
        else:
            return cur_pos

    elif is_node_start(align[index], node, ret_tuple_as_trans_desc):
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

            if node.parent.children[0].index == node.index:    # first child
                while not is_node_end(align[index], node.parent.children[1], ret_tuple_as_trans_desc) and \
                        not is_node_start(align[index], node.parent, ret_tuple_as_trans_desc):
                    index -= 1
                if is_node_end(align[index], node.parent.children[1], ret_tuple_as_trans_desc):
                    index = find_left_border(node.parent.children[1], align, index, bound, ret_tuple_as_trans_desc)
                else:
                    index = find_left_border(node.parent, align, index, bound, ret_tuple_as_trans_desc)

            else:   # second child
                index = find_next_left_border(align, index, node.parent.children[0], 0, bound, ret_tuple_as_trans_desc)

    # if node.parent.operator == Operator.PARALLEL:
    #     if node.operator == Operator.PARALLEL:
    #         move_move(align, cur_pos + 1, index + 2)
    #         cur_pos += 1
    #     move_move(align, cur_pos, index + 2)
    #     return index + 2
    # else:
    #     if node.operator == Operator.PARALLEL:
    #         move_move(align, cur_pos + 1, index + 1)
    #         cur_pos += 1
    move_move(align, cur_pos, index + 1)
    return index + 1


def find_next_right_border(align, index, node, start_or_end, border, ret_tuple_as_trans_desc):
    if start_or_end == 1:
        while not is_node_start(align[index], node, ret_tuple_as_trans_desc):
            index += 1
    else:
        while not is_node_end(align[index], node, ret_tuple_as_trans_desc):
            index += 1
    return find_right_border(node, align, index, border, ret_tuple_as_trans_desc)


def find_right_border(node, align, cur_pos, border, ret_tuple_as_trans_desc):
    index = cur_pos
    if index == border:
        return index

    if node.parent is None:
        move_move(align, cur_pos, len(align) - 1)
        return len(align) - 1

    if is_node_start(align[index], node, ret_tuple_as_trans_desc):
        flag = 0
        children = pt_number.get_all_labels(node)
        while not is_node_end(align[index], node, ret_tuple_as_trans_desc):
            if not check_tuple_belong_to_subtree(align[index], children, ret_tuple_as_trans_desc):
                move_move(align, index, cur_pos)
                cur_pos += 1
            elif is_sync_move(align[index], ret_tuple_as_trans_desc):
                flag = 1
                break
            index += 1
        if flag == 0:
            block_length = index - cur_pos
            index = find_right_border(node, align, index, border, ret_tuple_as_trans_desc)
            for i in range(block_length):
                move_move(align, cur_pos, index - 1)
            return index - block_length
        else:
            return cur_pos

    elif is_node_end(align[index], node, ret_tuple_as_trans_desc):
        # parent is not NONE, otherwise index = 0

        if node.parent.operator == Operator.PARALLEL or node.parent.operator == Operator.XOR:
            index = find_next_right_border(align, index, node.parent, 0, border, ret_tuple_as_trans_desc)

        elif node.parent.operator == Operator.SEQUENCE:
            child_no = 0
            for i in range(len(node.parent.children)):
                if node.parent.children[i].index == node.index:
                    child_no = i
                    break
            if child_no == len(node.parent.children) - 1:
                index = find_next_right_border(align, index, node.parent, 0, border, ret_tuple_as_trans_desc)
            else:
                index = find_next_right_border(align, index, node.parent.children[child_no + 1], 1, border,
                                               ret_tuple_as_trans_desc)

        elif node.parent.operator == Operator.LOOP:
            if node.parent.children[0].index == node.index:  # first child
                while not is_node_start(align[index], node.parent.children[1], ret_tuple_as_trans_desc) and \
                        not is_node_start(align[index], node.parent.children[2], ret_tuple_as_trans_desc):
                    index += 1
                if is_node_start(align[index], node.parent.children[1], ret_tuple_as_trans_desc):
                    index = find_right_border(node.parent.children[1], align, index, border, ret_tuple_as_trans_desc)
                else:
                    index = find_right_border(node.parent.children[2], align, index, border, ret_tuple_as_trans_desc)
            elif node.parent.children[1].index == node.index:    # second child
                index = find_next_right_border(align, index, node.parent.children[0], 1, border, ret_tuple_as_trans_desc)
            else:
                index = find_next_right_border(align, index, node.parent, 0, border, ret_tuple_as_trans_desc)

    # if node.parent.operator == Operator.PARALLEL:
    #     if node.operator == Operator.PARALLEL:
    #         move_move(align, cur_pos - 1, index - 2)
    #         cur_pos -= 1
    #     move_move(align, cur_pos, index - 2)
    #     return index - 2
    # else:
    #     if node.operator == Operator.PARALLEL:
    #         move_move(align, cur_pos - 1, index - 1)
    #         cur_pos -= 1
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
    left_border = 0
    for i in range(len(index)//2):
        right_border = min(len(align) - 1, index[(i+1) * 2]) if (i + 1) * 2 < len(index) else len(align) - 1
        find_left_border(subtree, align, index[i * 2], left_border, ret_tuple_as_trans_desc)
        left_border = find_right_border(subtree, align, index[i * 2 + 1], right_border, ret_tuple_as_trans_desc)
    return align


def scope_expand(alignments, subtree, ret_tuple_as_trans_desc):
    for align in alignments:
        new_align = scope_expand_trace(align["alignment"], subtree, ret_tuple_as_trans_desc)
        align["alignment"] = new_align
    return alignments
