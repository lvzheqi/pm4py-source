import unittest
import random
import copy

from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.objects.process_tree import util as pt_util

from align_repair.stochastic_generation.stochastic_pt_generation import randomly_create_new_tree
from align_repair.stochastic_generation import stochastic_mutated_pt
from align_repair.pt_manipulate.pt_compare import pt_compare
from align_repair.pt_manipulate.pt_number import pt_number


class PTGenerationTest(unittest.TestCase):
    def test_random_create_tree(self):
        for _ in range(100):
            tree1 = randomly_create_new_tree(random.randint(10, 35))
            tree2 = pt_util.parse(str(tree1))
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
            tree = randomly_create_new_tree(random.randint(10, 35))
            tree1 = stochastic_mutated_pt.randomly_create_mutated_tree(tree)
            tree2 = pt_util.parse(str(tree1))
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
            tree = randomly_create_new_tree(no_num)
            index_num = pt_number(tree, 'D', 1)
            self.assertEqual(no_num, index_num)

    def test_mutated_tree(self):
        for _ in range(100):
            tree1 = randomly_create_new_tree(random.randint(10, 35))
            tree2 = copy.deepcopy(tree1)
            sub1, sub2 = stochastic_mutated_pt.change_node_operator(tree2)
            com_res = pt_compare(tree1, tree2)
            self.assertEqual(str(sub1), str(com_res.subtree1))
            self.assertEqual(str(sub2), str(com_res.subtree2))

            tree2 = copy.deepcopy(tree1)
            sub1, sub2 = stochastic_mutated_pt.add_new_node(tree2)
            com_res = pt_compare(tree1, tree2)
            if sub1.operator == Operator.LOOP and sub1.children[1].operator is not None:
                self.assertEqual(str(sub1.children[1]), str(com_res.subtree1))
                self.assertEqual(str(sub2.children[1]), str(com_res.subtree2))
            else:
                self.assertEqual(str(sub1), str(com_res.subtree1))
                self.assertEqual(str(sub2), str(com_res.subtree2))

            tree2 = copy.deepcopy(tree1)
            sub1, sub2 = stochastic_mutated_pt.remove_node(tree2)
            com_res = pt_compare(tree1, tree2)
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
