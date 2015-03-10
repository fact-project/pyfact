"""
Some classes for generating closed paths around groups of hexagonal pixels.
"""
from __future__ import print_function
#from future.utils import python_2_unicode_compatible

import numpy as np
from matplotlib.patches import RegularPolygon
from utils import get_pixel_coords


#@python_2_unicode_compatible
class ClosedGraphNode(object):

    def __init__(self, vertex, next=None, prev=None):
        self.vertex = np.array(vertex)

        if next is None:
            self.next_node = self
        if prev is None:
            self.prev_node = self

        # used to find the end of an iteration over the closed graph
        self._iter_start_node = None
        self._last_node_seen = None

        self.__len = 1

    def append(self, new_node):
        my_old_next = self.next_node
        self.next_node = new_node
        new_node.next_node = my_old_next

        new_node.prev_node = self
        my_old_next.prev_node = new_node

        self.__len += 1

    def __len__(self):
        return self.__len            

    def __repr__(self):
        return str(self)

    def __del__(self):
        self.prev_node.next_node = self.next_node
        self.next_node.prev_node = self.prev_node

    def __str__(self):
        return u'ClosedGraphNode(L:{len}) @{me} next:{next} prev:{prev}'.format(
            me=self.vertex,
            next=self.next_node.vertex,
            prev=self.prev_node.vertex,
            len=len(self))

    def is_near(self, other_node, limit=1):
        if np.linalg.norm(self.vertex - other_node.vertex) < limit:
            return True
        else:
            return False

    def __iter__(self):
        self._iter_start_node = self
        self._next_for_iterator = self
        self._stop_iteration = False
        return self

    def next(self):
        ret = self._next_for_iterator
        if self._stop_iteration and (ret == self._iter_start_node):
            raise StopIteration

        self._next_for_iterator = ret.next_node
        self._stop_iteration = True
        return ret


def test_append():
    a = ClosedGraphNode([0,0])
    b = ClosedGraphNode([1,1])
    a.append(b)
    assert a.next_node == b
    assert a.prev_node == b
    assert b.next_node == a
    assert b.prev_node == a

def test_larger_circle():

    points = np.array([[0,0],[1,0],[1,1],[0,1]], dtype=float)

    circle = ClosedGraphNode(vertex=points[0])
    for i in range(1,len(points)):
        circle.append(ClosedGraphNode(vertex=points[i]))

    assert circle == circle.next_node.next_node.next_node.next_node
    return circle


def make_hexagon_groups():
    pixel_x, pixel_y = get_pixel_coords()
    hexagon_groups = []
    for trg_patch_id in range(160):
        hexes = []
        for i in range(9):
            x = pixel_x[trg_patch_id * 9 + i]
            y = pixel_y[trg_patch_id * 9 + i]
            
            hex = RegularPolygon(
                xy=(x, y),
                numVertices=6,
                radius=5.2,
                orientation=0)
            hexes.append(hex)
        hexagon_groups.append(hexes)
    return hexagon_groups

def hex_group_to_closed_graph_group(hex_group):
    closed_graph_group = []
    for hex in hex_group:
        closed_graph = None
        for point in hex.get_verts()[:6, :]:
            if closed_graph is None:
                closed_graph = ClosedGraphNode(point)
            else:
                closed_graph.append(ClosedGraphNode(point))
        closed_graph_group.append(closed_graph)

    return closed_graph_group

def snap_together(closed_graph_group):

    old_graph = closed_graph_group.pop()

    for new_graph in closed_graph_group:
        snapped = False
        for old_node in old_graph:
            for new_node in new_graph:
                if new_node.is_near(old_node):
                    old_next = old_node.next_node
                    new_prev = new_node.prev_node

                    old_node.next_node = new_node
                    new_node.prev_node = old_node

                    new_prev.next_node = old_next
                    old_next.prev_node = new_prev
                    snapped = True

                if snapped:
                    break
            if snapped:
                break

    return old_graph

