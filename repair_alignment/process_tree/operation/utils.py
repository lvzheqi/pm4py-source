from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.objects.process_tree.process_tree import ProcessTree


def non_none_leaves_labels(tree: ProcessTree):
    q, labels = list(), list()
    q.append(tree)
    while len(q) != 0:
        node = q.pop(0)
        for i in range(len(node.children)):
            q.append(node.children[i])
        labels.append(node.label) if node.operator is None else None
    return labels


def lock_tree_labels(tree: ProcessTree):
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


def non_none_leaves_number(tree):
    return len(non_none_leaves_labels(tree))


def leaves_number(tree: ProcessTree):
    q, num = list(), 0
    q.append(tree)
    while len(q) != 0:
        node = q.pop(0)
        for i in range(len(node.children)):
            q.append(node.children[i])
        num += 1 if node.operator is None else 0
    return num


def parse_tree_to_a_bfs_sequence(tree: ProcessTree):
    q, sequence = list(), list()
    q.append(tree)
    while len(q) != 0:
        node = q.pop(0)
        sequence.append(node)
        for i in range(len(node.children)):
            q.append(node.children[i])
    return sequence


def nodes_number(tree):
    return len(parse_tree_to_a_bfs_sequence(tree))


def pt_depth(tree):
    s_tree, depth, cur_depth = str(tree).strip(), 1, 1
    for i in range(len(s_tree)):
        if s_tree[i] == '(':
            cur_depth += 1
        elif s_tree[i] == ')':
            cur_depth -= 1
        depth = cur_depth if cur_depth > depth else depth
    return depth
