import time

from pm4py.algo.discovery.inductive.util.petri_el_count import Counts
from pm4py.objects import petri
from pm4py.objects.petri.petrinet import Marking
from pm4py.algo.discovery.inductive.versions.dfg.util.petri_el_add import get_new_place, get_new_hidden_trans, \
    get_transition
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.objects.process_tree.pt_operator import Operator

from align_repair.pt_manipulate.utils import LOCK_START, LOCK_END

SOURCE_NAME = "source"
SINK_NAME = "SINK"


def recursively_get_node_index(tree, index, node_end):
    """
    Returns Largest index number of the descendant for each node related to DFS

    Parameters
    -----------
        tree
            Current subtree
        index
            DFS Index Number of the root
        node_end
            Store the largest index number of the descendant for each node
    Returns
    ------------
    index
        Largest index number of the descendant
    """
    cur_pos = index
    if tree.operator is not None:
        tree_childs = [child for child in tree.children]
        for i in range(len(tree_childs)):
            index = recursively_get_node_index(tree_childs[i], index + 1, node_end)
    node_end[cur_pos] = index
    return index


def recursively_add_tree(tree, net, initial_entity_subtree, final_entity_subtree, counts, index, node_end,
                         param_child_lock):
    cur_pos = index
    if type(initial_entity_subtree) is PetriNet.Transition:
        initial_place = get_new_place(counts)
        net.places.add(initial_place)
        petri.utils.add_arc_from_to(initial_entity_subtree, initial_place, net)
    else:
        initial_place = initial_entity_subtree
    if final_entity_subtree is not None and type(final_entity_subtree) is PetriNet.Place:
        final_place = final_entity_subtree
    else:
        final_place = get_new_place(counts)
        net.places.add(final_place)
        if final_entity_subtree is not None and type(final_entity_subtree) is PetriNet.Transition:
            petri.utils.add_arc_from_to(final_place, final_entity_subtree, net)

    intermediate_place_s, intermediate_place_e = initial_place, final_place
    if param_child_lock or tree.operator is not None:
        intermediate_place_s = get_new_place(counts)
        net.places.add(intermediate_place_s)
        # petri_trans = get_new_hidden_trans(counts, type_trans=str(index)+"_start")
        petri_trans = get_transition(counts, str(cur_pos) + LOCK_START)
        net.transitions.add(petri_trans)

        petri.utils.add_arc_from_to(initial_place, petri_trans, net)
        petri.utils.add_arc_from_to(petri_trans, intermediate_place_s, net)

        intermediate_place_e = get_new_place(counts)
        net.places.add(intermediate_place_e)
        # petri_trans = get_new_hidden_trans(counts, type_trans=str(index)+"_end")
        petri_trans = get_transition(counts, str(cur_pos) + LOCK_END)
        net.transitions.add(petri_trans)
        petri.utils.add_arc_from_to(intermediate_place_e, petri_trans, net)
        petri.utils.add_arc_from_to(petri_trans, final_place, net)

    if tree.operator is not None:
        # intermediate_place_s = initial_place
        # intermediate_place_e = final_place

        tree_childs = [child for child in tree.children]
        if tree.operator == Operator.XOR:
            for subtree in tree_childs:
                recursively_add_tree(subtree, net, intermediate_place_s, intermediate_place_e, counts,
                                     index+1, node_end, param_child_lock)
                index = node_end[index + 1]

        elif tree.operator == Operator.PARALLEL:
            new_initial_trans = get_new_hidden_trans(counts, type_trans=str(cur_pos) + "_tau")
            net.transitions.add(new_initial_trans)
            petri.utils.add_arc_from_to(intermediate_place_s, new_initial_trans, net)
            new_final_trans = get_new_hidden_trans(counts, type_trans=str(cur_pos) + "_tau")
            net.transitions.add(new_final_trans)
            petri.utils.add_arc_from_to(new_final_trans, intermediate_place_e, net)

            for subtree in tree_childs:
                recursively_add_tree(subtree, net, new_initial_trans, new_final_trans, counts, index + 1, node_end, param_child_lock)
                index = node_end[index + 1]

        elif tree.operator == Operator.SEQUENCE:
            intermediate_place = intermediate_place_s
            for i in range(len(tree_childs)):
                if i == len(tree_childs) - 1:
                    final_connection_place = intermediate_place_e
                else:
                    final_connection_place = None
                intermediate_place = recursively_add_tree(tree_childs[i], net, intermediate_place,
                                                          final_connection_place, counts, index + 1,
                                                          node_end, param_child_lock)
                index = node_end[index + 1]

        elif tree.operator == Operator.LOOP:
            if intermediate_place_s.name == SOURCE_NAME:
                petri_trans = get_new_hidden_trans(counts, type_trans=str(cur_pos) + "_tau")
                net.transitions.add(petri_trans)
                petri.utils.add_arc_from_to(intermediate_place_s, petri_trans, net)
                intermediate_place_s = get_new_place(counts)
                net.places.add(intermediate_place_s)
                petri.utils.add_arc_from_to(petri_trans, intermediate_place_s, net)

            intermediate_place = recursively_add_tree(tree_childs[0], net, intermediate_place_s, None, counts,
                                                      index+1, node_end, param_child_lock)
            index = node_end[index + 1]
            recursively_add_tree(tree_childs[1], net, intermediate_place, intermediate_place_s, counts,
                                 index+1, node_end, param_child_lock)

            index = node_end[index + 1]
            recursively_add_tree(tree_childs[2], net, intermediate_place, intermediate_place_e, counts,
                                 index + 1, node_end, param_child_lock)
            # loop_trans = get_new_hidden_trans(counts, type_trans=str(cur_pos) + "_tau")
            # net.transitions.add(loop_trans)
            # petri.utils.add_arc_from_to(intermediate_place, loop_trans, net)
            # petri.utils.add_arc_from_to(loop_trans, intermediate_place_e, net)

    elif tree.operator is None:
        if tree.label is None:
            petri_trans = get_new_hidden_trans(counts, type_trans=str(cur_pos) + "_skip")
        else:
            petri_trans = get_transition(counts, tree.label)
        net.transitions.add(petri_trans)
        petri.utils.add_arc_from_to(intermediate_place_s, petri_trans, net)
        petri.utils.add_arc_from_to(petri_trans, intermediate_place_e, net)

    return final_place


def generate_pn(tree, net, initial_entity_subtree, final_entity_subtree, counts, param_child_lock=False):
    """
    Recursively converse the subtrees into a Petri net

    Parameters
    -----------
    tree
        Current subtree
    net
        Petri net
    initial_entity_subtree
        Initial entity (place/transition) that should be attached from the subtree
    final_entity_subtree
        Final entity (place/transition) that should be attached from the subtree
    counts
        Counts object (keeps the number of places, transitions and hidden transitions)
    param_child_lock
        True indicates that the child also needs to add start_lock and end_lock
    """
    node_end = dict()
    index = 1 if tree.index == 0 else tree.index
    recursively_get_node_index(tree, index, node_end)
    recursively_add_tree(tree, net, initial_entity_subtree, final_entity_subtree, counts, index, node_end,
                         param_child_lock)


def apply_with_operator(tree, parameters=None):
    """
    Conversion Process Tree to PetriNet.

    Parameters
    -----------
    tree
        Process tree
    parameters
        PARAM_CHILD_LOCK

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """

    counts = Counts()
    net = petri.petrinet.PetriNet('imdf_net_' + str(time.time()))
    initial_marking = Marking()
    final_marking = Marking()
    source = get_new_place(counts)
    source.name = SOURCE_NAME
    sink = get_new_place(counts)
    sink.name = SINK_NAME
    net.places.add(source)
    net.places.add(sink)
    initial_marking[source] = 1
    final_marking[sink] = 1
    param_child_lick = parameters['PARAM_CHILD_LOCK'] if parameters is not None else True
    generate_pn(tree, net, source, sink, counts, param_child_lick)

    return net, initial_marking, final_marking
