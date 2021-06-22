import numpy as np

from .formFunc import get3N
from .mesh.search import StepsMeshSearch


class CentersInterpolator:
    """
    Класс для интерполяции по двумерной сетке с четырехугольными элементами
    Рассчитывает значения в центрах элементов по узловым значениям функции
    """
    
    def __init__(self, mesh):
        self.mesh = mesh
                    
    @property
    def mesh(self):
        return self._mesh
        
    @mesh.setter
    def mesh(self, mesh):
        mesh.computeCenters()
        
        self._A = np.empty(shape=(mesh.M, 3))
        for i, ((centerX, centerY), coords) \
        in enumerate(zip(mesh.centers, mesh.coords)):
            self._A[i] = np.array([centerX, centerY, 1], dtype=np.double)@ \
                          get3N(coords[:3])
                          
        self._mesh = mesh
            
    def apply(self, values):
        return np.array([values[indx]@a for indx, a \
                                        in zip(self._mesh.cells[:, :3], 
                                               self._A)], 
                        dtype=np.double)
    

class StraightInterpolator:
    """
    Класс для интерполяции по двумерной сетке с четырехугольными элементами
    Рассчитывает значения по узловым значениям функции на непрерывных списках точек
    """
    
    def __init__(self, mesh):
        self.mesh = mesh
        
    @property
    def mesh(self):
        return self._mesh
    
    @mesh.setter
    def mesh(self, mesh):
        self._mesh = mesh
        self._searcher = StepsMeshSearch(mesh)
        self._prev = None
    
    def applyOne(self, point, values):
        cell_id = self._searcher.search(point)
        if cell_id == -1:
            return None
            
        triangle = self._mesh.getTriangle(point, cell_id)
        
        if (self._prev != triangle).any():
            self._A = get3N(self._mesh.nodes[triangle])@values[triangle]
            self._prev = triangle
        
        return np.array([point[0], point[1], 1], dtype=np.double)@self._A
    
    def apply(self, points, values):
        self._searcher.setArea(points[0])
        return np.array([self.applyOne(point, values) for point in points], dtype=np.double)