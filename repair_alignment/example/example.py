"""
This module specifies some examples of methods in repair_alignment, including source package,
input variable, output result.
"""

import pm4py
import repair_alignment

from repair_alignment.evaluation import print_event_log, create_event_log, alignment_on_lock_pt


def example_create_random_tree():
    """
    Create random process tree with fixed node number

    Input:
        Number of nodes that need to created
    Output:
        Process Tree
    """
    print_spilt_start("create-random-tree")
    node_number = 10
    tree = repair_alignment.process_tree.generation.stochastic_pt_create.apply(node_number)
    print("Randomly Tree with 10 Nodes (including leaves): \n\t", tree)
    print_spilt_end()


def example_create_mutated_tree():
    """
    Create mutated tree

    Input:
        Process Tree
    Output:
        Mutated Process Tree
    """
    print_spilt_start("create-mutated-tree")
    tree1 = repair_alignment.process_tree.generation.stochastic_pt_create.apply(20)
    tree2 = repair_alignment.process_tree.generation.stochastic_pt_mutate.apply(tree1)
    print("Original Tree:", tree1)
    print("Mutated Tree:", tree2)
    print_spilt_end()


def example_create_non_fitting_event_log():
    """
    Create non fitting event log

    Input:
        Process Tree
        Number of traces
        Probability of non-fitting event
    Output:
        Event Log
    """
    print_spilt_start("create-non-fitting-event-log")
    trace_number, probability_non_fitting = 10, 0.8
    tree = repair_alignment.process_tree.generation.stochastic_pt_create.apply(10)
    log = repair_alignment.process_tree.generation.non_fitting_log_create. \
        apply(tree, trace_number, probability_non_fitting)
    print("Event Log:", end=" ")
    print_event_log(log)
    print_spilt_end()


def example_compare_process_tree():
    """
    Process Tree Compare

    Input:
        Two Process Tree
    Output:
        {VALUE: True/ False, SUB1: subtree1, SUB2: subtree2}
    """
    print_spilt_start("compare-process-tree")
    tree1 = pm4py.objects.process_tree.pt_util.parse("X (a, ->( b, c))")
    tree2 = pm4py.objects.process_tree.pt_util.parse("X (a, *( b, c, τ))")
    result = repair_alignment.process_tree.operation.pt_compare.apply(tree1, tree2)
    print(str(result))
    tree1 = pm4py.objects.process_tree.pt_util.parse("X (a, ->( b, c))")
    tree2 = pm4py.objects.process_tree.pt_util.parse("X (a, ->( b, c))")
    result = repair_alignment.process_tree.operation.pt_compare.apply(tree1, tree2)
    print(str(result))
    print_spilt_end()


def example_number_process_tree():
    """
    Process Tree Number

    Input:
        Process Tree without labels
        Order Type
        Begin Number
    Output:
        Process Tree with labels
    """
    print_spilt_start("number-process-tree")
    tree = repair_alignment.process_tree.generation.stochastic_pt_create.apply(20)
    total_number = repair_alignment.process_tree.operation.pt_number.apply(tree, 'D', 1)
    print("DFS search: There are totally", total_number, "nodes")
    total_number = repair_alignment.process_tree.operation.pt_number.apply(tree, 'B', 1)
    print("BFS search: There are totally", total_number, "nodes")
    print_spilt_end()


def example_pt2pn_with_lock():
    """
    Convert Petri Net to Process Tree with Lock

    Input:
        Process Tree
        Parameters
    Output:
        net, initial_marking, final_marking
    """
    print_spilt_start("pt2pn-without-lock")
    tree = pm4py.objects.process_tree.pt_util.parse("* (a, b, τ)")
    net, _, final_markting = repair_alignment.process_tree.conversion.to_petri_net.apply(tree, )
    gviz = pm4py.visualization.petrinet.factory.apply(net)
    pm4py.visualization.petrinet.factory.view(gviz)

    print_spilt_start("pt2pn-with-lock")
    tree = pm4py.objects.process_tree.pt_util.parse("* (a, b, τ)")
    net, _, _ = repair_alignment.process_tree.conversion.to_petri_net.apply(tree, {
        'PARAM_CHILD_LOCK': True})
    gviz = pm4py.visualization.petrinet.factory.apply(net)
    pm4py.visualization.petrinet.factory.view(gviz)

    tree = pm4py.objects.process_tree.pt_util.parse("* (a, b, τ)")
    net, _, _ = repair_alignment.process_tree.conversion.to_petri_net.apply(tree, {'PARAM_LOOP_LOCK': True})
    gviz = pm4py.visualization.petrinet.factory.apply(net)
    pm4py.visualization.petrinet.factory.view(gviz)

    tree = pm4py.objects.process_tree.pt_util.parse("X (a, τ)")
    net, _, _ = repair_alignment.process_tree.conversion.to_petri_net.apply(tree, {'PARAM_LOOP_LOCK': True})
    gviz = pm4py.visualization.petrinet.factory.apply(net)
    pm4py.visualization.petrinet.factory.view(gviz)
    print("SHOW IN GRAPH")

    print_spilt_end()


def example_lock_alignment_parameters():
    """
    Get corresponding parameters for alignment

    Input:
        Net
    Output:
        Parameters
    """
    print_spilt_start("parameters-with-lock")
    tree = pm4py.objects.process_tree.pt_util.parse("X (a, b)")
    net, _, _ = repair_alignment.process_tree.conversion.to_petri_net.apply(tree, {'PARAM_CHILD_LOCK': True})
    parameters = repair_alignment.algo.utils.align_utils.alignment_parameters(net)
    print("Parameters:", parameters)
    print_spilt_end()


def example_repair_alignment_with_lock():
    """
    Repair Alignment

    Input:
        Two Numbered Process Tree
        Event Log
        Alignment on One Process Tree
    Output:
        Repaired Alignment On Tree2
    """
    print_spilt_start("alignment-repair")
    tree1 = pm4py.objects.process_tree.pt_util.parse("+( a, X( g, h ) ) ")
    tree2 = pm4py.objects.process_tree.pt_util.parse("+( a, ->( g, h ) )")
    repair_alignment.process_tree.operation.pt_number.apply(tree1, 'D', 1)
    repair_alignment.process_tree.operation.pt_number.apply(tree2, 'D', 1)
    log = create_event_log("agh")
    alignment_on_tree1 = alignment_on_lock_pt(tree1, log)

    repaired_alignment = repair_alignment.deprecation.ar_lock. \
        apply(tree1, tree2, log, alignment_on_tree1, {'ret_tuple_as_trans_desc': True})

    print("Tree1:", tree1)
    print("Tree2:", tree2)
    print("Event Log:", end=" ")
    print_event_log(log)
    print("Alignment on Tree1:\n\t", alignment_on_tree1)
    print("Repaired Alignment on Tree2:\n\t", repaired_alignment)
    print_spilt_end()


def example_scope_expand_with_lock():
    """
    Expand scope of lock

    Input:
        Two Numbered Process Tree
        Event Log
        Alignment on One Process Tree
    Output:
       Scope Expanding Alignment of Alignment on Tree1
    """
    print_spilt_start("scope-expand")
    tree1 = repair_alignment.process_tree.generation.stochastic_pt_create.apply(15)
    tree2 = repair_alignment.process_tree.generation.stochastic_pt_mutate.apply(tree1)
    log = repair_alignment.process_tree.generation.non_fitting_log_create.apply(tree2, 1, 0.8)
    repair_alignment.process_tree.operation.pt_number.apply(tree1, 'D', 1)
    alignment_on_tree1 = alignment_on_lock_pt(tree1, log)
    parameters = {'ret_tuple_as_trans_desc': True}
    expand_alignment = repair_alignment.algo.range_detection.se_rd_lock.apply_with_lock(alignment_on_tree1,
                                                                                        tree1, tree2, parameters)

    print("Tree1:", tree1)
    print("Tree2:", tree2)
    print("Event Log:", end=" ")
    print_event_log(log)
    print("Alignment on Tree1:\n\t", alignment_on_tree1)
    print("Scope Expanding Alignment:\n\t", expand_alignment)
    print_spilt_end()


def example_repair_alignment():
    """
    Repair Alignment

    Input:
        Two Numbered Process Tree
        Event Log
    Output:
        Alignment on One Tree1,
        Repaired Alignment On Tree2
    """
    print_spilt_start("optimal-alignment-repair")
    tree1 = pm4py.objects.process_tree.pt_util.parse("+( a, X( g, h ) ) ")
    tree2 = pm4py.objects.process_tree.pt_util.parse("+( a, ->( g, h ) )")
    log = create_event_log("agh")
    parameters = {'ret_tuple_as_trans_desc': True}
    state = repair_alignment.algo.repair.repair.Version.AR_LINEAR
    option = 1
    alignments, repair_alignments = repair_alignment.algo.repair.repair.apply(tree1, tree2, log, state, parameters,
                                                                              option)

    print("Tree1:", tree1)
    print("Tree2:", tree2)
    print("Event Log:", end=" ")
    print_event_log(log)
    print("Alignment on Tree1:\n\t", alignments)
    print("Repaired Alignment on Tree2:\n\t", repair_alignments)
    print_spilt_end()


def print_spilt_start(name):
    print('---------------------------', name, '---------------------------------')


def print_spilt_end():
    print('--------------------------------------------------------------------------------------')


if __name__ == "__main__":
    example_create_random_tree()
    example_create_mutated_tree()
    example_create_non_fitting_event_log()
    example_compare_process_tree()
    example_number_process_tree()
    example_pt2pn_with_lock()
    example_lock_alignment_parameters()
    example_repair_alignment_with_lock()
    example_scope_expand_with_lock()
    example_repair_alignment()
