from pm4py.objects.process_tree.pt_operator import Operator
from align_repair.pt_manipulate.pt_compare import normal_pt_compare


def merge_child_to_node(node):
    """
    Merge the child' children to the node, if node has the same operator with child, except LOOP

    Parameters
    -----------
    node
        process tree
    """
    children = node.children[:]
    while len(children) > 0:
        child = children.pop(0)
        if node.operator == child.operator and node.operator != Operator.LOOP:
            index = node.children.index(child)
            node.children.pop(index)
            for i in range(len(child.children) - 1, -1, -1):
                node.children.insert(index, child.children[i])
                child.children[i].parent = node


def remove_none_child(node):
    """
    Remove the redundant NONE-child

    Parameters
    -----------
    node
        process tree
    """
    if node.operator == Operator.LOOP:
        for child in node.children:
            if child.operator is not None or child.label is not None:
                return node
        node.operator = None
        node.children = None
    elif node.operator == Operator.SEQUENCE or node.operator == Operator.PARALLEL:
        for i in range(len(node.children) - 1, -1, -1):
            if node.children[i].label is None and node.children[i].operator is None:
                node.children.pop(i)
    elif node.operator == Operator.XOR:
        flag = 0
        for i in range(len(node.children) - 1, -1, -1):
            if node.children[i].label is None and node.children[i].operator is None and flag == 1:
                node.children.pop(i)
            elif node.children[i].label is None and node.children[i].operator is None and flag == 0:
                flag = 1
    return node


def remove_repeat_child(node):
    """
    Remove the repeatable child, if the operator is XOR

    Parameters
    -----------
    node
        process tree
    """
    if node.operator == Operator.XOR:
        children = list()
        for i in range(len(node.children) - 1, -1, -1):
            for child in children:
                same, _, _ = normal_pt_compare(node.children[i], child)
                if not same:
                    children.append(node.children[i])
                else:
                    node.children.pop(i)


def normalize_node(node):
    """
    Normalize the node, e.g. every inner node has at least two children, AND has no NONE child

    Parameters
    -----------
    node
        process tree
    """
    if node.operator is None:
        return
    merge_child_to_node(node)
    remove_none_child(node)
    remove_repeat_child(node)
    while len(node.children) == 1:
        node.label = node.children[0].label
        node.operator = node.children[0].operator
        node.children = node.children[0].children


def recursively_to_general_tree(tree):
    """
    Recursively to generate a normalized tree

    Parameters
    -----------
    tree
        process tree
    """
    if tree.operator is None:
        return
    for i in range(len(tree.children)):
        recursively_to_general_tree(tree.children[i])
    normalize_node(tree)


def parse_to_general_tree(tree):
    """
    Conversion the given process tree to a general process tree, e.g.->(a,->(b,c)) = ->(a,b,c),
    remove repeatable child

    Parameters
    -----------
    tree
        process tree
    """
    recursively_to_general_tree(tree)


def parse_to_general_tree_bfs(tree):
    """
    Conversion the given process tree to a general process tree, e.g.->(a,->(b,c)) = ->(a,b,c)
    BFS -- not so good, which does't consider repeatable NONE label

    Parameters
    -----------
    tree
        process tree
    """
    q = list()
    q.append(tree)
    while len(q) != 0:
        node = q.pop(0)
        while len(node.children) == 1:
            node.label = node.children[0].label
            node.operator = node.children[0].operator
            node.children = node.children[0].children
        children = node.children[:]
        while len(children) > 0:
            child = children.pop(0)
            if node.operator == child.operator and node.operator != Operator.LOOP:
                index = node.children.index(child)
                node.children.pop(index)
                for i in range(len(child.children)-1, -1, -1):
                    node.children.insert(index, child.children[i])
                    child.children[i].parent = node
                    children.append(child.children[i])
            else:
                q.append(child)

