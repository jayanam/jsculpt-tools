import gpu

from gpu_extras.batch import batch_for_shader

from .. utils.shader_utils import * 

class VertexContainer:

  def __init__(self):
    self.__shader = get_builtin_shader('UNIFORM_COLOR', '3D')
    self.__vertices = []
    self.__type = 'POINTS'
    self.__batch_points = None

  def set_type(self, type):
    self.__type = type

  def append(self, vertex):
    self.__vertices.append(vertex)
    self.build_batch()
  
  def clear(self):
    self.__vertices.clear()
    self.build_batch()

  def get_vertices(self):
    return self.__vertices

  def get_vertex_count(self):
    return len(self.__vertices)

  def reset(self):
      self.__vertices.clear()

  def set_vertex(self, index, vertex):
    self.__vertices[index] = vertex
    self.build_batch()

  def build_batch(self):
    self.__batch_points = batch_for_shader(self.__shader, self.__type, {"pos": self.__vertices})

  def draw(self):
    if self.__batch_points and self.get_vertex_count() > 0:
      self.__shader.bind()
      gpu.state.point_size_set(10)
      gpu.state.line_width_set(4)
      self.__shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
      self.__batch_points.draw(self.__shader)
      gpu.state.point_size_set(1)