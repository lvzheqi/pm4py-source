import unittest

from pm4py.objects.process_tree import util as pt_utils

from repair_alignment.process_tree.operation import pt_number
from repair_alignment.deprecation import ar_lock

from ra_tests import utils


class LockAlignRepairTest(unittest.TestCase):
    def setUp(self):
        self.parameters = {'ret_tuple_as_trans_desc': True, 'PARAM_CHILD_LOCK': True}
        self.parameters_tuple_false = {'ret_tuple_as_trans_desc': False, 'PARAM_LOOP_LOCK': True}

    def test_align_repair1(self):
        tree1 = pt_utils.parse("+( a, X( g, h ) ) ")
        tree2 = pt_utils.parse("+( a, ->( g, h ) )")
        pt_number.apply(tree1, 'D', 1)
        pt_number.apply(tree2, 'D', 1)
        log = utils.create_event_log("gah")
        alignments = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '1_tau_1'), ('>>', None)),
                                     (('>>', '3_s'), ('>>', '3_s')), (('>>', '2_s'), ('>>', '2_s')),
                                     (('t_g_0', '>>'), ('g', '>>')),
                                     (('t_a_1', 'a'), ('a', 'a')), (('>>', '5_s'), ('>>', '5_s')),
                                     (('t_h_2', 'h'), ('h', 'h')),
                                     (('>>', '5_e'), ('>>', '5_e')), (('>>', '3_e'), ('>>', '3_e')),
                                     (('>>', '2_e'), ('>>', '2_e')),
                                     (('>>', '1_tau_2'), ('>>', None)), (('>>', '1_e'), ('>>', '1_e'))], 'cost': 5,
                       'visited_states': 18, 'queued_states': 35, 'traversed_arcs': 35, 'fitness': 0.736842105263158}]

        a_repair = ar_lock.apply(tree1, tree2, log, alignments, self.parameters)
        exp_a_repair = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '1_tau_1'), ('>>', None)),
                                       (('>>', '6_s'), ('>>', '6_s')), (('>>', '7_s'), ('>>', '7_s')),
                                       (('>>', '2_s'), ('>>', '2_s')),
                                       (('t_g_0', 'g'), ('g', 'g')), (('>>', '7_e'), ('>>', '7_e')),
                                       (('>>', '8_s'), ('>>', '8_s')),
                                       (('t_a_1', 'a'), ('a', 'a')), (('t_h_1', 'h'), ('h', 'h')),
                                       (('>>', '8_e'), ('>>', '8_e')),
                                       (('>>', '6_e'), ('>>', '6_e')), (('>>', '2_e'), ('>>', '2_e')),
                                       (('>>', '1_tau_2'), ('>>', None)), (('>>', '1_e'), ('>>', '1_e'))], 'cost': 0,
                         'fitness': 1.0}]

        # l_alignments = [{'alignment': [('>>', '1_s'), ('>>', None), ('>>', '3_s'), ('g', '>>'), ('>>', '2_s'),
        #                                ('a', 'a'), ('>>', '2_e'), ('>>', '5_s'), ('h', 'h'), ('>>', '5_e'),
        #                                ('>>', '3_e'), ('>>', None), ('>>', '1_e')], 'cost': 5, 'visited_states': 7,
        #                  'queued_states': 13, 'traversed_arcs': 15, 'fitness': 0.736842105263158}]
        # l_a_repair = repair_alignment.apply(tree1, tree2, log, l_alignments, self.parameters_tuple_false)
        # exp_l_a_repair = [{'alignment': [('>>', '1_s'), ('>>', None), ('>>', '6_s'), ('>>', '7_s'), ('g', 'g'),
        #                                  ('>>', '7_e'), ('>>', '8_s'), ('a', 'a'), ('h', 'h'), ('>>', '8_e'),
        #                                  ('>>', '6_e'), ('>>', None), ('>>', '1_e')], 'cost': 0, 'visited_states': 6,
        #                    'queued_states': 13, 'traversed_arcs': 15, 'fitness': 1}]

        for i in range(len(alignments)):
            self.assertEqual(list(map(lambda x: x[1], a_repair[i]["alignment"])),
                             list(map(lambda x: x[1], exp_a_repair[i]["alignment"])))
            self.assertEqual(a_repair[i]["cost"], exp_a_repair[i]["cost"])
            self.assertEqual(a_repair[i]["fitness"], exp_a_repair[i]["fitness"])
            # self.assertEqual(str(exp_l_a_repair[i]['alignment']), str(l_a_repair[i]['alignment']))
            # self.assertEqual(exp_l_a_repair[i]["cost"], l_a_repair[i]["cost"])

    def test_align_repair2(self):
        tree1 = pt_utils.parse("X( a, ->(b, c)) ")
        tree2 = pt_utils.parse("X( τ, ->(b, c))")
        pt_number.apply(tree1, 'D', 1)
        pt_number.apply(tree2, 'D', 1)
        log = utils.create_event_log("")
        alignments = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                                     (('>>', 'a'), ('>>', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                                     (('>>', '1_e'), ('>>', '1_e'))],
                       'cost': 2, 'visited_states': 6, 'queued_states': 6, 'traversed_arcs': 6, 'fitness': 0.0}]
        a_repair = ar_lock.apply(tree1, tree2, log, alignments, self.parameters)
        exp_a_repair = [{'alignment': [(('>>', '6_s'), ('>>', '6_s')), (('>>', '7_s'), ('>>', '7_s')),
                                       (('t_a_0', 'a'), ('>>', None)), (('>>', '7_e'), ('>>', '7_e')),
                                       (('>>', '6_e'), ('>>', '6_e'))],
                         'cost': 0, 'visited_states': 9, 'queued_states': 13, 'traversed_arcs': 13,
                         'fitness': 1}]

        # l_alignments = [
        #     {'alignment': [('>>', '1_s'), ('>>', '2_s'), ('>>', 'a'), ('>>', '2_e'), ('>>', '1_e')], 'cost': 2,
        #      'visited_states': 2, 'queued_states': 2, 'traversed_arcs': 2, 'fitness': 0.0}]
        #
        # l_a_repair = repair_alignment.apply(tree1, tree2, log, l_alignments, self.parameters_tuple_false)
        # exp_l_a_repair = [
        #     {'alignment': [('>>', '6_s'), ('>>', '7_s'), ('>>', None), ('>>', '7_e'), ('>>', '6_e')], 'cost': 0,
        #      'visited_states': 2, 'queued_states': 2, 'traversed_arcs': 2, 'fitness': 1}]

        for i in range(len(alignments)):
            self.assertEqual(list(map(lambda x: x[1], a_repair[i]["alignment"])),
                             list(map(lambda x: x[1], exp_a_repair[i]["alignment"])))
            self.assertEqual(a_repair[i]["cost"], exp_a_repair[i]["cost"])
            self.assertEqual(a_repair[i]["fitness"], exp_a_repair[i]["fitness"])
            # self.assertEqual(exp_l_a_repair[i]["cost"], l_a_repair[i]["cost"])

    def test_align_repair3(self):
        tree1 = pt_utils.parse("->( a, X(b, c)) ")
        tree2 = pt_utils.parse("->( a, X(b, τ))")
        pt_number.apply(tree1, 'D', 1)
        pt_number.apply(tree2, 'D', 1)
        log = utils.create_event_log("a")
        alignments = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                                     (('t_a_0', 'a'), ('a', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                                     (('>>', '3_s'), ('>>', '3_s')), (('>>', '4_s'), ('>>', '4_s')),
                                     (('>>', 'b'), ('>>', 'b')), (('>>', '4_e'), ('>>', '4_e')),
                                     (('>>', '3_e'), ('>>', '3_e')), (('>>', '1_e'), ('>>', '1_e'))],
                       'cost': 2, 'visited_states': 11, 'queued_states': 15, 'traversed_arcs': 15,
                       'fitness': 0.7777777777777778}]

        a_repair = ar_lock.apply(tree1, tree2, log, alignments, self.parameters)
        exp_a_repair = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                                       (('t_a_0', 'a'), ('a', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                                       (('>>', '6_s'), ('>>', '6_s')), (('>>', '8_s'), ('>>', '8_s')),
                                       (('>>', 'b'), ('>>', None)), (('>>', '8_e'), ('>>', '8_e')),
                                       (('>>', '6_e'), ('>>', '6_e')), (('>>', '1_e'), ('>>', '1_e'))],
                         'cost': 0, 'visited_states': 11, 'queued_states': 15, 'traversed_arcs': 15,
                         'fitness': 1}]

        # l_alignments = [{'alignment': [('>>', '1_s'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '3_s'),
        #                                ('>>', '5_s'), ('>>', 'c'), ('>>', '5_e'), ('>>', '3_e'), ('>>', '1_e')],
        #                  'cost': 2, 'visited_states': 3, 'queued_states': 4, 'traversed_arcs': 5,
        #                  'fitness': 0.7777777777777778}]
        #
        # l_a_repair = repair_alignment.apply(tree1, tree2, log, l_alignments, self.parameters_tuple_false)
        # exp_l_a_repair = [{'alignment': [('>>', '1_s'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '6_s'),
        #                                  ('>>', '8_s'), ('>>', None), ('>>', '8_e'), ('>>', '6_e'), ('>>', '1_e')],
        #                    'cost': 0, 'visited_states': 3, 'queued_states': 4, 'traversed_arcs': 5, 'fitness': 1}]

        for i in range(len(alignments)):
            self.assertEqual(list(map(lambda x: x[1], a_repair[i]["alignment"])),
                             list(map(lambda x: x[1], exp_a_repair[i]["alignment"])))
            self.assertEqual(a_repair[i]["cost"], exp_a_repair[i]["cost"])
            self.assertEqual(a_repair[i]["fitness"], exp_a_repair[i]["fitness"])
            # self.assertEqual(exp_l_a_repair[i]["cost"], l_a_repair[i]["cost"])

    def test_align_repair4(self):
        tree1 = pt_utils.parse("->( a, +(b, c)) ")
        tree2 = pt_utils.parse("->( a, X(b, c))")
        pt_number.apply(tree1, 'D', 1)
        pt_number.apply(tree2, 'D', 1)
        log = utils.create_event_log("abdc")
        alignments = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                                     (('t_a_0', 'a'), ('a', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                                     (('>>', '3_s'), ('>>', '3_s')), (('>>', '3_tau_1'), ('>>', None)),
                                     (('>>', '4_s'), ('>>', '4_s')), (('>>', '5_s'), ('>>', '5_s')),
                                     (('t_b_1', 'b'), ('b', 'b')), (('t_d_2', '>>'), ('d', '>>')),
                                     (('t_c_3', 'c'), ('c', 'c')), (('>>', '4_e'), ('>>', '4_e')),
                                     (('>>', '5_e'), ('>>', '5_e')), (('>>', '3_tau_2'), ('>>', None)),
                                     (('>>', '3_e'), ('>>', '3_e')), (('>>', '1_e'), ('>>', '1_e'))],
                       'cost': 5, 'visited_states': 18, 'queued_states': 37, 'traversed_arcs': 38,
                       'fitness': 0.8076923076923077}]
        a_repair = ar_lock.apply(tree1, tree2, log, alignments, self.parameters)
        exp_a_repair = [{'alignment': [],
                         'cost': 10, 'visited_states': 18, 'queued_states': 37, 'traversed_arcs': 38,
                         'fitness': 1 - 10 / (20 + 4)}]
        # l_alignments = [{'alignment': [('>>', '1_s'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', None),
        #                                ('>>', '3_s'), ('>>', '4_s'), ('b', 'b'), ('>>', '4_e'), ('d', '>>'),
        #                                ('>>', '5_s'), ('c', 'c'), ('>>', '5_e'), ('>>', '3_e'), ('>>', None),
        #                                ('>>', '1_e')], 'cost': 5, 'visited_states': 7, 'queued_states': 14,
        #                  'traversed_arcs': 14, 'fitness': 0.8076923076923077}]
        # l_a_repair = repair_alignment.apply(tree1, tree2, log, l_alignments, self.parameters_tuple_false)
        # exp_l_a_repair = [{'alignment': [('>>', '1_s'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', None),
        #                                  ('>>', '6_s'), ('>>', '8_s'), ('b', '>>'), ('d', '>>'), ('c', 'c'),
        #                                  ('>>', '8_e'), ('>>', '6_e'), ('>>', None), ('>>', '1_e')], 'cost': 10,
        #                    'visited_states': 6, 'queued_states': 6, 'traversed_arcs': 5,
        #                    'fitness': 0.5833333333333333}]
        for i in range(len(alignments)):
            self.assertEqual(a_repair[i]["cost"], exp_a_repair[i]["cost"])
            self.assertEqual(a_repair[i]["fitness"], exp_a_repair[i]["fitness"])
            # self.assertEqual(exp_l_a_repair[i]["cost"], l_a_repair[i]["cost"])

    def test_align_repair5(self):
        tree1 = pt_utils.parse("X( a, ->(b, c)) ")
        tree2 = pt_utils.parse("X( a, +(b, c))")
        pt_number.apply(tree1, 'D', 1)
        pt_number.apply(tree2, 'D', 1)
        log = utils.create_event_log("ab")
        alignments = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                                     (('t_a_0', 'a'), ('a', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                                     (('>>', '1_e'), ('>>', '1_e')), (('t_b_1', '>>'), ('b', '>>'))],
                       'cost': 5, 'visited_states': 9, 'queued_states': 13, 'traversed_arcs': 13,
                       'fitness': 0.5833333333333333}]

        a_repair = ar_lock.apply(tree1, tree2, log, alignments, self.parameters)
        exp_a_repair = [{'alignment': [(('>>', '1_s'), ('>>', '1_s')), (('>>', '2_s'), ('>>', '2_s')),
                                       (('t_a_0', 'a'), ('a', 'a')), (('>>', '2_e'), ('>>', '2_e')),
                                       (('>>', '1_e'), ('>>', '1_e')), (('t_b_1', '>>'), ('b', '>>'))],
                         'cost': 5, 'visited_states': 9, 'queued_states': 13, 'traversed_arcs': 13,
                         'fitness': 0.5833333333333333}]
        # l_alignments = [
        #     {'alignment': [('>>', '1_s'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('b', '>>'), ('>>', '1_e')],
        #      'cost': 5, 'visited_states': 3, 'queued_states': 5, 'traversed_arcs': 5, 'fitness': 0.5833333333333333}]
        # l_a_repair = repair_alignment.apply(tree1, tree2, log, l_alignments, self.parameters_tuple_false)
        # exp_l_a_repair = [
        #     {'alignment': [('>>', '1_s'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('b', '>>'), ('>>', '1_e')],
        #      'cost': 5, 'visited_states': 3, 'queued_states': 5, 'traversed_arcs': 5, 'fitness': 0.5833333333333333}]

        for i in range(len(alignments)):
            self.assertEqual(list(map(lambda x: x[1], a_repair[i]["alignment"])),
                             list(map(lambda x: x[1], exp_a_repair[i]["alignment"])))
            self.assertEqual(a_repair[i]["cost"], exp_a_repair[i]["cost"])
            self.assertEqual(a_repair[i]["fitness"], exp_a_repair[i]["fitness"])
            # self.assertEqual(exp_l_a_repair[i]["cost"], l_a_repair[i]["cost"])


if __name__ == "__main__":
    unittest.main()
