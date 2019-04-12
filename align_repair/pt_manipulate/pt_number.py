from pm4py.objects.process_tree.pt_operator import Operator


def dfs_number(tree, index=1):
    """
    Number the nodes of tree according to DFS

    Parameters
    -----------
    tree
        Process Tree
    index
        the label of root

    Returns
    ----------
    index
        total number of nodes
    """
    return recursively_dfs(tree, index)


def bfs_number(tree, index=1):
    """
    Number the nodes of tree according to BFS

    Parameters
    -----------
    tree
        Process Tree
    index
        the label of root

    Returns
    ----------
    index
        total number of nodes
    """
    return recursively_bfs(tree, index)


def recursively_dfs(tree, index=1):
    tree.index = index
    for i in range(len(tree.children)):
        index = recursively_dfs(tree.children[i], index + 1)
    return index


def recursively_bfs(tree, index):
    q = list()
    q.append(tree)
    while len(q) != 0:
        node = q.pop(0)
        node.index = index
        index += 1
        for i in range(len(node.children)):
            q.append(node.children[i])
    return index


def parse_tree_to_a_bfs_sequence(tree):
    q, sequence = list(), list()
    q.append(tree)
    while len(q) != 0:
        node = q.pop(0)
        sequence.append(node)
        for i in range(len(node.children)):
            q.append(node.children[i])
    return sequence


# the last child of loop dont consider as a leaf
def get_leaves_labels(tree):
    q, labels = list(), list()
    q.append(tree)
    while len(q) != 0:
        node = q.pop(0)
        for i in range(len(node.children)):
            q.append(node.children[i])
        if node.operator is None:
            labels.append(node.label)
        # elif node.operator == Operator.LOOP:
        #     q.pop()
    return labels


def get_all_labels(tree):
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
            if node.operator == Operator.PARALLEL:
                    # or node.operator == Operator.LOOP:
                labels.append(str(node.index) + "_tau")
            # if node.operator == Operator.LOOP:
            #     q.pop()
    return labels
