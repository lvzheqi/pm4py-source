from pm4py.objects.process_tree.pt_operator import Operator


def normal_pt_compare(tree1, tree2):
    """
    Compare two normalized process trees and return two smallest subtree that cause different in the original trees,
    otherwise return True, None, None.

    Parameters
    -----------
        tree1
            Process Tree
        tree2
            Process Tree
    Returns
    ------------
    Boolean
        that is true if the given trees are same
    subtree1
        the subtree in tree1 that differs from tree2
    subtree2
        the subtree in tree2 that differs from tree1

    """

    if tree1.operator is not None and tree2.operator is not None and tree1.operator != tree2.operator:
        return False, tree1, tree2
    if (tree1.parent is None or tree2.parent is None) and \
            (tree1.operator != tree2.operator or tree1.label != tree2.label):
        return False, tree1, tree2
    if tree1.operator != tree2.operator or tree1.label != tree2.label:
        return False, tree1.parent, tree2.parent

    if tree1.operator is not None:
        if len(tree1.children) != len(tree2.children):
            return False, tree1, tree2

        if tree1.operator == Operator.SEQUENCE or tree1.operator == Operator.LOOP:
            flag, subtree1, subtree2 = 0, None, None
            for i in range(len(tree1.children)):
                same, sub1, sub2 = pt_compare(tree1.children[i], tree2.children[i])
                if not same and flag == 0:
                    subtree1, subtree2 = sub1, sub2
                    flag += 1
                elif not same and flag < 2:
                    flag += 1
                elif flag == 2:
                    break
            if flag == 2:
                return False, tree1, tree2
            elif flag == 1:
                return False, subtree1, subtree2

        elif tree1.operator == Operator.XOR or tree1.operator == Operator.PARALLEL:
            children1 = [child for child in tree1.children]
            children2 = [child for child in tree2.children]
            for i in range(len(children1)-1, -1, -1):
                for j in range(len(children2)-1, -1, -1):
                    same, _, _ = pt_compare(children1[i], children2[j])
                    if same:
                        children1.pop(i)
                        children2.pop(j)
                        break
            if len(children2) > 1:
                return False, tree1, tree2
            elif len(children2) == 1:
                return pt_compare(children1.pop(), children2.pop())
    return True, None, None


def pt_compare(tree1, tree2):
    from align_repair.pt_manipulate.pt_normalize import parse_to_general_tree
    parse_to_general_tree(tree1)
    parse_to_general_tree(tree2)
    return normal_pt_compare(tree1, tree2)
