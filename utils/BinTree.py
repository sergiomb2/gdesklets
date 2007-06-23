#
# Class for a generic comparator-sorted binary tree.
#
class BinTree(object):

    def __init__(self, value = None):

        self._parent = None
        self._left_child = None
        self._right_child = None
        self._value = value


    def _find_node(self, value, comparator):

        if (self._value == None):
            return (self, False)
        else:
            comp = comparator(value, self._value)
            if (comp < 0 and self._left_child):
                return self._left_child._find_node(value, comparator)
            elif (comp > 0 and self._right_child):
                return self._right_child._find_node(value, comparator)
            elif (comp == 0):
                return (self, True)
            else:
                return (self, False)


    def _get_successor(self):

        succ = self._right_child
        while (succ._left_child):
            succ = succ._left_child

        return succ


    def insert(self, value, comparator):

        node, success = self._find_node(value, comparator)

        if (node._value == None):
            node._value = value
        else:
            new_node = BinTree(value)
            new_node._parent = node
            if (comparator(value, node._value) < 0):
                node._left_child = new_node
            else:
                node._right_child = new_node


    def find(self, value, comparator):

        node, success = self._find_node(value, comparator)
        if (success): return node._value


    def remove(self, value, comparator):

        node, success = self._find_node(value, comparator)
        if (success):
            if (not node._left_child or not node._right_child):
                y = node
            else:
                y = node._get_successor()

            if (y._left_child):
                x = y._left_child
            else:
                x = y._right_child

            if (x):
                x._parent = y._parent

            if (not y._parent):
                if (x):
                    self._value = x._value
                else:
                    self._value = None
            else:
                if (y == y._parent._left_child):
                    y._parent._left_child = x
                else:
                    y._parent._right_child = x

            if (y != node):
                node._value = y._value

