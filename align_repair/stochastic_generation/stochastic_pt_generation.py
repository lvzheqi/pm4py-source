import random

from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.objects.process_tree.pt_operator import Operator
from align_repair.pt_manipulate.pt_normalize import parse_to_general_tree


def get_cur_label(no_number):
    """
    Return a unique label for the current node

    Parameters
    -----------
    no_number
        The number of the node, each leaf-node has a unique number

    Returns
    ------------
    Label
        Unique label of current node
    """
    # return 'label_' + str(no_number)
    return chr(no_number + 96)


def add_label_to_leaf(children):
    """
    Randomly create labels and Add label to leafs of the tree

    Parameters
    -----------
    children
        list of Process tree that has no child
    """
    for i, child in enumerate(children):
        child.label = get_cur_label(i + 1)


def create_pt_of_three_node(root, op):
    child1, child2 = ProcessTree(), ProcessTree()
    root.children = [child1, child2]
    root.operator = op
    child1.parent = root
    child2.parent = root
    if op == Operator.LOOP:
        root.children.append(ProcessTree())
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
    boolean
        True if the PT could be built
    tree
        Process Tree
    """
    root = ProcessTree()
    if no_number == 1:
        return True, ProcessTree(None, None, None, 'a')
    if no_number == 2:
        return False, None
    operators, enable, cur_num = [_ for _ in Operator], [root], 1
    while cur_num + 3 <= no_number:
        node = enable.pop(random.randint(0, len(enable)-1))
        children = create_pt_of_three_node(node, operators[random.randint(0, 3)])
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
            flag, root = create_new_binary_process_tree(no_number)
            print('could not create a tree, try again!!! Maybe infinite!!!')
    elif no_number - cur_num == 2:  # must differ with parent and not equal LOOP
        node = enable.pop(random.randint(0, len(enable) - 1))
        op = operators[random.randint(0, 3)]
        while op == Operator.LOOP or (node.parent is not None and op == node.parent.operator)\
                or node.parent is None:
            op = operators[random.randint(0, 3)]
        children = create_pt_of_three_node(node, op)
        enable += children

    add_label_to_leaf(enable)
    return True, root


def randomly_create_new_tree(no_number):
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
    success, tree = create_new_binary_process_tree(no_number)
    parse_to_general_tree(tree) if success else None
    return success, tree
