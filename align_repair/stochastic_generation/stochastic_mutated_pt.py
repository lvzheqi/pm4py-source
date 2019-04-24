import random, copy

from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.objects.process_tree.pt_operator import Operator

from align_repair.pt_manipulate.pt_normalize import parse_to_general_tree
from align_repair.pt_manipulate import utils as pt_mani_utils
from align_repair.stochastic_generation.stochastic_pt_generation import get_cur_label


def randomly_choose_node(tree):
    """
    Randomly choose an inner node

    Parameters
    -----------
    tree
        Original Process Tree

    Returns
    ------------
    node
        The inner node that be selected, except root
    """
    node_sequence = pt_mani_utils.parse_tree_to_a_bfs_sequence(tree)
    index = random.randint(0, len(node_sequence) - 1)
    while node_sequence[index].operator is None:
        index = random.randint(0, len(node_sequence) - 1)
    return node_sequence[index]


def add_new_node(tree):
    """
    Randomly select an inner node, and add a new child, and ensure that it satisfies the tree rules.

    Parameters
    -----------
    tree
        Original Process Tree
    """
    node = randomly_choose_node(tree)
    tmp_node = copy.deepcopy(node)
    add_node = ProcessTree(None, node, None,
                           get_cur_label(pt_mani_utils.get_non_none_leaves_number(tree) + 1))
    if node.operator == Operator.LOOP:
        child = node.children[1]
        new_child = ProcessTree(Operator.XOR, node, [child, add_node], None)
        child.parent = new_child
        add_node.parent = new_child
        node.children[1] = new_child
    else:
        node.children.append(add_node)
    return tmp_node, node


def remove_node(tree):
    """
    Randomly select one node, and remove one of the child

    Parameters
    -----------
    tree
        Original Process Tree
    """

    node = randomly_choose_node(tree)
    tmp_node = copy.deepcopy(node)
    if node.operator == Operator.LOOP:
        node.children[random.randint(0, 1)] = ProcessTree(None, node, None, None)
    else:
        node.children.pop(random.randint(0, len(node.children) - 1))
    parse_to_general_tree(tree)
    return tmp_node, node


def change_node_operator(tree):
    """
    Randomly select an inner node, and replace the operator using others,
    and ensure that it satisfies the tree rules.

    Parameters
    -----------
    tree
        Original Process Tree
    """
    node = randomly_choose_node(tree)
    tmp_node = copy.deepcopy(node)
    operators = [_ for _ in Operator]
    index = random.randint(0, len(operators) - 1)
    while operators[index] == node.operator:
        index = random.randint(0, len(operators) - 1)
    if operators[index] == Operator.LOOP:
        while len(node.children) > 2:
            node.children.pop()
        node.children.append(ProcessTree(None, node, None, None))
    node.operator = operators[index]
    return tmp_node, node


def randomly_create_mutated_tree(tree):
    """
    Slightly change the given tree, e.g. randomly adding a new node, randomly removing a node, Or
    Randomly change a node of the tree

    Parameters
    -----------
    tree
        Original Process Tree

    Returns
    ------------
    mutated_tree
        New Process Tree that be randomly changed
    """
    mutated_tree = copy.deepcopy(tree)
    index = random.randint(0, 2)
    if index == 0:
        add_new_node(mutated_tree)
    elif index == 1:
        remove_node(mutated_tree)
    elif index == 2:
        change_node_operator(mutated_tree)
    return mutated_tree
