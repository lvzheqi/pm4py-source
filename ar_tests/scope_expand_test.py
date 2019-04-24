import unittest
import random

from pm4py.objects.process_tree import util as pt_util

from align_repair.repair.general_scope_expand import general_scope_expand
from align_repair.repair.scope_expand import scope_expand
from align_repair.pt_manipulate import pt_number
from align_repair.evaluation import create_event_log, alignment_on_lock_pt
from align_repair.stochastic_generation.stochastic_mutated_pt import randomly_create_mutated_tree
from align_repair.stochastic_generation.stochastic_pt_generation import randomly_create_new_tree
from align_repair.repair.align_repair import alignment_repair_with_operator_align
from align_repair.stochastic_generation.non_fitting_eventlog_generation import create_non_fitting_eventlog

class ScopeExpandTest(unittest.TestCase):
    def test_scope_expand1(self):
        tree1 = pt_util.parse("->( a, *( X(c, b), d, τ), e)")
        tree2 = pt_util.parse("->( a, *(->(c, b), d, τ), e)")
        # log = create_event_log("abdce")
        pt_number.pt_number(tree1, 'D', 1)
        pt_number.pt_number(tree2, 'D', 1)
        align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                                (('t_a_0', 'a'), ('a', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                                (('>>', '3_s'), ('>>', '3_s')), (('>>', '4_s'), ('>>', '4_s')),
                                (('>>', '6_s'), ('>>', '6_s')), (('t_b_1', 'b'), ('b', 'b')),
                                (('>>', '6_e'), ('>>', '6_e')), (('>>', '4_e'), ('>>', '4_e')),
                                (('>>', '7_s'), ('>>', '7_s')), (('t_d_2', 'd'), ('d', 'd')),
                                (('>>', '7_e'), ('>>', '7_e')), (('>>', '4_s'), ('>>', '4_s')),
                                (('>>', '5_s'), ('>>', '5_s')), (('t_c_3', 'c'), ('c', 'c')),
                                (('>>', '5_e'), ('>>', '5_e')), (('>>', '4_e'), ('>>', '4_e')),
                                (('>>', '8_s'), ('>>', '8_s')), (('>>', '8_skip_1'), ('>>', None)),
                                (('>>', '8_e'), ('>>', '8_e')), (('>>', '3_e'), ('>>', '3_e')),
                                (('>>', '9_s'), ('>>', '9_s')), (('t_e_4', 'e'), ('e', 'e')),
                                (('>>', '9_e'), ('>>', '9_e')), (('>>', '1_e'), ('>>', '1_e'))],
                  'cost': 0, 'visited_states': 33, 'queued_states': 71, 'traversed_arcs': 71, 'fitness': 1}]

        s_align = scope_expand(align, tree1, tree2)
        g_s_align = general_scope_expand(align, tree1, tree2)
        e_s_align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                                    (('t_a_0', 'a'), ('a', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                                    (('>>', '3_s'), ('>>', '3_s')), (('>>', '4_s'), ('>>', '4_s')),
                                    (('>>', '6_s'), ('>>', '6_s')), (('t_b_1', 'b'), ('b', 'b')),
                                    (('>>', '6_e'), ('>>', '6_e')), (('>>', '4_e'), ('>>', '4_e')),
                                    (('>>', '7_s'), ('>>', '7_s')), (('t_d_2', 'd'), ('d', 'd')),
                                    (('>>', '7_e'), ('>>', '7_e')), (('>>', '4_s'), ('>>', '4_s')),
                                    (('>>', '5_s'), ('>>', '5_s')), (('t_c_3', 'c'), ('c', 'c')),
                                    (('>>', '5_e'), ('>>', '5_e')), (('>>', '4_e'), ('>>', '4_e')),
                                    (('>>', '8_s'), ('>>', '8_s')), (('>>', '8_skip_1'), ('>>', None)),
                                    (('>>', '8_e'), ('>>', '8_e')), (('>>', '3_e'), ('>>', '3_e')),
                                    (('>>', '9_s'), ('>>', '9_s')), (('t_e_4', 'e'), ('e', 'e')),
                                    (('>>', '9_e'), ('>>', '9_e')), (('>>', '1_e'), ('>>', '1_e'))],
                     'cost': 0, 'visited_states': 33, 'queued_states': 71, 'traversed_arcs': 71, 'fitness': 1}]
        self.assertEqual(str(s_align), str(e_s_align))
        self.assertEqual(str(g_s_align), str(e_s_align))

    def test_scope_expand2(self):
        tree1 = pt_util.parse("+( a, ->(b, c))")
        tree2 = pt_util.parse("+( a, X(b, c))")
        # log = create_event_log("bac")
        pt_number.pt_number(tree1, 'D', 1)
        pt_number.pt_number(tree2, 'D', 1)
        align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '1_tau_1'), ('>>', None)),
                                (('>>', '3_s'), ('>>', '3_s')), (('>>', '2_s'), ('>>', '2_s')),
                                (('>>', '4_s'), ('>>', '4_s')), (('t_b_0', 'b'), ('b', 'b')),
                                (('>>', '4_e'), ('>>', '4_e')), (('>>', '5_s'), ('>>', '5_s')),
                                (('t_a_1', 'a'), ('a', 'a')), (('t_c_2', 'c'), ('c', 'c')),
                                (('>>', '5_e'), ('>>', '5_e')), (('>>', '2_e'), ('>>', '2_e')),
                                (('>>', '3_e'), ('>>', '3_e')), (('>>', '1_tau_2'), ('>>', None)),
                                (('>>', '1_e'), ('>>', '1_e'))], 'cost': 0, 'visited_states': 24,
                  'queued_states': 57, 'traversed_arcs': 64, 'fitness': 1}]

        s_align = scope_expand(align, tree1, tree2)
        g_s_align = general_scope_expand(align, tree1, tree2)
        e_s_align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '3_s'), ('>>', '3_s')),
                                    (('>>', '1_tau_1'), ('>>', None)), (('>>', '2_s'), ('>>', '2_s')),
                                    (('>>', '4_s'), ('>>', '4_s')), (('t_b_0', 'b'), ('b', 'b')),
                                    (('>>', '4_e'), ('>>', '4_e')), (('>>', '5_s'), ('>>', '5_s')),
                                    (('t_a_1', 'a'), ('a', 'a')), (('t_c_2', 'c'), ('c', 'c')),
                                    (('>>', '5_e'), ('>>', '5_e')), (('>>', '2_e'), ('>>', '2_e')),
                                    (('>>', '1_tau_2'), ('>>', None)), (('>>', '3_e'), ('>>', '3_e')),
                                    (('>>', '1_e'), ('>>', '1_e'))], 'cost': 0, 'visited_states': 24,
                     'queued_states': 57, 'traversed_arcs': 64, 'fitness': 1}]

        self.assertEqual(str(s_align), str(e_s_align))
        self.assertEqual(str(g_s_align), str(e_s_align))

    def test_scope_expand3(self):
        tree1 = pt_util.parse("X( a, ->(b, c))")
        tree2 = pt_util.parse("X( a, +(b, c))")
        # log = create_event_log("ebf")
        pt_number.pt_number(tree1, 'D', 1)
        pt_number.pt_number(tree2, 'D', 1)
        align = [{'alignment': [(('t_e_0', '>>'), ('e', '>>')), (('>>', '1_s'), ('>>', '1_s')),
                                (('>>', '3_s'), ('>>', '3_s')), (('>>', '4_s'), ('>>', '4_s')),
                                (('t_b_1', 'b'), ('b', 'b')), (('>>', '4_e'), ('>>', '4_e')),
                                (('>>', '5_s'), ('>>', '5_s')), (('>>', 'c'), ('>>', 'c')),
                                (('>>', '5_e'), ('>>', '5_e')), (('>>', '3_e'), ('>>', '3_e')),
                                (('>>', '1_e'), ('>>', '1_e')), (('t_f_2', '>>'), ('f', '>>'))],
                  'cost': 12, 'visited_states': 22, 'queued_states': 27, 'traversed_arcs': 27,
                  'fitness': 0.2941176470588235}]

        s_align = scope_expand(align, tree1, tree2)
        g_s_align = general_scope_expand(align, tree1, tree2)
        e_s_align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '3_s'), ('>>', '3_s')),
                                    (('t_e_0', '>>'), ('e', '>>')), (('>>', '4_s'), ('>>', '4_s')),
                                    (('t_b_1', 'b'), ('b', 'b')), (('>>', '4_e'), ('>>', '4_e')),
                                    (('>>', '5_s'), ('>>', '5_s')), (('>>', 'c'), ('>>', 'c')),
                                    (('>>', '5_e'), ('>>', '5_e')), (('t_f_2', '>>'), ('f', '>>')),
                                    (('>>', '3_e'), ('>>', '3_e')), (('>>', '1_e'), ('>>', '1_e'))],
                      'cost': 12, 'visited_states': 22, 'queued_states': 27,
                      'traversed_arcs': 27, 'fitness': 0.2941176470588235}]

        self.assertEqual(str(s_align), str(e_s_align))
        self.assertEqual(str(g_s_align), str(e_s_align))

    def test_scope_expand4(self):
        tree1 = pt_util.parse("*( a, X(b, c), τ)")
        tree2 = pt_util.parse("*( a, ->(b, c), τ)")
        # log = create_event_log("abeaf")
        pt_number.pt_number(tree1, 'D', 1)
        pt_number.pt_number(tree2, 'D', 1)
        align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                                (('t_a_0', 'a'), ('a', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                                (('>>', '3_s'), ('>>', '3_s')), (('>>', '4_s'), ('>>', '4_s')),
                                (('t_b_1', 'b'), ('b', 'b')), (('>>', '4_e'), ('>>', '4_e')),
                                (('>>', '3_e'), ('>>', '3_e')), (('>>', '2_s'), ('>>', '2_s')),
                                (('t_e_2', '>>'), ('e', '>>')), (('t_a_3', 'a'), ('a', 'a')),
                                (('>>', '2_e'), ('>>', '2_e')), (('>>', '6_s'), ('>>', '6_s')),
                                (('>>', '6_skip_1'), ('>>', None)), (('>>', '6_e'), ('>>', '6_e')),
                                (('>>', '1_e'), ('>>', '1_e')), (('t_f_4', '>>'), ('f', '>>'))],
                  'cost': 10, 'visited_states': 31, 'queued_states': 50, 'traversed_arcs': 50,
                  'fitness': 0.6296296296296297}]

        s_align = scope_expand(align, tree1, tree2)
        g_s_align = general_scope_expand(align, tree1, tree2)
        e_s_align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                                    (('t_a_0', 'a'), ('a', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                                    (('>>', '3_s'), ('>>', '3_s')), (('>>', '4_s'), ('>>', '4_s')),
                                    (('t_b_1', 'b'), ('b', 'b')), (('>>', '4_e'), ('>>', '4_e')),
                                    (('t_e_2', '>>'), ('e', '>>')), (('>>', '3_e'), ('>>', '3_e')),
                                    (('>>', '2_s'), ('>>', '2_s')), (('t_a_3', 'a'), ('a', 'a')),
                                    (('>>', '2_e'), ('>>', '2_e')),  (('>>', '6_s'), ('>>', '6_s')),
                                    (('>>', '6_skip_1'), ('>>', None)), (('>>', '6_e'), ('>>', '6_e')),
                                    (('>>', '1_e'), ('>>', '1_e')),  (('t_f_4', '>>'), ('f', '>>'))],
                      'cost': 10, 'visited_states': 31, 'queued_states': 50, 'traversed_arcs': 50,
                      'fitness': 0.6296296296296297}]
        e_g_s_align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                                      (('t_a_0', 'a'), ('a', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                                      (('>>', '3_s'), ('>>', '3_s')), (('>>', '4_s'), ('>>', '4_s')),
                                      (('t_b_1', 'b'), ('b', 'b')), (('>>', '4_e'), ('>>', '4_e')),
                                      (('t_e_2', '>>'), ('e', '>>')), (('>>', '3_e'), ('>>', '3_e')),
                                      (('>>', '2_s'), ('>>', '2_s')), (('t_a_3', 'a'), ('a', 'a')),
                                      (('t_f_4', '>>'), ('f', '>>')), (('>>', '2_e'), ('>>', '2_e')),
                                      (('>>', '6_s'), ('>>', '6_s')),
                                      (('>>', '6_skip_1'), ('>>', None)), (('>>', '6_e'), ('>>', '6_e')),
                                      (('>>', '1_e'), ('>>', '1_e'))],
                        'cost': 10, 'visited_states': 31, 'queued_states': 50, 'traversed_arcs': 50,
                        'fitness': 0.6296296296296297}]
        self.assertEqual(str(s_align), str(e_s_align))
        self.assertEqual(str(g_s_align), str(e_g_s_align))

    def test_two_scope_cost(self):
        for _ in range(100):
            tree1 = randomly_create_new_tree(random.randint(5, 15))
            tree2 = randomly_create_mutated_tree(tree1)
            log = create_non_fitting_eventlog(tree2, 1, 0.8)
            pt_number.pt_number(tree1, 'D', 1)
            pt_number.pt_number(tree2, 'D', 1)
            align = alignment_on_lock_pt(tree1, log)
            s_align = scope_expand(align, tree1, tree2)
            g_s_align = general_scope_expand(align, tree1, tree2)
            ar1 = alignment_repair_with_operator_align(tree1, tree2, log, s_align)
            ar2 = alignment_repair_with_operator_align(tree1, tree2, log, g_s_align)
            self.assertEqual(ar1[0]['cost'], ar2[0]['cost'])


if __name__ == "__main__":
    unittest.main()
