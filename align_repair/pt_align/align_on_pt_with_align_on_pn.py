from pm4py.objects.process_tree.pt_operator import Operator


# False

def get_children_labels(tree, index, labels, node_end):
    cur_pos = index
    if tree.operator is not None:
        tree_childs = [child for child in tree.children]
        labels[cur_pos] = list()
        for i in range(len(tree_childs)):
            child_pos = index + 1
            index = get_children_labels(tree_childs[i], index + 1, labels, node_end)
            labels[cur_pos] += labels[child_pos]
    elif tree.label is not None:
        labels[index] = [tree.label]
    else:
        labels[index] = list()
    node_end[cur_pos] = index
    return index


def recusive_alignemnt_on_pt_trace(tree, alignment, labels, node_end, alignment_pt, index=1):
    tree_childs = [child for child in tree.children]

    if tree.operator is not None:
        cur_pos = index
        alignment_pt.append(('>>', str(cur_pos) + '_s'))
        if tree.operator == Operator.SEQUENCE:
            for i in range(len(tree_childs)):
                index = recusive_alignemnt_on_pt_trace(tree_childs[i], alignment,
                                                       labels, node_end, alignment_pt, index + 1)
        elif tree.operator == Operator.XOR:
            if check_next(alignment, labels[cur_pos]):
                for i in range(len(tree_childs)):
                    if check_next(alignment, labels[index+1]):
                        recusive_alignemnt_on_pt_trace(tree_childs[i], alignment, labels, node_end,
                                                       alignment_pt, index + 1)
                        break
                    else:
                        index = node_end[index + 1]
            else:   # skip
                add_move(alignment_pt, alignment)
                for i in range(len(tree_childs)):
                    if tree_childs[i].operator is None and tree_childs[i].label is None:
                        recusive_alignemnt_on_pt_trace(tree_childs[i], alignment, labels, node_end,
                                                       alignment_pt, index + 1)
                        break
                    else:
                        index = node_end[index + 1]
            index = node_end[cur_pos]

        elif tree.operator == Operator.PARALLEL:
            add_move(alignment_pt, alignment)
            subnode_index = [0 for _ in range(len(tree_childs))]
            subnode_index[0] = index + 1
            for i in range(1, len(tree_childs)):
                subnode_index[i] = node_end[subnode_index[i - 1]] + 1
            children = [i for i in range(len(tree_childs))]
            while len(children) != 0:
                child_num = children[0]
                children.pop(0)
                if check_next(alignment, labels[subnode_index[child_num]]):
                    index = recusive_alignemnt_on_pt_trace(tree_childs[child_num], alignment,
                                                           labels, node_end, alignment_pt, subnode_index[child_num])
                else:
                    children.append(child_num)
            add_move(alignment_pt, alignment)

        elif tree.operator == Operator.LOOP:
            if alignment[0][1] is None and len(alignment_pt) == 0:
                add_move(alignment_pt, alignment)
            while check_next(alignment, labels[cur_pos]):
                index = cur_pos
                # first child
                index = recusive_alignemnt_on_pt_trace(tree_childs[0], alignment, labels, node_end,
                                                       alignment_pt, index + 1)
                # second child
                if check_next(alignment, labels[cur_pos]):
                    recusive_alignemnt_on_pt_trace(tree_childs[1], alignment, labels, node_end, alignment_pt,
                                                   index + 1)
                # restart or exit
                add_move(alignment_pt, alignment)
            index = node_end[cur_pos]
        alignment_pt.append(('>>', str(cur_pos) + '_e'))
    else:
        add_move(alignment_pt, alignment)
        while len(alignment) != 0 and alignment[0][1] == '>>' and alignment[0][0] is not None:
            add_move(alignment_pt, alignment)
    return index


def check_next(alignment, labels):
    if len(alignment) > 0:
        label, i = alignment[0][1], 1
    else:
        return False
    while label is None and i < len(alignment):
        label = alignment[i][1]
        i += 1
    return True if label is not None and label in labels else False


def add_move(alignment_pt, alignment):
    alignment_pt.append(alignment[0])
    alignment.pop(0)


def alignments_on_process_tree(tree, alignments):
    labels, node_end, alignments_pt = dict(), dict(), list()
    get_children_labels(tree, 1, labels, node_end)
    for alignment in alignments:
        alignment_pn, alignment_pt = alignment['alignment'], list()
        recusive_alignemnt_on_pt_trace(tree, alignment_pn, labels, node_end, alignment_pt, 1)
        if len(alignment_pn) > 0:
            print(alignment_pn)
            print("Error by alignment")
        move_on_innner_node = 0
        for t in alignment_pt:
            if t[0] == '>>' and t[1] is not None and len(t[1]) == 3 and (t[1][1:] == '_s' or t[1][1:] == '_e'):
                move_on_innner_node += 1
        alignments_pt += [{'alignment': alignment_pt, 'cost': alignment['cost'] + move_on_innner_node,
                          'fitness': alignment['fitness']}]
    return alignments_pt



