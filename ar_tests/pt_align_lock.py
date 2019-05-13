import unittest

from pm4py.objects.process_tree import util as pt_utils

from align_repair.process_tree.manipulation import pt_number
from align_repair.process_tree.alignments import to_lock_align


class AlignLockTest(unittest.TestCase):

    def test_range1(self):
        tree = pt_utils.parse("->( a, b, c)")
        pt_number.apply(tree, 'D', 1)
        alignments = [{'alignment': [('a', 'a'), ('b', 'b'), ('d', '>>'), ('c', 'c'), ('e', '>>')],
                       'cost': 10, 'visited_states': 6, 'queued_states': 11, 'traversed_arcs': 11,
                       'fitness': 0.6774193548387097}]
        ranges = to_lock_align.compute_lock_range(tree, alignments, [])
        expect_ranges = [{1: [[0, 4]], 2: [[0, 0]], 3: [[1, 1]], 4: [[3, 3]]}]
        self.assertEqual(str(expect_ranges), str(ranges))

    def test_range2(self):
        tree = pt_utils.parse("*( a, b, τ)")
        pt_number.apply(tree, 'D', 1)
        alignments = [{'alignment': [('>>', None), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '3_s'),
                                     ('b', 'b'), ('>>', '3_e'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'),
                                     ('>>', '3_s'), ('b', 'b'), ('>>', '3_e'), ('>>', '2_s'), ('a', 'a'),
                                     ('>>', '2_e'), ('>>', None)], 'cost': 0, 'visited_states': 20,
                       'queued_states': 42, 'traversed_arcs': 42, 'fitness': 1}]
        ranges = to_lock_align.compute_lock_range(tree, alignments, [])
        expect_ranges = [{1: [[0, 16]], 2: [[1, 3], [7, 9], [13, 15]], 3: [[4, 6], [10, 12]]}]
        self.assertEqual(str(expect_ranges), str(ranges))

    def test_range3(self):
        tree = pt_utils.parse("*( +( *(->( a, b), c, τ), d), X(e, f), τ)")
        pt_number.apply(tree, 'D', 1)
        alignments = [{'alignment': [('>>', None), ('>>', '2_s'), ('>>', None), ('>>', '4_s'), ('a', 'a'),
                                     ('d', 'd'), ('b', 'b'), ('>>', '4_e'), ('>>', '7_s'), ('c', 'c'),
                                     ('>>', '7_e'), ('>>', '4_s'), ('a', 'a'), ('b', 'b'), ('>>', '4_e'),
                                     ('>>', None), ('>>', None), ('>>', '2_e'), ('>>', '10_s'), ('e', 'e'),
                                     ('>>', '10_e'), ('>>', '2_s'), ('>>', None), ('>>', '4_s'), ('a', 'a'),
                                     ('b', 'b'), ('>>', '4_e'), ('>>', None), ('d', 'd'), ('>>', None),
                                     ('>>', '2_e'), ('>>', None)], 'cost': 0, 'visited_states': 39,
                       'queued_states': 97, 'traversed_arcs': 99, 'fitness': 1}]
        ranges = to_lock_align.compute_lock_range(tree, alignments, [])
        expect_ranges = [{1: [[0, 31]], 2: [[1, 17], [21, 30]], 3: [[3, 14], [23, 26]],
                          4: [[3, 7], [11, 14], [23, 26]], 5: [[4, 4], [12, 12], [24, 24]],
                          6: [[6, 6], [13, 13], [25, 25]], 7: [[8, 10]], 9: [[5, 5], [28, 28]],
                          10: [[18, 20]], 11: [[19, 19]]}]
        self.assertEqual(str(ranges), str(expect_ranges))

    def test_range4(self):
        tree = pt_utils.parse("+( ->( + (a, b), X(c, d)), e")
        pt_number.apply(tree, 'D', 1)
        alignments = [{'alignment': [('>>', None), ('>>', None), ('>>', 'b'), ('a', 'a'), ('f', '>>'), ('e', 'e'),
                                     ('>>', None), ('d', 'd'), ('>>', None), ('g', '>>')], 'cost': 12,
                       'visited_states': 12, 'queued_states': 27, 'traversed_arcs': 28, 'fitness': 0.6363636363636364}]
        ranges = to_lock_align.compute_lock_range(tree, alignments, [])
        expect_ranges = [
            {1: [[0, 9]], 2: [[2, 7]], 3: [[2, 3]], 4: [[3, 3]], 5: [[2, 2]], 6: [[7, 7]], 8: [[7, 7]], 9: [[5, 5]]}]
        self.assertEqual(str(expect_ranges), str(ranges))

    def test_range5(self):
        tree = pt_utils.parse("+( a, X(b, τ))")
        pt_number.apply(tree, 'D', 1)
        alignments = [
            {'alignment': [('>>', None), ('>>', '5_s'), ('a', 'a'), ('>>', None), ('>>', '5_e'), ('>>', None)],
             'cost': 0, 'visited_states': 8, 'queued_states': 15, 'traversed_arcs': 16, 'fitness': 1}]
        ranges = to_lock_align.compute_lock_range(tree, alignments, [])
        expect_ranges = [{1: [[0, 5]], 2: [[2, 2]], 3: [[1, 4]], 5: [[1, 4]]}]
        self.assertEqual(str(expect_ranges), str(ranges))

    def test_add_lock1(self):
        alignments = [{'alignment': [('a', 'a'), ('b', 'b'), ('d', '>>'), ('c', 'c'), ('e', '>>')],
                       'cost': 10, 'visited_states': 6, 'queued_states': 11, 'traversed_arcs': 11,
                       'fitness': 0.6774193548387097}]
        locks = [{0: ['1_s', '2_s'], 5: ['1_e'], 1: ['2_e', '3_s'], 2: ['3_e'], 3: ['4_s'], 4: ['4_e']}]
        to_lock_align.insert_lock_to_alignment(alignments, locks)
        expect_alignments = [{'alignment': [('>>', '1_s'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '3_s'),
                                            ('b', 'b'), ('>>', '3_e'), ('d', '>>'), ('>>', '4_s'), ('c', 'c'),
                                            ('>>', '4_e'), ('e', '>>'), ('>>', '1_e')], 'cost': 10, 'visited_states': 6,
                              'queued_states': 11, 'traversed_arcs': 11, 'fitness': 0.6774193548387097}]
        self.assertEqual(str(expect_alignments), str(alignments))

    def test_add_lock2(self):
        alignments = [{'alignment': [('>>', None), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', '3_s'),
                                     ('b', 'b'), ('>>', '3_e'), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'),
                                     ('>>', '3_s'), ('b', 'b'), ('>>', '3_e'), ('>>', '2_s'), ('a', 'a'),
                                     ('>>', '2_e'), ('>>', None)], 'cost': 0, 'visited_states': 20,
                       'queued_states': 42, 'traversed_arcs': 42, 'fitness': 1}]
        locks = [{0: ['1_s'], 17: ['1_e']}]
        to_lock_align.insert_lock_to_alignment(alignments, locks)
        expect_alignments = [{'alignment': [('>>', '1_s'), ('>>', None), ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'),
                                            ('>>', '3_s'), ('b', 'b'), ('>>', '3_e'), ('>>', '2_s'), ('a', 'a'),
                                            ('>>', '2_e'), ('>>', '3_s'), ('b', 'b'), ('>>', '3_e'), ('>>', '2_s'),
                                            ('a', 'a'), ('>>', '2_e'), ('>>', None), ('>>', '1_e')], 'cost': 0,
                              'visited_states': 20, 'queued_states': 42, 'traversed_arcs': 42, 'fitness': 1}]
        self.assertEqual(str(expect_alignments), str(alignments))

    def test_add_lock3(self):
        alignments = [{'alignment': [('>>', None), ('>>', '2_s'), ('>>', None), ('>>', '4_s'), ('a', 'a'),
                                     ('d', 'd'), ('b', 'b'), ('>>', '4_e'), ('>>', '7_s'), ('c', 'c'),
                                     ('>>', '7_e'), ('>>', '4_s'), ('a', 'a'), ('b', 'b'), ('>>', '4_e'),
                                     ('>>', None), ('>>', None), ('>>', '2_e'), ('>>', '10_s'), ('e', 'e'),
                                     ('>>', '10_e'), ('>>', '2_s'), ('>>', None), ('>>', '4_s'), ('a', 'a'),
                                     ('b', 'b'), ('>>', '4_e'), ('>>', None), ('d', 'd'), ('>>', None),
                                     ('>>', '2_e'), ('>>', None)], 'cost': 0, 'visited_states': 39,
                       'queued_states': 97, 'traversed_arcs': 99, 'fitness': 1}]
        locks = [
            {0: ['1_s'], 32: ['1_e'], 3: ['3_s'], 15: ['3_e'], 23: ['3_s'], 27: ['3_e'], 4: ['5_s'], 5: ['5_e', '9_s'],
             12: ['5_s'], 13: ['5_e', '6_s'], 24: ['5_s'], 25: ['5_e', '6_s'], 6: ['9_e', '6_s'], 7: ['6_e'],
             14: ['6_e'], 26: ['6_e'], 28: ['9_s'], 29: ['9_e'], 19: ['11_s'], 20: ['11_e']}]
        to_lock_align.insert_lock_to_alignment(alignments, locks)
        expect_alignments = [{'alignment': [('>>', '1_s'), ('>>', None), ('>>', '2_s'), ('>>', None), ('>>', '3_s'),
                                            ('>>', '4_s'), ('>>', '5_s'), ('a', 'a'), ('>>', '5_e'), ('>>', '9_s'),
                                            ('d', 'd'), ('>>', '9_e'), ('>>', '6_s'), ('b', 'b'), ('>>', '6_e'),
                                            ('>>', '4_e'), ('>>', '7_s'), ('c', 'c'), ('>>', '7_e'), ('>>', '4_s'),
                                            ('>>', '5_s'), ('a', 'a'), ('>>', '5_e'), ('>>', '6_s'), ('b', 'b'),
                                            ('>>', '6_e'), ('>>', '4_e'), ('>>', '3_e'), ('>>', None), ('>>', None),
                                            ('>>', '2_e'), ('>>', '10_s'), ('>>', '11_s'), ('e', 'e'), ('>>', '11_e'),
                                            ('>>', '10_e'), ('>>', '2_s'), ('>>', None), ('>>', '3_s'), ('>>', '4_s'),
                                            ('>>', '5_s'), ('a', 'a'), ('>>', '5_e'), ('>>', '6_s'), ('b', 'b'),
                                            ('>>', '6_e'), ('>>', '4_e'), ('>>', '3_e'), ('>>', None), ('>>', '9_s'),
                                            ('d', 'd'), ('>>', '9_e'), ('>>', None), ('>>', '2_e'), ('>>', None),
                                            ('>>', '1_e')], 'cost': 0, 'visited_states': 39, 'queued_states': 97,
                              'traversed_arcs': 99, 'fitness': 1}]
        self.assertEqual(str(expect_alignments), str(alignments))

    def test_add_lock4(self):
        alignments = [{'alignment': [('>>', None), ('>>', None), ('>>', 'b'), ('a', 'a'), ('f', '>>'), ('e', 'e'),
                                     ('>>', None), ('d', 'd'), ('>>', None), ('g', '>>')], 'cost': 12,
                       'visited_states': 12, 'queued_states': 27, 'traversed_arcs': 28, 'fitness': 0.6363636363636364}]
        locks = [{0: ['1_s'], 10: ['1_e'], 2: ['2_s', '3_s', '5_s'], 8: ['8_e', '6_e', '2_e'], 4: ['4_e', '3_e'],
                  3: ['5_e', '4_s'], 7: ['6_s', '8_s'], 5: ['9_s'], 6: ['9_e']}]

        to_lock_align.insert_lock_to_alignment(alignments, locks)
        expect_alignments = [{'alignment': [('>>', '1_s'), ('>>', None), ('>>', None), ('>>', '2_s'), ('>>', '3_s'),
                                            ('>>', '5_s'), ('>>', 'b'), ('>>', '5_e'), ('>>', '4_s'), ('a', 'a'),
                                            ('>>', '4_e'), ('>>', '3_e'), ('f', '>>'), ('>>', '9_s'), ('e', 'e'),
                                            ('>>', '9_e'), ('>>', None), ('>>', '6_s'), ('>>', '8_s'), ('d', 'd'),
                                            ('>>', '8_e'), ('>>', '6_e'), ('>>', '2_e'), ('>>', None), ('g', '>>'),
                                            ('>>', '1_e')], 'cost': 12, 'visited_states': 12, 'queued_states': 27,
                              'traversed_arcs': 28, 'fitness': 0.6363636363636364}]
        self.assertEqual(str(expect_alignments), str(alignments))

    def test_add_lock5(self):
        alignments = [
            {'alignment': [('>>', None), ('>>', '5_s'), ('a', 'a'), ('>>', None), ('>>', '5_e'), ('>>', None)],
             'cost': 0, 'visited_states': 8, 'queued_states': 15, 'traversed_arcs': 16, 'fitness': 1}]
        locks = [{0: ['1_s'], 6: ['1_e'], 2: ['2_s'], 3: ['2_e'], 1: ['3_s', '5_s'], 5: ['5_e', '3_e']}]
        to_lock_align.insert_lock_to_alignment(alignments, locks)
        expect_alignments = [{'alignment': [('>>', '1_s'), ('>>', None), ('>>', '3_s'), ('>>', '5_s'), ('>>', '5_s'),
                                            ('>>', '2_s'), ('a', 'a'), ('>>', '2_e'), ('>>', None), ('>>', '5_e'),
                                            ('>>', '5_e'), ('>>', '3_e'), ('>>', None), ('>>', '1_e')], 'cost': 0,
                              'visited_states': 8, 'queued_states': 15, 'traversed_arcs': 16, 'fitness': 1}]
        self.assertEqual(str(expect_alignments), str(alignments))


if __name__ == "__main__":
    unittest.main()
