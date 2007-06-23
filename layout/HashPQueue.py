class HashPQueue:
    """
    Hashing Priority Queue
    (c) 2001, 2005 Martin Grimme  <martin@gdesklets.org>

    This class implements a hashing priority queue. It is similar to a heap
    data structure, but allows to remove arbitrary elements, not only the
    topmost one.
    """


    # The comparators for the heap.
    LESS_THAN = 0
    GREATER_THAN = 1


    def __init__(self, comparator = LESS_THAN):
        """
        Creates a new HashPQueue object with the given comparator.
        """

        self.__heap = []
        self.__id2pos = {}
        self.__pos2id = {}
        self.__index_counter = 0
        self.__comparator = comparator



    def __compare(self, v1, v2):
        """
        Compares the given two values by applying the comparator.
        Returns whether the comparator returned True.
        """

        if (self.__comparator == self.LESS_THAN):
            return (v1 < v2)
        if (self.__comparator == self.GREATER_THAN):
            return (v1 > v2)



    def __swap(self, i1, i2):
        """
        Swaps the two elements given by their index values.
        """

        obj1 = self.__heap[i1]
        obj1_id = self.__pos2id[i1]
        obj2 = self.__heap[i2]
        obj2_id = self.__pos2id[i2]

        self.__id2pos[obj1_id] = i2
        self.__pos2id[i2] = obj1_id

        self.__id2pos[obj2_id] = i1
        self.__pos2id[i1] = obj2_id

        self.__heap[i1], self.__heap[i2] = self.__heap[i2], self.__heap[i1]



    def insert(self, object):
        """
        Inserts a new object into the queue. The object must be comparable.
        Returns the identifier for the object by which it can be removed again.
        """

        ident = self.__index_counter
        self.__index_counter += 1

        position = len(self.__heap)
        self.__heap.append(object)
        self.__id2pos[ident] = position
        self.__pos2id[position] = ident
        self.__heapify_upwards(position)

        return ident



    def pick(self):
        """
        Returns and removes the first object from the queue, or None if the
        queue is empty.
        """

        obj = self.top()
        if (obj != None): self.remove(self.__pos2id[0])

        return obj



    def remove(self, ident):
        """
        Removes the object with the given identifier from the queue.
        """

        if (ident in self.__id2pos):
            index = self.__id2pos[ident]

            obj_index = len(self.__heap) - 1
            obj = self.__heap[obj_index]
            obj_id = self.__pos2id[obj_index]

            del self.__id2pos[ident]
            del self.__pos2id[index]

            self.__heap.pop()
            if (index != obj_index):
                del self.__pos2id[obj_index]
                self.__id2pos[obj_id] = index
                self.__pos2id[index] = obj_id
                self.__heap[index] = obj
                self.__heapify_downwards(index)



    def top(self):
        """
        Returns the first object in the queue without removing it, or None if
        the queue is empty.
        """

        # return 'None' if the queue is empty
        if (not self.__heap):
            return None
        else:
            return self.__heap[0]



    def has(self, object):
        """
        Returns whether the queue contains the given object.
        """

        return object in self.__heap



    def __heapify_upwards(self, position):
        """
        Restores the heap structure on the heap from bottom up, starting at the
        given position.
        """

        # terminate the recursion as soon as the top of the heap has been
        # reached
        if (position == 0):
            return

        # get the index of the parent node
        parent = (position - 1) / 2

        # get the elements from the nodes
        element1 = self.__heap[position]
        element2 = self.__heap[parent]

        # compare them and swap them if necessary
        if (self.__compare(element1, element2)):
            self.__swap(position, parent)

        # continue heapifying
        self.__heapify_upwards(parent)



    def __heapify_downwards(self, position):
        """
        Restores the heap structure on the heap from top down, starting at the
        given position.
        """

        length = len(self.__heap)

        # get the indices of the child nodes
        child1 = 2 * position + 1
        child2 = 2 * position + 2

        # if there are no children, terminate the recursion
        if (child1 >= length):
            return

        # if there is only one child, take this one
        if (child1 < length and child2 >= length):
            # get the elements from the nodes
            element1 = self.__heap[position]
            element2 = self.__heap[child1]
            child = child1

        # if there are two children, take the one complying to the comparator
        if (child1 < length and child2 < length):
            # get the elements from the nodes
            element1 = self.__heap[position]
            childelem1 = self.__heap[child1]
            childelem2 = self.__heap[child2]

            # find the appropriate child element
            if (self.__compare(childelem1, childelem2)):
                element2 = childelem1
                child = child1
            else:
                element2 = childelem2
                child = child2

        # compare the nodes and swap them if necessary
        if (not self.__compare(element1, element2)):
            self.__swap(position, child)

        # continue heapifying
        self.__heapify_downwards(child)



#
# Sort a list by using the heapsort algorithm to demonstrate the heap's usage.
#
if (__name__ == "__main__"):
    items = [0, 5, 6, 3, 56, 23, 89, 543, 12, 546,
             76, 34, 5, 3, 4, 2, 4, 6, 3, 30]

    light_heap = HashPQueue(HashPQueue.LESS_THAN)
    heavy_heap = HashPQueue(HashPQueue.GREATER_THAN)

    for i in items:
        light_heap.insert(i)
        heavy_heap.insert(i)

    ascend = []
    while (1):
        object = light_heap.pick()
        if (object == None):
            break
        else:
            ascend.append(object)

    descend = []
    while (1):
        object = heavy_heap.pick()
        if (object == None):
            break
        else:
            descend.append(object)

    print "\nThe items to sort:\n", items
    print "\nSorted in ascending order:\n", ascend
    print "\nSorted in descending order:\n", descend
    print
