import unittest

from pm4py.objects.process_tree import util as pt_utils

from repair_alignment.process_tree.operation import pt_compare, utils as pt_mani_utils


class PTUtilsTest(unittest.TestCase):

    @staticmethod
    def compare_diff_tree(s_tree1, s_tree2, option=1):
        tree1 = pt_utils.parse(s_tree1)
        tree2 = pt_utils.parse(s_tree2)
        return pt_compare.apply(tree1, tree2, option)

    def test_compare_diff_tree(self):

        result = PTUtilsTest.compare_diff_tree(" +( ->( j, k ), a, b )",
                                               " +( a, ->( j, k ), b )")
        self.assertTrue(result.value)

        result = PTUtilsTest.compare_diff_tree(" +( *( j, k , τ), a, b )",
                                               " +( a, ->( j, k ), b )")
        self.assertFalse(result.value)
        self.assertEqual(str(result.subtree1), str(pt_utils.parse("*( j, k ,τ)")))
        self.assertEqual(str(result.subtree2), str(pt_utils.parse("->( j, k )")))

        result = PTUtilsTest.compare_diff_tree(" +( *( j, k, τ ), a )",
                                               " +( a, ->( j, k ), b )")
        self.assertFalse(result.value)
        self.assertEqual(str(result.subtree1), str(pt_utils.parse("+( *( j, k, τ ), a )")))
        self.assertEqual(str(result.subtree2), str(pt_utils.parse("+( a, ->( j, k ), b )")))

        result = PTUtilsTest.compare_diff_tree(" +( ->( j, k ), a, X(c, d) )",
                                               " +( a, ->( j, k ), b )")
        self.assertFalse(result.value)
        self.assertEqual(str(result.subtree1), str(pt_utils.parse("+( ->( j, k ), a, X(c, d) )")))
        self.assertEqual(str(result.subtree2), str(pt_utils.parse("+( a, ->( j, k ), b )")))

        result = PTUtilsTest.compare_diff_tree("->( a, *( b, f, τ ), X( g, h ) ) ",
                                               "->( a, *( b, f, τ ), +( g, h ) ) ")
        self.assertEqual(str(result.subtree1), str(pt_utils.parse("X( g, h )")))
        self.assertEqual(str(result.subtree2), str(pt_utils.parse("+( g, h )")))

        result = PTUtilsTest.compare_diff_tree("->( a, *( ->( +( b, +( c, d ) ), e ), f, τ )) ",
                                               "->( a, *( ->( +( b, X( c, d ) ), e ), f, τ )) ")
        self.assertEqual(str(result.subtree1), str(pt_utils.parse("+( c, d )")))
        self.assertEqual(str(result.subtree2), str(pt_utils.parse("X( c, d )")))

    def test_compare_diff_tree_option2(self):

        result = PTUtilsTest.compare_diff_tree(" +( ->( j, k ), a, b )",
                                               " +( a, ->( j, k ), b )", 2)
        self.assertTrue(result.value)

        result = PTUtilsTest.compare_diff_tree(" *( *( j, k , τ), a, b )",
                                               " *( a, ->( j, k ), b )", 2)
        self.assertFalse(result.value)
        self.assertEqual(str(result.subtree1), str(pt_utils.parse("*( *( j, k , τ), a, b )")))
        self.assertEqual(str(result.subtree2), str(pt_utils.parse("*( a, ->( j, k ), b )")))

        result = PTUtilsTest.compare_diff_tree(" +( *( j, k, τ ), a )",
                                               " +( a, ->( j, k ), b )", 2)
        self.assertFalse(result.value)
        self.assertEqual(str(result.subtree1), str(pt_utils.parse("+( *( j, k, τ ), a )")))
        self.assertEqual(str(result.subtree2), str(pt_utils.parse("+( a, ->( j, k ), b )")))

        result = PTUtilsTest.compare_diff_tree(" +( ->( j, k ), a, X(c, d) )",
                                               " +( a, ->( j, k ), b )", 2)
        self.assertFalse(result.value)
        self.assertEqual(str(result.subtree1), str(pt_utils.parse("+( ->( j, k ), a, X(c, d) )")))
        self.assertEqual(str(result.subtree2), str(pt_utils.parse("+( a, ->( j, k ), b )")))

        result = PTUtilsTest.compare_diff_tree("X( a, *( b, f, τ ), X( g, h ) ) ",
                                               "X( a, *( b, f, τ ), +( g, h ) ) ", 2)
        self.assertEqual(str(result.subtree1), str(pt_utils.parse("X( a, *( b, f, τ ), X( g, h ) )")))
        self.assertEqual(str(result.subtree2), str(pt_utils.parse("X( a, *( b, f, τ ), +( g, h ) )")))

        result = PTUtilsTest.compare_diff_tree("->( a, *( ->( *( b, +( c, d ) ), e ), f, τ )) ",
                                               "->( a, *( ->( *( b, X( c, d ) ), e ), f, τ )) ", 2)
        self.assertEqual(str(result.subtree1), str(pt_utils.parse("*( b, +( c, d ) )")))
        self.assertEqual(str(result.subtree2), str(pt_utils.parse("*( b, X( c, d ) )")))

    def test_pt_depth(self):
        tree = pt_utils.parse("a")
        self.assertEqual(1, pt_mani_utils.pt_depth(tree))

        tree = pt_utils.parse("X(a, b)")
        self.assertEqual(2, pt_mani_utils.pt_depth(tree))

        tree = pt_utils.parse("X(a, ->(b, c), d)")
        self.assertEqual(3, pt_mani_utils.pt_depth(tree))

        tree = pt_utils.parse("X(a, ->(b, c, +(e, f)), *(d, X(g, h), τ))")
        self.assertEqual(4, pt_mani_utils.pt_depth(tree))


if __name__ == "__main__":
    unittest.main()
