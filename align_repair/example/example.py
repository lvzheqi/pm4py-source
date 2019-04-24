"""
This module specifies some examples of methods in align_repair, including source package,
input variable, output result.
"""

import pm4py
import align_repair

from align_repair.evaluation import print_event_log, create_event_log, alignment_on_lock_pt


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
    tree = align_repair.stochastic_generation.stochastic_pt_generation.randomly_create_new_tree(node_number)
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
    tree1 = align_repair.stochastic_generation.stochastic_pt_generation.randomly_create_new_tree(20)
    tree2 = align_repair.stochastic_generation.stochastic_mutated_pt.randomly_create_mutated_tree(tree1)
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
    tree = align_repair.stochastic_generation.stochastic_pt_generation.randomly_create_new_tree(10)
    log = align_repair.stochastic_generation.non_fitting_eventlog_generation.\
        create_non_fitting_eventlog(tree, trace_number, probability_non_fitting)
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
    result = align_repair.pt_manipulate.pt_compare.pt_compare(tree1, tree2)
    print(str(result))
    tree1 = pm4py.objects.process_tree.pt_util.parse("X (a, ->( b, c))")
    tree2 = pm4py.objects.process_tree.pt_util.parse("X (a, ->( b, c))")
    result = align_repair.pt_manipulate.pt_compare.pt_compare(tree1, tree2)
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
    tree = align_repair.stochastic_generation.stochastic_pt_generation.randomly_create_new_tree(20)
    total_number = align_repair.pt_manipulate.pt_number.pt_number(tree, 'D', 1)
    print("DFS search: There are totally", total_number, "nodes")
    total_number = align_repair.pt_manipulate.pt_number.pt_number(tree, 'B', 1)
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
    print_spilt_start("pt2pn-with-lock")
    tree = align_repair.stochastic_generation.stochastic_pt_generation.randomly_create_new_tree(20)
    net, initial_marking, final_marking = align_repair.pt_align.to_petri_net_with_operator.apply_with_operator(tree)
    gviz = pm4py.visualization.petrinet.factory.apply(net)
    pm4py.visualization.petrinet.factory.view(gviz)
    print("SHOW IN GRAPH")
    print_spilt_end()


def example_get_with_lock_parameters():
    """
    Get corresponding parameters for alignment

    Input:
        Net
    Output:
        Parameters
    """
    print_spilt_start("parameters-with-lock")
    tree = pm4py.objects.process_tree.pt_util.parse("X (a, b)")
    net, _, _ = align_repair.pt_align.to_petri_net_with_operator.apply_with_operator(tree)
    parameters = align_repair.pt_align.utils.get_parameters(net)
    print("Parameters:", parameters)
    print_spilt_end()


def example_repair_alignment():
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
    align_repair.pt_manipulate.pt_number.pt_number(tree1, 'D', 1)
    align_repair.pt_manipulate.pt_number.pt_number(tree2, 'D', 1)
    log = create_event_log("agh")
    alignment_on_tree1 = alignment_on_lock_pt(tree1, log)

    repaired_alignment = align_repair.repair.align_repair.\
        alignment_repair_with_operator_align(tree1, tree2, log, alignment_on_tree1)

    print("Tree1:", tree1)
    print("Tree2:", tree2)
    print("Event Log:", end=" ")
    print_event_log(log)
    print("Alignment on Tree1:\n\t", alignment_on_tree1)
    print("Repaired Alignment on Tree2:\n\t", repaired_alignment)
    print_spilt_end()


def example_scope_expand():
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
    tree1 = align_repair.stochastic_generation.stochastic_pt_generation.randomly_create_new_tree(15)
    tree2 = align_repair.stochastic_generation.stochastic_mutated_pt.randomly_create_mutated_tree(tree1)
    log = align_repair.stochastic_generation.non_fitting_eventlog_generation.create_non_fitting_eventlog(tree2, 1, 0.8)
    align_repair.pt_manipulate.pt_number.pt_number(tree1, 'D', 1)
    alignment_on_tree1 = alignment_on_lock_pt(tree1, log)
    expand_alignment = align_repair.repair.scope_expand.scope_expand(alignment_on_tree1, tree1, tree2)

    print("Tree1:", tree1)
    print("Tree2:", tree2)
    print("Event Log:", end=" ")
    print_event_log(log)
    print("Alignment on Tree1:\n\t", alignment_on_tree1)
    print("Scope Expanding Alignment:\n\t", expand_alignment)
    print_spilt_end()


def example_general():
    """
    A concrete general example

    Input:
        Two Numbered Process Tree
        Event Log
        Alignment on One Process Tree
    Output:
       Scope Expanding Alignment of Alignment on Tree1
    """
    print_spilt_start("general-scope-expand")
    tree1 = align_repair.stochastic_generation.stochastic_pt_generation.randomly_create_new_tree(15)
    tree2 = align_repair.stochastic_generation.stochastic_mutated_pt.randomly_create_mutated_tree(tree1)
    log = align_repair.stochastic_generation.non_fitting_eventlog_generation.create_non_fitting_eventlog(tree2, 1, 0.8)
    align_repair.pt_manipulate.pt_number.pt_number(tree1, 'D', 1)
    alignment_on_tree1 = alignment_on_lock_pt(tree1, log)
    optimal_alignment_on_tree2 = align_repair.repair.scope_expand.scope_expand(alignment_on_tree1, tree1, tree2)
    direct_repaired_alignment = align_repair.repair.align_repair. \
        alignment_repair_with_operator_align(tree1, tree2, log, alignment_on_tree1)
    expand_alignment = align_repair.repair.scope_expand.scope_expand(alignment_on_tree1, tree1, tree2)
    scoped_repaired_alignment = align_repair.repair.align_repair. \
        alignment_repair_with_operator_align(tree1, tree2, log, expand_alignment)

    print("Tree1:", tree1)
    print("Tree2:", tree2)
    print("Event Log:", end=" ")
    print_event_log(log)
    print("Alignment on Tree1:\n\t", alignment_on_tree1)
    print("Optimal Alignment on Tree2:\n\t", optimal_alignment_on_tree2)
    print("Directly Repaired alignment on Tree2:\n\t", direct_repaired_alignment)
    print("Expanding Repaired alignment on Tree2:\n\t", scoped_repaired_alignment)

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
    example_get_with_lock_parameters()
    example_repair_alignment()
    example_scope_expand()
    example_general()
