
from .vertices import *

class LineContainer(VertexContainer):

    def __init__(self):
        super().__init__()
        self._vertices_2d = [] 
        self.set_type('LINES')

    def get_start_point(self):
        return self.get_vertices()[0]

    def get_end_point(self):
        return self.get_vertices()[-1]

    def append(self, vertex_2d, vertex):
        self._vertices_2d.append(vertex_2d)
        super().append(vertex)

    def get_center_2d(self):
        return ((self._vertices_2d[0][0] + self._vertices_2d[1][0]) / 2, (self._vertices_2d[0][1] + self._vertices_2d[1][1]) / 2)

    def set_vertex(self, index, vertex_2d, vertex):
        self._vertices_2d[index] = vertex_2d
        super().set_vertex(index, vertex)

    def get_length(self):
        return (self.get_end_point() - self.get_start_point()).length

    def reset(self):
        super().reset()
        self._vertices_2d.clear()

    def is_initialized(self):
        return self.get_vertex_count() == 2