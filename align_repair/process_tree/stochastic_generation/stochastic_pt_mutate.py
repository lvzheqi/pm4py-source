import random
import copy

from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.objects.process_tree.pt_operator import Operator

from align_repair.process_tree.manipulation import pt_normalize
from align_repair.process_tree.manipulation import utils as pt_mani_utils
from align_repair.process_tree.stochastic_generation import utils as pt_gene_utils


def randomly_choose_node(tree, level):
    """
    Randomly choose an inner node

    Parameters
    -----------
    tree
        Original Process Tree
    level
        The maximal depth of the chosen node
    Returns
    ------------
    node
        The inner node that be selected, except root
    """
    level = pt_mani_utils.pt_depth(tree) if level is None else min(pt_mani_utils.pt_depth(tree), level)
    node_sequence = pt_mani_utils.parse_tree_to_a_bfs_sequence(tree)
    node = random.choice(node_sequence)
    while node.operator is None or pt_mani_utils.pt_depth(node) > level:
        node = random.choice(node_sequence)
    return node


def add_new_node(tree, level):
    """
    Randomly select an inner node, and add a new child, and ensure that it satisfies the tree rules.

    Parameters
    -----------
    tree
        Original Process Tree
    level
        The maximal depth of the chosen node
    """
    node = randomly_choose_node(tree, level)
    tmp_node = copy.deepcopy(node)
    add_node = ProcessTree(None, node, None,
                           pt_gene_utils.get_cur_label(pt_mani_utils.non_none_leaves_number(tree) + 1))
    if node.operator == Operator.LOOP:
        child = node.children[1]
        new_child = ProcessTree(Operator.XOR, node, [child, add_node], None)
        child.parent = new_child
        add_node.parent = new_child
        node.children[1] = new_child
    else:
        node.children.append(add_node)
    return tmp_node, node


def remove_node(tree, level):
    """
    Randomly select one node, and remove one of the child

    Parameters
    -----------
    tree
        Original Process Tree
    level
        The maximal depth of the chosen node
    """

    node = randomly_choose_node(tree, level)
    tmp_node = copy.deepcopy(node)
    if node.operator == Operator.LOOP:
        node.children[random.randint(0, 1)] = ProcessTree(None, node, None, None)
    else:
        node.children.remove(random.choice(node.children))
    pt_normalize.apply(tree)
    return tmp_node, node


def change_node_operator(tree, level):
    """
    Randomly select an inner node, and replace the operator using others,
    and ensure that it satisfies the tree rules.

    Parameters
    -----------
    tree
        Original Process Tree
    level
        The maximal depth of the chosen node
    """
    node = randomly_choose_node(tree, level)
    tmp_node = copy.deepcopy(node)
    operators = [_ for _ in Operator]
    op = random.choice(operators)
    while op == node.operator:
        op = random.choice(operators)
    if op == Operator.LOOP:
        while len(node.children) > 2:
            node.children.pop()
        node.children.append(ProcessTree(None, node, None, None))
    node.operator = op
    return tmp_node, node


def apply(tree, level=None):
    """
    Slightly change the given tree, e.g. randomly adding a new node, randomly removing a node, Or
    Randomly change a node of the tree

    Parameters
    -----------
    tree
        Original Process Tree
    level
        The maximal depth of the chosen node

    Returns
    ------------
    mutated_tree
        New Process Tree that be randomly changed
    """
    mutated_tree = copy.deepcopy(tree)
    index = random.randint(0, 2)
    if index == 0:
        add_new_node(mutated_tree, level)
    elif index == 1:
        remove_node(mutated_tree, level)
    elif index == 2:
        change_node_operator(mutated_tree, level)
    return mutated_tree
