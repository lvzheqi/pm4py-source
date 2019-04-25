import unittest
import random
import copy

from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.objects.process_tree import util as pt_utils

from align_repair.process_tree.stochastic_generation import stochastic_pt_mutate as pt_mutate
from align_repair.process_tree.stochastic_generation import stochastic_pt_create as pt_create
from align_repair.process_tree.manipulation import pt_number
from align_repair.process_tree.manipulation import pt_compare


class PTGenerationTest(unittest.TestCase):
    def test_random_create_tree(self):
        for _ in range(100):
            tree1 = pt_create.apply(random.randint(10, 35))
            tree2 = pt_utils.parse(str(tree1))
            q1, q2 = list(), list()
            q1.append(tree1)
            q2.append(tree2)
            while len(q1) != 0:
                node1 = q1.pop(0)
                node2 = q2.pop(0)
                self.assertEqual(str(node1.parent), str(node2.parent))
                self.assertEqual(str(node1.children), str(node2.children))
                for i in range(len(node1.children)):
                    q1.append(node1.children[i])
                    q2.append(node2.children[i])

    def test_random_mutated_tree(self):
        for _ in range(100):
            tree = pt_create.apply(random.randint(10, 35))
            tree1 = pt_mutate.apply(tree)
            tree2 = pt_utils.parse(str(tree1))
            q1, q2 = list(), list()
            q1.append(tree1)
            q2.append(tree2)
            while len(q1) != 0:
                node1 = q1.pop(0)
                node2 = q2.pop(0)
                self.assertEqual(str(node1.parent), str(node2.parent))
                self.assertEqual(str(node1.children), str(node2.children))
                for i in range(len(node1.children)):
                    q1.append(node1.children[i])
                    q2.append(node2.children[i])

    def test_random_create_tree_node(self):
        for _ in range(100):
            no_num = random.randint(10, 35)
            tree = pt_create.apply(no_num)
            index_num = pt_number.apply(tree, 'D', 1)
            self.assertEqual(no_num, index_num)

    def test_mutated_tree(self):
        for _ in range(100):
            tree1 = pt_create.apply(random.randint(10, 35))
            tree2 = copy.deepcopy(tree1)
            sub1, sub2 = pt_mutate.change_node_operator(tree2, None)
            com_res = pt_compare.apply(tree1, tree2)
            self.assertEqual(str(sub1), str(com_res.subtree1))
            self.assertEqual(str(sub2), str(com_res.subtree2))

            tree2 = copy.deepcopy(tree1)
            sub1, sub2 = pt_mutate.add_new_node(tree2, None)
            com_res = pt_compare.apply(tree1, tree2)
            if sub1.operator == Operator.LOOP and sub1.children[1].operator is not None:
                self.assertEqual(str(sub1.children[1]), str(com_res.subtree1))
                self.assertEqual(str(sub2.children[1]), str(com_res.subtree2))
            else:
                self.assertEqual(str(sub1), str(com_res.subtree1))
                self.assertEqual(str(sub2), str(com_res.subtree2))

            tree2 = copy.deepcopy(tree1)
            sub1, sub2 = pt_mutate.remove_node(tree2, None)
            com_res = pt_compare.apply(tree1, tree2)
            if (len(sub1.children) == 2 and (sub1.parent is None or (sub2.operator is not None and
                                                                     (sub1.parent is not None and
                                                                      sub2.operator != sub1.parent.operator))
                                             or sub2.operator == Operator.LOOP)) or (len(sub1.children) > 2):
                self.assertEqual(str(sub1), str(com_res.subtree1))
                self.assertEqual(str(sub2), str(com_res.subtree2))
            else:
                self.assertEqual(str(sub1.parent), str(com_res.subtree1))
                self.assertEqual(str(sub2.parent), str(com_res.subtree2))


if __name__ == "__main__":
    unittest.main()
