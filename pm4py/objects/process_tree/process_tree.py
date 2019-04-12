from pm4py.objects.process_tree.pt_operator import Operator


class ProcessTree(object):

    def __init__(self, operator=None, parent=None, children=None, label=None, index=0):
        """
        Constructor

        Parameters
        ------------
        operator
            Operator (of the current node) of the process tree
        parent
            Parent node (of the current node)
        children
            List of children of the current node
        label
            Label (of the current node)
        """
        self._operator = operator
        self._parent = parent
        self._children = list() if children is None else children
        self._label = label
        self._index = index

    def _set_operator(self, operator):
        self._operator = operator

    def _set_parent(self, parent):
        self._parent = parent

    def _set_label(self, label):
        self._label = label

    def _set_children(self, children):
        self._children = children

    def _get_children(self):
        return self._children

    def _get_parent(self):
        return self._parent

    def _get_operator(self):
        return self._operator

    def _get_label(self):
        return self._label

    def _get_index(self):
        return self._index

    def _set_index(self, index):
        self._index = index

    def __repr__(self):
        """
        Returns a string representation of the process tree

        Returns
        ------------
        stri
            String representation of the process tree
        """
        if self.operator is not None:
            rep = str(self._operator) + '( '
            for i in range(0, len(self._children)):
                child = self._children[i]
                rep += str(child) + ', ' if i < len(self._children) - 1 else str(child)
            return rep + ' )'
        elif self.label is not None:
            return self.label
        else:
            return u'\u03c4'

    def __str__(self):
        """
        Returns a string representation of the process tree

        Returns
        ------------
        stri
            String representation of the process tree
        """
        return self.__repr__()

    # def __eq__(self, other):
    #     if self._operator != other.operator or self._label != other.label:
    #         return False
    #     if self._operator is not None:
    #         if len(self._children) != len(other.children):
    #             return False
    #         if self._operator == Operator.SEQUENCE or self._operator == Operator.LOOP:
    #             for i in range(len(self._children)):
    #                 if self._children[i] != other.children[i]:
    #                     return False
    #         elif self._operator == Operator.XOR or self._operator == Operator.PARALLEL:
    #             children1 = [child for child in self._children]
    #             children2 = [child for child in other.children]
    #             for child1 in children1:
    #                 flag = 0
    #                 for i in range(len(children2)-1, -1, -1):
    #                     if children2[i] == child1:
    #                         children2.remove(children2[i])
    #                         flag = 1
    #                         break
    #                 if flag == 0:
    #                     return False
    #
    #     return True

    parent = property(_get_parent, _set_parent)
    children = property(_get_children, _set_children)
    operator = property(_get_operator, _set_operator)
    label = property(_get_label, _set_label)
    index = property(_get_index, _set_index)
