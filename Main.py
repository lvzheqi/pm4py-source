import os
import copy

from pm4py.objects.log.importer.xes.factory import iterparse_xes as xes_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.algo.conformance.alignments import factory as align_factory
from pm4py.objects.conversion.process_tree import factory as pt_to_net
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.visualization.process_tree import factory as pt_vis_factory
from pm4py.objects.process_tree import util as pt_util

from align_repair.pt_align import to_petri_net_with_operator as pt_to_net_with_op
from align_repair.stochastic_generation.stochastic_pt_generation import randomly_create_new_tree
from align_repair.stochastic_generation.stochastic_mutated_pt import randomly_create_mutated_tree
from align_repair.stochastic_generation.non_fitting_eventlog_generation import create_non_fitting_eventlog
from align_repair.pt_manipulate.pt_compare import pt_compare
from align_repair.pt_manipulate import pt_number
from pm4py.objects.log.util import xes
from align_repair.repair.align_repair import alignment_repair_with_operator
from pm4py.objects.log.log import EventLog, Trace, Event
from align_repair.repair.scope_expand import scope_expand
from align_repair.evaluation.evaluation import compare_run_time, alignment_quality


def print_spilt_end():
    print('----------------------------------------------------------------------------')


def print_spilt_start(name):
    print('---------------------------', name, '---------------------------------')


def non_fit_eventlog(node, no, prob):
    print_spilt_start("non-fit-eventlog")
    _, tree = randomly_create_new_tree(node)
    print("Tree:", tree)
    # gviz = pt_vis_factory.apply(tree)
    # pt_vis_factory.view(gviz)
    log = create_non_fitting_eventlog(tree, no, prob)
    for trace in log:
        print("  ", end='')
        for event in trace:
            print(event[xes.DEFAULT_NAME_KEY], end=' ')
        print()
    print_spilt_end()


def pt_to_pn_alignment():
    log = xes_importer.import_log(os.path.join("tests", "input_data", "running-example.xes"))
    tree_template = inductive_miner.apply_tree(log)
    net, initial_marking, final_marking = pt_to_net_with_op.apply_with_operator(tree_template)
    gviz = pn_vis_factory.apply(net)
    pn_vis_factory.view(gviz)
    net, initial_marking, final_marking = pt_to_net.apply(tree_template)
    gviz = pn_vis_factory.apply(net)
    pn_vis_factory.view(gviz)


def align_repair_example1():
    print_spilt_start("align-repair-compare")
    log = xes_importer.import_log(os.path.join("tests", "input_data", "running-example.xes"))
    tree_template = inductive_miner.apply_tree(log)
    gviz1 = pt_vis_factory.apply(tree_template)
    pt_vis_factory.view(gviz1)
    print("Original: ", tree_template)
    # manually operate
    tree_mutated = copy.deepcopy(tree_template)
    xor = tree_mutated.children.pop()
    child1 = xor.children[1]
    child2 = xor.children[0]
    xor.operator = Operator.PARALLEL
    xor.children[0] = child1
    xor.children[1] = child2
    tree_mutated.children.append(xor)
    print("Mutated:  ", tree_mutated)
    same, sub1, sub2 = pt_compare(tree_template, tree_mutated)
    if not same:
        print(" Sub1:", sub1)
        print(" Sub2:", sub2)

    # log_without_reinitialrequest = xes_importer.import_log(os.path.join("tests", "input_data",
    #                                                                     "running-example-wo-reinitial.xes"))
    # tree_mutated = inductive_miner.apply_tree(log_without_reinitialrequest)
    # gviz2 = pt_vis_factory.apply(tree_mutated)
    # pt_vis_factory.view(gviz2)

    net, initial_marking, final_marking = pt_to_net_with_op.apply_with_operator(tree_mutated)
    alignments = align_factory.apply_log(log, net, initial_marking, final_marking,
                                         parameters=pt_to_net_with_op.get_parameters(net))
    # print(alignments.pop(0))

    align_repair = alignment_repair_with_operator(tree_template, tree_mutated, log, parameters=pt_to_net_with_op.get_parameters(net))
    # print(align_repair.pop(0))
    # log_fitness = replay_fitness_factory.evaluate(alignments_pt, variant="alignments")
    # # print(log_fitness)
    print_spilt_end()


def align_repair_example2():
    print_spilt_start("align-repair-compare")
    _, tree_template = randomly_create_new_tree(20)
    print("Original: ", tree_template)
    tree_mutated = randomly_create_mutated_tree(tree_template)
    print("Mutated:  ", tree_mutated)
    same, sub1, sub2 = pt_compare(tree_template, tree_mutated)
    if not same:
        print(" Sub1:", sub1)
        print(" Sub2:", sub2)
    compare_diff_tree(str(tree_template), str(tree_mutated))

    log = create_non_fitting_eventlog(tree_template, 5, 0.1)
    net, initial_marking, final_marking = pt_to_net_with_op.apply_with_operator(tree_mutated)

    alignments = align_factory.apply_log(log, net, initial_marking, final_marking,
                                         parameters=pt_to_net_with_op.get_parameters(net))

    align_repair = alignment_repair_with_operator(tree_template, tree_mutated, log,
                                                  parameters=pt_to_net_with_op.get_parameters(net))
    # log_fitness = replay_fitness_factory.evaluate(alignments_pt, variant="alignments")
    # # print(log_fitness)
    print_spilt_end()


def create_event_log(events):
    trace = Trace()
    for e in list(events):
        event = Event()
        event["concept:name"] = e
        trace.append(event)
    return EventLog([trace])


def align_repair_example3():
    print_spilt_start("align-repair-3")
    tree1 = pt_util.parse("->( a, *( X( d, e), k , τ), i")
    tree2 = pt_util.parse("->( a, *( X( d, c), k, τ), i")
    log = create_event_log("aei")
    net, initial_marking, final_marking = pt_to_net_with_op.apply_with_operator(tree2, {'PARAM_CHILD_LOCK': True})
    # alignments = align_factory.apply_log(log, net, initial_marking, final_marking,
    #                                      parameters=pt_to_net_with_op.get_parameters(net))
    # print(alignments)
    parameters = pt_to_net_with_op.get_parameters(net)
    parameters['PARAM_CHILD_LOCK'] = True
    alignment_repair_with_operator(tree1, tree2, log, parameters=parameters)
    print_spilt_end()


def compare_diff_tree(s_tree1, s_tree2):
    tree1 = pt_util.parse(s_tree1)
    tree2 = pt_util.parse(s_tree2)
    print("Original: ", tree1)
    print("Mutated:  ", tree2)
    same, sub1, sub2 = pt_compare(tree1, tree2)
    if not same:
        print(" Sub1:", sub1)
        print(" Sub2:", sub2)


def random_create(no, node):
    print_spilt_start("create-random-tree")
    for _ in range(no):
        _, tree1 = randomly_create_new_tree(node)
        tree2 = randomly_create_mutated_tree(tree1)
        print("Original: ", tree1)
        print("Mutated:  ", tree2)
        same, sub1, sub2 = pt_compare(tree1, tree2)
        if not same:
            print(" Sub1:", sub1)
            print(" Sub2:", sub2)
    print_spilt_end()


def test_compare_diff_tree_example():
    print_spilt_start("Hard-Example")
    # compare_diff_tree('->( a, *( *( b, c, τ ), X( *( ->( d, e ), X( f, g ), τ ), +( h, i ) ), τ ) )',
    #                   '->( a, *( *( b, c, τ ), X( *( e, X( f, g ), τ ), +( h, i ) ), τ ) )')
    # compare_diff_tree("->( a, b, c, X( +( X( i, *( j, k, τ ) ), h ), +( ->( X( f, g ), e ), d ) ) )",
    #                   "->( a, b, c, X( +( ->( i, *( j, k, τ ) ), h ), +( ->( X( f, g ), e ), d ) ) )")
    # compare_diff_tree("+( X( ->( *( a, *( ->( h, i ), d, τ ), τ ), j, k ), b, c ), X( f, g, e ) )",
    #                   "+( X( ->( *( a, *( ->( h, i ), X( d, n ), τ ), τ ), j, k ), b, c ), X( f, g, e ) )")
    # compare_diff_tree("+( X( *( e, X( f, g ), τ ), +( h, i ) ), X( *( b, *( c, d, τ ), τ ), a ) )",
    #                   "+( X( *( e, X( f, g ), τ ), +( h, i ) ), X( *( b, X( *( c, d, τ ), m ), τ ), a ) )")
    # compare_diff_tree("+( ->( a, X( ->( *( d, e, τ ), c ), f, g ) ), ->( +( b, ->( j, k ) ), h, i ) )",
    #                   "+( ->( a, X( ->( *( d, X( e, m ), τ ), c ), f, g ) ), ->( +( b, ->( j, k ) ), h, i ) )")
    compare_diff_tree(" +( ->( X( ->( f, g ), a ), j, k ), X( +( X( d, e ), ->( h, i ) ), +( b, c ) ) )",
                      "+( +( X( ->( f, g ), a ), j, k ), X( +( X( d, e ), ->( h, i ) ), +( b, c ) ) )")
    print_spilt_end()


def test_scope_expand_example1():
    # tree1 = pt_util.parse("->( a, *( X(c, b), d, τ), e)")
    # net, initial_marking, final_marking = pt_to_net.apply(tree1)
    # log = create_event_log("abfce")
    # alignments = align_factory.apply_log(log, net, initial_marking, final_marking)
    # print(alignments)

    print_spilt_start("Scope-Expand")
    tree1 = pt_util.parse("->( a, *( X(c, b), d, τ), e)")
    tree2 = pt_util.parse("->( a, * (->(c, b), d, τ), e)")
    log = create_event_log("abfce")
    pt_number.dfs_number(tree1)
    pt_number.dfs_number(tree2)

    # net, initial_marking, final_marking = pt_to_net_with_op.apply_with_operator(tree1, {'PARAM_CHILD_LOCK': True})
    # gviz = pn_vis_factory.apply(net)
    # pn_vis_factory.view(gviz)
    # alignments = align_factory.apply_log(log, net, initial_marking, final_marking,
    #                                      parameters=pt_to_net_with_op.get_parameters(net))
    # print(alignments)
    # parameters = pt_to_net_with_op.get_parameters(net)
    # parameters['PARAM_CHILD_LOCK'] = True
    # alignment_repair_with_operator(tree1, tree2, log, parameters=parameters)
    s_align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                             (('t_a_0', 'a'), ('a', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                             (('>>', '3_s'), ('>>', '3_s')), (('>>', '4_s'), ('>>', '4_s')),  (('>>', '5_s'), ('>>', '5_s')),
                             (('t_c_3', 'c'), ('c', 'c')),   (('>>', '5_e'), ('>>', '5_e')), (('>>', '4_e'), ('>>', '4_e')),
                             (('>>', '7_s'), ('>>', '7_s')), (('t_d_1', '>>'), ('>>', 'd')),   (('>>', '7_e'), ('>>', '7_e')),
                             (('>>', '4_s'), ('>>', '4_s')), (('>>', '6_s'), ('>>', '6_s')),
                             (('t_b_3', 'b'), ('b', 'b')), (('>>', '6_e'), ('>>', '6_e')),
                             (('>>', '4_e'), ('>>', '4_e')),
                             (('>>', '8_s'), ('>>', '8_s')), (('>>', '8_skip_1'), ('>>', None)),
                             (('>>', '8_e'), ('>>', '8_e')),  (('t_k_2', '>>'), ('k', '>>')), (('>>', '3_e'), ('>>', '3_e')),
                             (('>>', '9_s'), ('>>', '9_s')), (('t_e_4', 'e'), ('e', 'e')),
                             (('>>', '9_e'), ('>>', '9_e')), (('>>', '1_e'), ('>>', '1_e'))],
               'cost': 20015, 'visited_states': 30, 'queued_states': 52, 'traversed_arcs': 52, 'fitness': 0.9090909}]
    print(s_align)
    _, sub1, _ = pt_compare(tree1, tree2)
    scope_expand(s_align, sub1, True)
    print(s_align)
    print_spilt_end()

    a = {'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')), (('t_a_0', 'a'), ('a', 'a')),
                   (('>>', '2_e'), ('>>', '2_e')), (('>>', '3_s'), ('>>', '3_s')), (('>>', '4_s'), ('>>', '4_s')),
                   (('>>', '5_s'), ('>>', '5_s')), (('t_c_3', 'c'), ('c', 'c')), (('>>', '4_e'), ('>>', '4_e')),
                   (('>>', '7_s'), ('>>', '7_s')), (('t_d_1', '>>'), ('>>', 'd')), (('>>', '7_e'), ('>>', '7_e')),
                   (('>>', '4_s'), ('>>', '4_s')), (('>>', '5_e'), ('>>', '5_e')), (('t_k_2', '>>'), ('k', '>>')),
                   (('>>', '6_s'), ('>>', '6_s')), (('t_b_3', 'b'), ('b', 'b')), (('>>', '4_e'), ('>>', '4_e')),
                   (('>>', '6_e'), ('>>', '6_e')), (('>>', '8_s'), ('>>', '8_s')), (('>>', '8_skip_1'), ('>>', None)),
                   (('>>', '8_e'), ('>>', '8_e')), (('t_k_2', '>>'), ('k', '>>')), (('>>', '3_e'), ('>>', '3_e')),
                   (('>>', '9_s'), ('>>', '9_s')), (('t_e_4', 'e'), ('e', 'e')), (('>>', '9_e'), ('>>', '9_e')),
                   (('>>', '1_e'), ('>>', '1_e'))], 'cost': 20015, 'visited_states': 30, 'queued_states': 52,
     'traversed_arcs': 52, 'fitness': 0.9090909}


def test_scope_expand_example():
    print_spilt_start("Scope-Expand")
    tree1 = pt_util.parse("->( +( ->( c, *( +( g, h ), d, τ ) ), X( a, b ) ), *( e, f, τ ) )")
    tree2 = pt_util.parse("->( +( ->( c, *( +( g, h ), d, τ ) ), X( a, b ) ), *( e, f, τ ), k )")
    log = create_event_log("chekekfefkek")

    pt_number.dfs_number(tree1)
    pt_number.dfs_number(tree2)

    net, initial_marking, final_marking = pt_to_net_with_op.apply_with_operator(tree1, {'PARAM_CHILD_LOCK': True})
    parameters = pt_to_net_with_op.get_parameters(net)
    parameters['PARAM_CHILD_LOCK'] = True
    # gviz = pn_vis_factory.apply(net)
    # pn_vis_factory.view(gviz)
    alignments = align_factory.apply_log(log, net, initial_marking, final_marking,
                                         parameters=pt_to_net_with_op.get_parameters(net))
    # print(alignments)
    # parameters = pt_to_net_with_op.get_parameters(net)
    # parameters['PARAM_CHILD_LOCK'] = True
    # alignment_repair_with_operator(tree1, tree2, log, parameters=parameters)
    # alignment_repair_with_operator(tree1, tree2, log,
    #                                parameters=pt_to_net_with_op.get_parameters(net))
    s_align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')), (('>>', '2_tau_1'), ('>>', None)),
                   (('>>', '6_s'), ('>>', '6_s')), (('>>', '3_s'), ('>>', '3_s')), (('>>', '5_s'), ('>>', '5_s')),
                  (('t_c_1', 'c'), ('c', 'c')), (('>>', '5_e'), ('>>', '5_e')),
                   (('>>', '3_e'), ('>>', '3_e')), (('t_d_2', 'd'), ('d', 'd')), (('>>', '6_e'), ('>>', '6_e')),
                   (('>>', '2_tau_2'), ('>>', None)), (('>>', '2_e'), ('>>', '2_e')),  (('t_b_0', '>>'), ('b', '>>')), (('>>', '7_s'), ('>>', '7_s')),
                   (('t_a_3', 'a'), ('>>', 'a')), (('>>', '7_e'), ('>>', '7_e')), (('>>', '1_e'), ('>>', '1_e'))],
     'cost': 10014, 'visited_states': 25, 'queued_states': 51, 'traversed_arcs': 51, 'fitness': 0.9473684210526316}]
    print(s_align)
    _, sub1, _ = pt_compare(tree1, tree2)
    scope_expand(s_align, sub1, True)
    print(s_align)
    print_spilt_end()


def evaluation():
    print_spilt_start("Compare_Runtime")
    # compare_run_time(20)
    alignment_quality()
    print_spilt_end()


# pt_to_pn_alignment()
# random_create(20, 20)
# non_fit_eventlog(20, 2, 0.1)
# align_repair_example1()
# align_repair_example2()
# align_repair_example3()
# test_compare_diff_tree_example()
# test_scope_expand_example()
# test_right_scope_expand_example()
evaluation()

