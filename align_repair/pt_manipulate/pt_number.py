"""
This module provides method for number the nodes of the process tree.
"""
from pm4py.objects.process_tree.process_tree import ProcessTree


def pt_number(tree, search='D', index=1):
    """
    Number the nodes of given process tree with specified type

    Parameters
    -----------
    tree
        Process Tree
    search
        'D' indicated using DFS to number the order
    index
        the label of root


    Returns
    --------------
        Return the total number of nodes
    """
    return _dfs_number(tree, index) if search == 'D' else _bfs_number(tree, index)


def _dfs_number(tree, index):
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
    tree.index = index
    for i in range(len(tree.children)):
        index = _dfs_number(tree.children[i], index + 1)
    return index


def _bfs_number(tree: ProcessTree, index):
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
    q = list()
    q.append(tree)
    while len(q) != 0:
        node = q.pop(0)
        node.index = index
        index += 1
        for i in range(len(node.children)):
            q.append(node.children[i])
    return index - 1

