import unittest
import random

from pm4py.objects.process_tree import util as pt_utils

from align_repair.repair.lock_pt import align_repair, general_scope_expand, scope_expand
from align_repair.process_tree.manipulation import pt_number
from align_repair.process_tree.stochastic_generation import stochastic_pt_create as pt_create
from align_repair.process_tree.stochastic_generation import non_fitting_log_create as log_create
from align_repair.process_tree.stochastic_generation import stochastic_pt_mutate as pt_mutate
from align_repair.process_tree.alignments import to_lock_align

from ar_tests import utils


class LockScopeExpandTest(unittest.TestCase):

    def setUp(self):
        self.parameters = {'ret_tuple_as_trans_desc': True, 'PARAM_CHILD_LOCK': True}
        self.parameters_tuple_false = {'ret_tuple_as_trans_desc': False, 'PARAM_LOOP_LOCK': True}

    def test_scope_expand1(self):
        tree1 = pt_utils.parse("->( a, *( X(c, b), d, τ), e)")
        tree2 = pt_utils.parse("->( a, *(->(c, b), d, τ), e)")
        # log = create_event_log("abdce")
        pt_number.apply(tree1, 'D', 1)
        pt_number.apply(tree2, 'D', 1)
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

        s_align = scope_expand.apply(align, tree1, tree2, self.parameters)
        g_s_align = general_scope_expand.apply(align, tree1, tree2, self.parameters)
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

        l_align = [{'alignment': [('>>', '1_s'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '3_s'), ('>>', '4_s'),
                                  ('>>', '6_s'), ('b', 'b'), ('>>', '6_e'), ('>>', '4_e'), ('>>', '7_s'), ('d', 'd'),
                                  ('>>', '7_e'), ('>>', '4_s'), ('>>', '5_s'), ('c', 'c'), ('>>', '5_e'), ('>>', '4_e'),
                                  ('>>', '8_s'), ('>>', None), ('>>', '8_e'), ('>>', '3_e'), ('>>', '9_s'), ('e', 'e'),
                                  ('>>', '9_e'), ('>>', '1_e')], 'cost': 0, 'visited_states': 18, 'queued_states': 41,
                    'traversed_arcs': 43, 'fitness': 1}]
        s_l_align = scope_expand.apply(l_align, tree1, tree2, self.parameters_tuple_false)
        e_s_l_align = [{'alignment': [('>>', '1_s'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '3_s'),
                                      ('>>', '4_s'), ('>>', '6_s'), ('b', 'b'), ('>>', '6_e'), ('>>', '4_e'),
                                      ('>>', '7_s'), ('d', 'd'), ('>>', '7_e'), ('>>', '4_s'), ('>>', '5_s'),
                                      ('c', 'c'), ('>>', '5_e'), ('>>', '4_e'), ('>>', '8_s'), ('>>', None),
                                      ('>>', '8_e'), ('>>', '3_e'), ('>>', '9_s'), ('e', 'e'), ('>>', '9_e'),
                                      ('>>', '1_e')], 'cost': 0, 'visited_states': 18, 'queued_states': 41,
                        'traversed_arcs': 43, 'fitness': 1}]

        self.assertEqual(str(s_l_align), str(e_s_l_align))
        self.assertEqual(str(s_align), str(e_s_align))
        self.assertEqual(str(g_s_align), str(e_s_align))

    def test_scope_expand2(self):
        tree1 = pt_utils.parse("+( a, ->(b, c))")
        tree2 = pt_utils.parse("+( a, X(b, c))")
        # log = create_event_log("bac")
        pt_number.apply(tree1, 'D', 1)
        pt_number.apply(tree2, 'D', 1)
        align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '1_tau_1'), ('>>', None)),
                                (('>>', '3_s'), ('>>', '3_s')), (('>>', '2_s'), ('>>', '2_s')),
                                (('>>', '4_s'), ('>>', '4_s')), (('t_b_0', 'b'), ('b', 'b')),
                                (('>>', '4_e'), ('>>', '4_e')), (('>>', '5_s'), ('>>', '5_s')),
                                (('t_a_1', 'a'), ('a', 'a')), (('t_c_2', 'c'), ('c', 'c')),
                                (('>>', '5_e'), ('>>', '5_e')), (('>>', '2_e'), ('>>', '2_e')),
                                (('>>', '3_e'), ('>>', '3_e')), (('>>', '1_tau_2'), ('>>', None)),
                                (('>>', '1_e'), ('>>', '1_e'))], 'cost': 0, 'visited_states': 24,
                  'queued_states': 57, 'traversed_arcs': 64, 'fitness': 1}]

        s_align = scope_expand.apply(align, tree1, tree2, self.parameters)
        g_s_align = general_scope_expand.apply(align, tree1, tree2, self.parameters)
        e_s_align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '3_s'), ('>>', '3_s')),
                                    (('>>', '1_tau_1'), ('>>', None)), (('>>', '2_s'), ('>>', '2_s')),
                                    (('>>', '4_s'), ('>>', '4_s')), (('t_b_0', 'b'), ('b', 'b')),
                                    (('>>', '4_e'), ('>>', '4_e')), (('>>', '5_s'), ('>>', '5_s')),
                                    (('t_a_1', 'a'), ('a', 'a')), (('t_c_2', 'c'), ('c', 'c')),
                                    (('>>', '5_e'), ('>>', '5_e')), (('>>', '2_e'), ('>>', '2_e')),
                                    (('>>', '1_tau_2'), ('>>', None)), (('>>', '3_e'), ('>>', '3_e')),
                                    (('>>', '1_e'), ('>>', '1_e'))], 'cost': 0, 'visited_states': 24,
                      'queued_states': 57, 'traversed_arcs': 64, 'fitness': 1}]

        l_align = [{'alignment': [('>>', '1_s'), ('>>', None), ('>>', '3_s'), ('>>', '4_s'), ('b', 'b'), ('>>', '4_e'),
                                  ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '5_s'), ('c', 'c'), ('>>', '5_e'),
                                  ('>>', '3_e'), ('>>', None), ('>>', '1_e')], 'cost': 0, 'visited_states': 6,
                    'queued_states': 14, 'traversed_arcs': 14, 'fitness': 1}]
        s_l_align = scope_expand.apply(l_align, tree1, tree2, self.parameters_tuple_false)
        e_s_l_align = [{'alignment': [('>>', '1_s'), ('>>', '3_s'), ('>>', None), ('>>', '4_s'), ('b', 'b'),
                                      ('>>', '4_e'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '5_s'),
                                      ('c', 'c'), ('>>', '5_e'), ('>>', None), ('>>', '3_e'), ('>>', '1_e')], 'cost': 0,
                        'visited_states': 6, 'queued_states': 14, 'traversed_arcs': 14, 'fitness': 1}]

        self.assertEqual(str(s_l_align), str(e_s_l_align))
        self.assertEqual(str(s_align), str(e_s_align))
        self.assertEqual(str(g_s_align), str(e_s_align))

    def test_scope_expand3(self):
        tree1 = pt_utils.parse("X( a, ->(b, c))")
        tree2 = pt_utils.parse("X( a, +(b, c))")
        # log = create_event_log("ebf")
        pt_number.apply(tree1, 'D', 1)
        pt_number.apply(tree2, 'D', 1)
        align = [{'alignment': [(('t_e_0', '>>'), ('e', '>>')), (('>>', '1_s'), ('>>', '1_s')),
                                (('>>', '3_s'), ('>>', '3_s')), (('>>', '4_s'), ('>>', '4_s')),
                                (('t_b_1', 'b'), ('b', 'b')), (('>>', '4_e'), ('>>', '4_e')),
                                (('>>', '5_s'), ('>>', '5_s')), (('>>', 'c'), ('>>', 'c')),
                                (('>>', '5_e'), ('>>', '5_e')), (('>>', '3_e'), ('>>', '3_e')),
                                (('>>', '1_e'), ('>>', '1_e')), (('t_f_2', '>>'), ('f', '>>'))],
                  'cost': 12, 'visited_states': 22, 'queued_states': 27, 'traversed_arcs': 27,
                  'fitness': 0.2941176470588235}]

        s_align = scope_expand.apply(align, tree1, tree2, self.parameters)
        g_s_align = general_scope_expand.apply(align, tree1, tree2, self.parameters)
        e_s_align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '3_s'), ('>>', '3_s')),
                                    (('t_e_0', '>>'), ('e', '>>')), (('>>', '4_s'), ('>>', '4_s')),
                                    (('t_b_1', 'b'), ('b', 'b')), (('>>', '4_e'), ('>>', '4_e')),
                                    (('>>', '5_s'), ('>>', '5_s')), (('>>', 'c'), ('>>', 'c')),
                                    (('>>', '5_e'), ('>>', '5_e')), (('t_f_2', '>>'), ('f', '>>')),
                                    (('>>', '3_e'), ('>>', '3_e')), (('>>', '1_e'), ('>>', '1_e'))],
                      'cost': 12, 'visited_states': 22, 'queued_states': 27,
                      'traversed_arcs': 27, 'fitness': 0.2941176470588235}]

        l_align = [{'alignment': [('>>', '1_s'), ('e', '>>'), ('>>', '3_s'), ('>>', '4_s'), ('b', 'b'), ('>>', '4_e'),
                                  ('>>', '5_s'), ('>>', 'c'), ('>>', '5_e'), ('>>', '3_e'), ('f', '>>'), ('>>', '1_e')],
                    'cost': 12, 'visited_states': 6, 'queued_states': 8, 'traversed_arcs': 8,
                    'fitness': 0.2941176470588235}]
        s_l_align = scope_expand.apply(l_align, tree1, tree2, self.parameters_tuple_false)
        e_s_l_align = [
            {'alignment': [('>>', '1_s'), ('>>', '3_s'), ('e', '>>'), ('>>', '4_s'), ('b', 'b'), ('>>', '4_e'),
                           ('>>', '5_s'), ('>>', 'c'), ('>>', '5_e'), ('f', '>>'), ('>>', '3_e'),
                           ('>>', '1_e')], 'cost': 12, 'visited_states': 6, 'queued_states': 8,
             'traversed_arcs': 8, 'fitness': 0.2941176470588235}]

        self.assertEqual(str(s_l_align), str(e_s_l_align))
        self.assertEqual(str(s_align), str(e_s_align))
        self.assertEqual(str(g_s_align), str(e_s_align))

    def test_scope_expand4(self):
        tree1 = pt_utils.parse("*( a, X(b, c), τ)")
        tree2 = pt_utils.parse("*( a, ->(b, c), τ)")
        # log = create_event_log("abeaf")
        pt_number.apply(tree1, 'D', 1)
        pt_number.apply(tree2, 'D', 1)
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

        s_align = scope_expand.apply(align, tree1, tree2, self.parameters)
        g_s_align = general_scope_expand.apply(align, tree1, tree2, self.parameters)
        e_s_align = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                                    (('t_a_0', 'a'), ('a', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                                    (('>>', '3_s'), ('>>', '3_s')), (('>>', '4_s'), ('>>', '4_s')),
                                    (('t_b_1', 'b'), ('b', 'b')), (('>>', '4_e'), ('>>', '4_e')),
                                    (('t_e_2', '>>'), ('e', '>>')), (('>>', '3_e'), ('>>', '3_e')),
                                    (('>>', '2_s'), ('>>', '2_s')), (('t_a_3', 'a'), ('a', 'a')),
                                    (('>>', '2_e'), ('>>', '2_e')), (('>>', '6_s'), ('>>', '6_s')),
                                    (('>>', '6_skip_1'), ('>>', None)), (('>>', '6_e'), ('>>', '6_e')),
                                    (('>>', '1_e'), ('>>', '1_e')), (('t_f_4', '>>'), ('f', '>>'))],
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

        l_align = [{'alignment': [('>>', '1_s'), ('>>', None), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '3_s'),
                                  ('>>', '4_s'), ('b', 'b'), ('>>', '4_e'), ('>>', '3_e'), ('>>', '2_s'), ('e', '>>'),
                                  ('a', 'a'), ('>>', '2_e'), ('>>', '6_s'), ('>>', None), ('>>', '6_e'), ('f', '>>'),
                                  ('>>', '1_e')], 'cost': 10, 'visited_states': 24, 'queued_states': 39,
                    'traversed_arcs': 40, 'fitness': 0.6296296296296297}]
        s_l_align = scope_expand.apply(l_align, tree1, tree2, self.parameters_tuple_false)
        e_s_l_align = [{'alignment': [('>>', '1_s'), ('>>', None), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'),
                                      ('>>', '3_s'), ('>>', '4_s'), ('b', 'b'), ('>>', '4_e'), ('e', '>>'),
                                      ('>>', '3_e'),
                                      ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '6_s'), ('>>', None),
                                      ('>>', '6_e'), ('f', '>>'), ('>>', '1_e')], 'cost': 10, 'visited_states': 24,
                        'queued_states': 39, 'traversed_arcs': 40, 'fitness': 0.6296296296296297}]

        self.assertEqual(str(s_l_align), str(e_s_l_align))
        self.assertEqual(str(s_align), str(e_s_align))
        self.assertEqual(str(g_s_align), str(e_g_s_align))

    def test_two_scope_cost(self):
        for _ in range(10):
            tree1 = pt_create.apply(random.randint(5, 15))
            tree2 = pt_mutate.apply(tree1)
            log = log_create.apply(tree2, 1, 0.8)
            pt_number.apply(tree1, 'D', 1)
            pt_number.apply(tree2, 'D', 1)
            align = utils.alignment_on_lock_pt(tree1, log)
            s_align = scope_expand.apply(align, tree1, tree2, self.parameters)
            g_s_align = general_scope_expand.apply(align, tree1, tree2, self.parameters)
            ar1 = align_repair.apply(tree1, tree2, log, s_align, self.parameters)
            ar2 = align_repair.apply(tree1, tree2, log, g_s_align, self.parameters)
            self.assertEqual(ar1[0]['cost'], ar2[0]['cost'])

    def test_scope_expand_tuple_false1(self):
        tree1 = pt_utils.parse("->( a, *( X(c, b), d, τ), e)")
        tree2 = pt_utils.parse("->( a, *(->(c, b), d, τ), e)")
        log = utils.create_event_log("abdce")
        pt_number.apply(tree1, 'D', 1)
        pt_number.apply(tree2, 'D', 1)
        alignments = utils.alignment_on_loop_lock_pt(tree1, log)
        to_lock_align.apply(tree1, alignments)
        l_align = [{'alignment': [('>>', '1_s'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '3_s'), ('>>', '4_s'),
                                  ('>>', '6_s'), ('b', 'b'), ('>>', '6_e'), ('>>', '4_e'), ('>>', '7_s'), ('d', 'd'),
                                  ('>>', '7_e'), ('>>', '4_s'), ('>>', '5_s'), ('c', 'c'), ('>>', '5_e'), ('>>', '4_e'),
                                  ('>>', '8_s'), ('>>', None), ('>>', '8_e'), ('>>', '3_e'), ('>>', '9_s'), ('e', 'e'),
                                  ('>>', '9_e'), ('>>', '1_e')], 'cost': 0, 'visited_states': 18, 'queued_states': 41,
                    'traversed_arcs': 43, 'fitness': 1}]
        s_l_align = scope_expand.apply(l_align, tree1, tree2, self.parameters_tuple_false)
        e_s_l_align = [{'alignment': [('>>', '1_s'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '3_s'),
                                      ('>>', '4_s'), ('>>', '6_s'), ('b', 'b'), ('>>', '6_e'), ('>>', '4_e'),
                                      ('>>', '7_s'), ('d', 'd'), ('>>', '7_e'), ('>>', '4_s'), ('>>', '5_s'),
                                      ('c', 'c'), ('>>', '5_e'), ('>>', '4_e'), ('>>', '8_s'), ('>>', None),
                                      ('>>', '8_e'), ('>>', '3_e'), ('>>', '9_s'), ('e', 'e'), ('>>', '9_e'),
                                      ('>>', '1_e')], 'cost': 0, 'visited_states': 18, 'queued_states': 41,
                        'traversed_arcs': 43, 'fitness': 1}]
        self.assertEqual(str(s_l_align), str(e_s_l_align))


if __name__ == "__main__":
    unittest.main()
