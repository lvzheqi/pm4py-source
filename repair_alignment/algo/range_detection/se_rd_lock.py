import copy

from pm4py.objects.process_tree.pt_operator import Operator

from repair_alignment.process_tree.operation import pt_compare, utils as pt_mani_utils
from repair_alignment.process_tree.operation.pt_compare import CompareResult
from repair_alignment.algo.range_detection import rd_linear
from repair_alignment.algo.utils import align_utils, tree_utils
from repair_alignment.algo.utils.tree_utils import RangeInterval
from repair_alignment.process_tree.conversion.to_petri_net import LOCK_START, LOCK_END


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
        flag = 0
        children = pt_mani_utils.lock_tree_labels(node)
        print("children", children)
        while not align_utils.is_node_start(align[index], node, ret_tuple_as_trans_desc):
            if not align_utils.check_model_label_belong_to_subtree(align[index], children, ret_tuple_as_trans_desc):
                move_move(align, index, cur_pos)
                cur_pos -= 1
            elif align_utils.is_sync_move(align[index], ret_tuple_as_trans_desc) or index == bound:
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
        flag = 0
        children = pt_mani_utils.lock_tree_labels(node)
        while not align_utils.is_node_end(align[index], node, ret_tuple_as_trans_desc):
            if not align_utils.check_model_label_belong_to_subtree(align[index], children, ret_tuple_as_trans_desc):
                move_move(align, index, cur_pos)
                cur_pos += 1
            elif align_utils.is_sync_move(align[index], ret_tuple_as_trans_desc) or index == bound:
                flag = 1
                break
            index += 1
        if flag == 0:
            block_length = index - cur_pos
            index = find_right_border(node, align, index, bound, ret_tuple_as_trans_desc)
            for i in range(block_length):
                move_move(align, cur_pos, index - 1)
            return index - block_length
        else:
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
                while not align_utils.is_node_start(align[index], node.parent.children[1],
                                                    ret_tuple_as_trans_desc) and \
                        not align_utils.is_node_start(align[index], node.parent.children[2],
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


def add_lock_for_each_node(tree, align, tree_info, mapping_t, ret_tuple_as_trans_desc):
    node_list = pt_mani_utils.parse_tree_to_a_bfs_sequence(tree)
    for node in node_list:
        com_res = CompareResult(True, node, node)
        stop_condition = tree_utils.detect_stop_condition(node, tree_info)
        ranges = rd_linear.apply(align, tree_info, mapping_t, com_res, stop_condition, ret_tuple_as_trans_desc)
        for ri in ranges[::-1]:
            move = ((">>", str(node.index) + LOCK_END + '_1'), (">>", str(node.index) + LOCK_END))
            align.insert(ri.upper_bound + 1, move)
            move = ((">>", str(node.index) + LOCK_START + '1'), (">>", str(node.index) + LOCK_START))
            align.insert(ri.lower_bound, move)


def remove_lock(align, index):
    pos = len(index)
    for i in range(len(align) - 1, -1, -1):
        if align[i][1][1] is not None and (align[i][1][1].endswith(LOCK_START) or align[i][1][1].endswith(LOCK_END)):
            while pos - 1 >= 0 and index[pos - 1] >= i:
                pos -= 1
            for j in range(pos, len(index)):
                if j % 2 == 0 and index[j] == i:
                    pass
                else:
                    index[j] -= 1
            align.pop(i)
    return index


def scope_expand_trace(align, subtree, ret_tuple_as_trans_desc):
    index = search_scope_index(align, subtree, ret_tuple_as_trans_desc)
    left_border = -1
    for i in range(len(index) // 2):
        right_border = min(len(align), index[(i + 1) * 2]) if (i + 1) * 2 < len(index) else len(align)
        find_left_border(subtree, align, index[i * 2], left_border, ret_tuple_as_trans_desc)
        left_border = find_right_border(subtree, align, index[i * 2 + 1], right_border, ret_tuple_as_trans_desc)
    return align


def apply_with_lock(alignments, tree, m_tree, option=1):
    alignments = copy.deepcopy(alignments)
    com_res = pt_compare.apply(tree, m_tree, option)
    if not com_res.value:
        for align in alignments:
            if align.get("expand") is None:
                scope_expand_trace(align["alignment"], com_res.subtree1, True)
                align["expand"] = True
        for a in alignments:
            a.pop("expand") if a.get("expand") is not None else None
    return alignments


def apply(align, tree_info, mapping_t, com_res, ret_tuple_as_trans_desc):
    add_lock_for_each_node(tree_info[1].tree, align, tree_info, mapping_t, ret_tuple_as_trans_desc)
    scope_expand_trace(align, com_res.subtree1, ret_tuple_as_trans_desc)
    index = search_scope_index(align, com_res.subtree1, ret_tuple_as_trans_desc)
    index = remove_lock(align, index)
    ranges = list()
    for j in range(len(index) // 2):
        ranges.append(RangeInterval(index[j * 2], index[j * 2 + 1]))
    return ranges
