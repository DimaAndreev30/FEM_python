__all__ = ['MeshSearchBase', 
           'BruteforseMeshSearch', 'PreselectionMeshSearch', 'StepsMeshSearch']


import numpy as np


from FEM.geometry import getS, getCenter, isBelong


class MeshSearchBase:
    """
    Базовый класс для реализации поиска элементов по точке на сетке
    
    
    Атрибуты
    ------------
    
    mesh : MeshClass
        Сетка, по которой осуществляется поиск
    """
    
    
    def __init__(self, mesh):
        self.mesh = mesh
    
    
    @property
    def mesh(self):
        return self._mesh
        
    @mesh.setter
    def mesh(self, mesh):
        self._mesh = mesh
        self._applyMesh()
        
    
    def _applyMesh(self):
        pass
        
        
    def search(self, a):
        """
        Поиск элемента в сетке mesh по координатам точки a
        """
        
        pass


class BruteforseMeshSearch(MeshSearchBase):
    """
    Класс для реализации поиска элементов методом тупого перебора
    """
    
    
    def _applyMesh(self):
        self._mesh.computeCoords()
        
    
    def search(self, a):
        for i, coords in enumerate(self._mesh.coords):
            if isBelong(a, coords) == True:
                return i
        return -1


class PreselectionMeshSearch(MeshSearchBase):
    """
    Класс для реализации поиска элементов методом перебора
    с предварительным отбором
    """
    
    def _applyMesh(self):
        self._mesh.computeMaxDiff()
    
    
    def search(self, a):
        candidates = np.where((
            np.abs(self._mesh.centers - a[np.newaxis, :]) <= 
            self._mesh.maxDiff[np.newaxis, :]
        ).all(axis=-1))[0]
        
        for i in candidates:
            if isBelong(a, self._mesh.coords[i]) == True:
                return i
        return -1


class StepsMeshSearch(MeshSearchBase):
    """
    Класс для реализации поиска элементов методом последовательного поиска
    """
    
    
    def _applyMesh(self):
        self._mesh.computeCenters()
        self._mesh.computeNeighbours()
    
        self.__alterMethod = PreselectionMeshSearch(self._mesh)
        self._currentCell = -1
        
            
    def setArea(self, a):
        """
        Устанавливает новую точку отсчета для последовательного поиска
        """
        
        self._currentCell = self.__alterMethod.search(a)
        return self._currentCell
        
    
    def search(self, a):
    
        self._path = [self._currentCell]
        while True:
            c = self._mesh.centers[self._currentCell]
            if np.allclose(a, c, atol=0.0):
                return self._currentCell
                
            coords = self._mesh.coords[self._currentCell]
            
            
            indx = 0
            S1 = getS(c, coords[indx], a)
            if S1 > 0:
                S2 = getS(c, coords[indx + 1], a)
                while S2 > 0:
                    indx = indx + 1
                    S1 = S2
                    S2 = getS(c, coords[indx + 1], a)
            else:
                indx = indx - 1
                S2 = S1
                S1 = getS(c, coords[indx], a)
                while S1 < 0:
                    indx = indx - 1
                    S2 = S1
                    S1 = getS(c, coords[indx], a)
            
            
            S = getS(c, coords[indx], coords[indx + 1])*(1 + 1e-5)
            if S1 - S2 < S:
                return self._currentCell
            else:
                self._currentCell = self._mesh.neighbours[self._currentCell, indx]
                if self._currentCell == self._mesh.NEIGHNONE:
                    return self.setArea(a)
                else:
                    self._path.append(self._currentCell)
                    
    def getPath(self):
        return self._path