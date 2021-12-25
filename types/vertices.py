import gpu
import bgl
from gpu_extras.batch import batch_for_shader

class VertexContainer:

  def __init__(self):
    self.__shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    self.__vertices = []
    self.__batch_points = None

  def append(self, vertex):
    self.__vertices.append(vertex)
    self.build_batch()
  
  def clear(self):
    self.__vertices.clear()
    self.build_batch()

  def get_vertices(self):
    return self.__vertices

  def build_batch(self):
    self.__batch_points = batch_for_shader(self.__shader, 'POINTS', {"pos": self.__vertices})

  def draw(self):
    if self.__batch_points:
      self.__shader.bind()
      bgl.glPointSize(10)
      self.__shader.uniform_float("color", (0.1, 0.1, 0.8, 1.0))
      self.__batch_points.draw(self.__shader)
      bgl.glPointSize(1)
