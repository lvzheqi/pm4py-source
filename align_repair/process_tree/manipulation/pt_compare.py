from pm4py.objects.process_tree.pt_operator import Operator


class CompareResult(object):
    def __init__(self, value, subtree1, subtree2):
        self._value = value
        self._subtree1 = subtree1
        self._subtree2 = subtree2

    def _get_value(self):
        return self._value

    def _get_subtree1(self):
        return self._subtree1

    def _get_subtree2(self):
        return self._subtree2

    def __repr__(self):
        output = "Two trees are same!" if self._value else "Two trees are different! \n"
        output = output + "\t Subtree1:" + str(self._subtree1) + "\n" if not self._value else output
        output = output + "\t Subtree2:" + str(self._subtree2) if not self._value else output
        return output

    value = property(_get_value)
    subtree1 = property(_get_subtree1)
    subtree2 = property(_get_subtree2)


def apply(tree1, tree2, option=1):
    """
    Compare process trees and return two smallest subtree that cause different in the original trees,
    otherwise return True, None, None.

    Parameters
    -----------
        tree1
            Process Tree
        tree2
            Process Tree
        option

    Returns
    ------------
        CompareResult
    """
    value, sub1, sub2 = True, None, None
    if tree1.operator is not None and tree2.operator is not None and tree1.operator != tree2.operator:
        value, sub1, sub2 = False, tree1, tree2
    elif (tree1.parent is None or tree2.parent is None) and \
            (tree1.operator != tree2.operator or tree1.label != tree2.label):
        value, sub1, sub2 = False, tree1, tree2
    elif tree1.operator != tree2.operator or tree1.label != tree2.label:
        value, sub1, sub2 = False, tree1.parent, tree2.parent

    elif tree1.operator is not None:
        if len(tree1.children) != len(tree2.children):
            value, sub1, sub2 = False, tree1, tree2

        elif tree1.operator == Operator.SEQUENCE or tree1.operator == Operator.LOOP:
            flag, subtree1, subtree2 = 0, None, None
            for i in range(len(tree1.children)):
                com_res = apply(tree1.children[i], tree2.children[i], option)
                if not com_res.value and flag == 0:
                    subtree1, subtree2 = com_res.subtree1, com_res.subtree2
                    flag += 1
                elif not com_res.value and flag < 2:
                    flag += 1
                elif flag == 2:
                    break
            if flag == 2:
                value, sub1, sub2 = False, tree1, tree2
            elif flag == 1:
                value, sub1, sub2 = False, subtree1, subtree2

        elif tree1.operator == Operator.XOR or tree1.operator == Operator.PARALLEL:
            children1 = [child for child in tree1.children]
            children2 = [child for child in tree2.children]
            for i in range(len(children1)-1, -1, -1):
                for j in range(len(children2)-1, -1, -1):
                    com_res = apply(children1[i], children2[j], option)
                    if com_res.value:
                        children1.pop(i)
                        children2.pop(j)
                        break
            if len(children2) > 1:
                value, sub1, sub2 = False, tree1, tree2
            elif len(children2) == 1:
                return apply(children1.pop(), children2.pop(), option)
    if option == 2 and sub1 is not None and sub1.parent is not None and \
            (sub1.parent.operator == Operator.LOOP or sub1.parent.operator == Operator.XOR):
        return CompareResult(value, sub1.parent, sub2.parent)
    return CompareResult(value, sub1, sub2)
