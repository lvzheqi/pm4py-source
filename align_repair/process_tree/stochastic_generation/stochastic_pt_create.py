import random

from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.objects.process_tree.pt_operator import Operator

from align_repair.process_tree.manipulation import pt_normalize
from align_repair.process_tree.stochastic_generation import utils as pt_gene_utils


def add_label_to_leaf(children):
    """
    Randomly create labels and Add label to leafs of the tree

    Parameters
    -----------
    children
        list of Process tree that has no child
    """
    for i, child in enumerate(children):
        child.label = pt_gene_utils.get_cur_label(i + 1)


def create_pt_of_three_node(root, op):
    child1, child2 = ProcessTree(), ProcessTree()
    root.children = [child1, child2]
    root.operator = op
    child1.parent = root
    child2.parent = root
    if op == Operator.LOOP:
        root.children.append(ProcessTree(None, root, None, None))
    return [child1, child2]


def create_new_binary_process_tree(no_number):
    """
    Random create a new tree with fixed node number

    Parameters
    -----------
    no_number
        Node number of the created process tree

    Returns
    ------------
    tree
        Process Tree (None, if there no normal process tree with such node)
    """
    root = ProcessTree()
    if no_number == 1:
        return ProcessTree(None, None, None, 'a')
    if no_number == 2:
        return None
    operators, enable, cur_num = [_ for _ in Operator], [root], 1
    while cur_num + 3 <= no_number:
        node = random.choice(enable)
        enable.remove(node)
        children = create_pt_of_three_node(node, random.choice(operators))
        enable += children
        if node.parent is not None and node.operator == node.parent.operator and node.operator != Operator.LOOP:
            cur_num += 1
        elif node.operator == Operator.LOOP:
            cur_num += 3
        else:
            cur_num += 2
    if no_number - cur_num == 1:    # must be agree with parent and not equal LOOP
        flag = False
        for i in range(len(enable)):
            if enable[i].parent.operator != Operator.LOOP:
                node = enable.pop(i)
                children = create_pt_of_three_node(node, node.parent.operator)
                enable += children
                flag = True
                break
        while not flag:
            root = create_new_binary_process_tree(no_number)
            flag = False if root is None else True
            print('could not create a tree, try again!!! Maybe infinite!!!')
    elif no_number - cur_num == 2:  # must differ with parent and not equal LOOP
        node = random.choice(enable)
        enable.remove(node)
        op = random.choice(operators)
        while op == Operator.LOOP or (node.parent is not None and op == node.parent.operator)\
                or node.parent is None:
            op = random.choice(operators)
        children = create_pt_of_three_node(node, op)
        enable += children

    add_label_to_leaf(enable)
    return root


def apply(no_number):
    """
    Random create a new tree with fixed node number

    Parameters
    -----------
    no_number
        Node number of the created process tree

    Returns
    ------------
    tree
        Process Tree
    """
    tree = create_new_binary_process_tree(no_number)
    pt_normalize.apply(tree) if tree is not None else None
    return tree
