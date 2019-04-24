import unittest

from pm4py.objects.process_tree import util as pt_util

from align_repair.pt_manipulate.pt_compare import pt_compare


class PTCompareTest(unittest.TestCase):

    @staticmethod
    def compare_diff_tree(s_tree1, s_tree2):
        tree1 = pt_util.parse(s_tree1)
        tree2 = pt_util.parse(s_tree2)
        return pt_compare(tree1, tree2)

    def test_compare_diff_tree(self):

        result = PTCompareTest.compare_diff_tree(" +( ->( j, k ), a, b )",
                                                 " +( a, ->( j, k ), b )")
        self.assertTrue(result.value)

        result = PTCompareTest.compare_diff_tree(" +( *( j, k , τ), a, b )",
                                                 " +( a, ->( j, k ), b )")
        self.assertFalse(result.value)
        self.assertEqual(str(result.subtree1), str(pt_util.parse("*( j, k ,τ)")))
        self.assertEqual(str(result.subtree2), str(pt_util.parse("->( j, k )")))

        result = PTCompareTest.compare_diff_tree(" +( *( j, k, τ ), a )",
                                                 " +( a, ->( j, k ), b )")
        self.assertFalse(result.value)
        self.assertEqual(str(result.subtree1), str(pt_util.parse("+( *( j, k, τ ), a )")))
        self.assertEqual(str(result.subtree2), str(pt_util.parse("+( a, ->( j, k ), b )")))

        result = PTCompareTest.compare_diff_tree(" +( ->( j, k ), a, X(c, d) )",
                                                 " +( a, ->( j, k ), b )")
        self.assertFalse(result.value)
        self.assertEqual(str(result.subtree1), str(pt_util.parse("+( ->( j, k ), a, X(c, d) )")))
        self.assertEqual(str(result.subtree2), str(pt_util.parse("+( a, ->( j, k ), b )")))

        result = PTCompareTest.compare_diff_tree("->( a, *( b, f, τ ), X( g, h ) ) ",
                                                 "->( a, *( b, f, τ ), +( g, h ) ) ")
        self.assertEqual(str(result.subtree1), str(pt_util.parse("X( g, h )")))
        self.assertEqual(str(result.subtree2), str(pt_util.parse("+( g, h )")))

        result = PTCompareTest.compare_diff_tree("->( a, *( ->( +( b, +( c, d ) ), e ), f, τ )) ",
                                                 "->( a, *( ->( +( b, X( c, d ) ), e ), f, τ )) ")
        self.assertEqual(str(result.subtree1), str(pt_util.parse("+( c, d )")))
        self.assertEqual(str(result.subtree2), str(pt_util.parse("X( c, d )")))


if __name__ == "__main__":
    unittest.main()
