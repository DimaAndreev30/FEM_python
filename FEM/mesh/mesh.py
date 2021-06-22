__all__ = ["MeshClass", "meshFrom"]


import numpy as np

from itertools import combinations


from .reader import KFileReader
from FEM.geometry import getCenter, getS
from .plot import plotMesh, plotMeshNodes


class MeshClass:
    """
    Класс для работы с двумерной сеткой, состоящей из четырехугольных элементов
    
    (!) Предполагается, что после инициализации данные о сетке не меняются
    
    
    Атрибуты
    ------------
    
    N : int 
        Количество узлов сетки
    nodes : np.array(shape=(N, 2), dtype=np.double) 
        Список координат (x, y) узлов сетки
    
    M : int 
        Количество координат сетки
    cells : np.array(shape=(M, 4), dtype=np.int) 
        Список данных об элементах сетки (n1, n2, n3, n4):
            ni - номер i-ого узла в контуре элемента
            Номера упорядочены так, что:
                1. Контур ориентирован против часовой стрелки
                2. Сумма 1 и 3 углов < pi
                3. Центр элемента находится в треугольнике с вершинами (n1, n2, n3)
    coords : np.array(shape=(M, 4), dtype=np.double)
        Список координат узлов элементов сетки (a1, a2, a3, a4):
            ai - координата узла элемента с номером ni
    S : np.array(shape=(M, ), dtype=np.double)
        Список площадей элементов сетки
    trS : np.array(shape=(M, 4), dtype=np.double)
        Список площадей треугольников на элементах сетки (S1, S2, S3, S4):
            Si - площадь треугольника на i-ом угле элемента
            
    centers : np.array(shape=(M, 4), dtype=np.double)
        Список центров элементов сетки
    maxDiff : float
        Максимальное расстояние от центра элемента до его вершин по всем элементам
        
    neighbours : np.array(shape=(M, 4), dtype=np.int)
        Список индексов соседних элементов (n1, n2, n3, n4):
            ni - индекс элемента, граничащего с текущем через i-ое ребро
            (соединяющее i-ую и i+1-ую вершины)
            или NEIGHNONE, если через это ребро соседей нет
    
    matrixS : np.array(shape=(N, N), dtype=np.double)
        Матрица площадей сетки
    """
    
    def __init__(self, nodes, cells, S, trS, copy=True):
        """
        Параметры
        -------------
       
        nodes, cells, S, trS
            объекты, которыми инициализируются поля класса
            корректность их представления лежит на пользователе
            
        copy : bool, optional
            Если True, то входные данные будут скопированы
            Иначе копирование будет происходить только при необходимости
                    
        """
        
        
        self.nodes = np.array(nodes, copy=copy, dtype=np.double)
        self.cells = np.array(cells, copy=copy, dtype=np.int32)
        self.S     = np.array(S,     copy=copy, dtype=np.double)
        self.trS   = np.array(trS,   copy=copy, dtype=np.double)
        
        self.N = self.nodes.shape[0]
        self.M = self.cells.shape[0]
        
        
        self.coords = None
        self.centers = None
        self.maxDiff = None
        self.neighbours = None
        self.matrixS = None
        
        self.computeCoords()
        
        self._vizualizedNodes = self.nodes
        
        
    # Дополнительные данные о сетке:
        
    def computeCoords(self):
        if self.coords is None:
            self.coords = self.nodes[self.cells]
        
    def computeCenters(self):
        if self.centers is None:
            self.computeCoords()
            self.centers = getCenter(self.coords)
    
    def computeMaxDiff(self):
        if self.maxDiff is None:
            self.computeCenters()
            self.maxDiff = np.abs(
                self.centers[:, np.newaxis, :] - self.coords
            ).max(axis=(0, 1))
        
    def computeNeighbours(self):
        if self.neighbours is None:
            nodes_to_cells = [[] for _ in range(self.N)]
            for cell_id, cell in enumerate(self.cells):
                nodes_to_cells[cell[0]].append([0, cell_id])
                nodes_to_cells[cell[1]].append([1, cell_id])
                nodes_to_cells[cell[2]].append([2, cell_id])
                nodes_to_cells[cell[3]].append([-1, cell_id])
            
            self.NEIGHNONE = self.M
            self.neighbours = np.full_like(self.cells, self.NEIGHNONE, dtype=np.int32)
            for node_to_cells in nodes_to_cells:
                for (ind1, cell_id1), (ind2, cell_id2) \
                in combinations(node_to_cells, 2):
                    if self.cells[cell_id1, ind1 + 1] == \
                       self.cells[cell_id2, ind2 - 1]:
                        self.neighbours[cell_id1, ind1]     = cell_id2
                        self.neighbours[cell_id2, ind2 - 1] = cell_id1
        
    def computeMatrixS(self):
        if self.matrixS is None:
            self.matrixS = np.zeros(shape=(self.N, self.N), dtype=np.double)
            k = np.array([[2.0, 1.0, 0.5, 1.0], 
                          [1.0, 2.0, 1.0, 0.5], 
                          [0.5, 1.0, 2.0, 1.0], 
                          [1.0, 0.5, 1.0, 2.0]])/6
            for cell, S, trS in zip(self.cells, self.S, self.trS):
                S_loc = k*(S + trS[:, np.newaxis] + trS[np.newaxis, :])
                for i in range(4):
                    self.matrixS[cell, cell[i]] += S_loc[i]
        
        
    def getTriangleRel(self, a, cell_id):
        """
        Возвращает номера узлов элемента cell_id, образующих треугольник,
        содержащий точку a
        Работает в предположении, что a принадлежит элементу cell_id
        """
            
        if getS(a, *self.coords[cell_id, [0, 2]]) > 0:
            return [0, 2, 3]
        else:
            return [0, 1, 2]
        
    def getTriangle(self, a, cell_id):
        """
        Возвращает индексы узлов элемента cell_id, образующих треугольник,
        содержащий точку a
        Работает в предположении, что a принадлежит элементу cell_id
        """
            
        return self.cells[cell_id, self.getTriangleRel(a, cell_id)]
        
        
    # Методы для визуализации сетки и значений функции на ней:
    
    def shiftNodes(self, U):
        """
        Устанавливает новые координаты узлов для визуализации сетки,
        перемещая координаты недеформированной сетки на U
        """
    
        self._vizualizedNodes = self.nodes + U
        
    def resetNodes(self):
        """
        Сбрасывает координаты узлов для визуализации сетки на исходные
        """
    
        self._vizualizedNodes = self.nodes
    
    
    def visualize(self, color=['#787878'], fill=False, **kwargs):
        """
        Визуализация сетки
        """
    
        plotMesh(self._vizualizedNodes, self.cells, 
                 color=color, fill=fill, **kwargs)
    
    def visualizeSpecials(self, specials, 
                          color=['g'], fill=False, hatch='O', **kwargs):
        """
        Визуализация элементов сетки, заданных их номерами в списке specials
        """
    
        plotMesh(self._vizualizedNodes, self.cells[specials], 
                 color=color, fill=fill, hatch=hatch, **kwargs)
    
    def visualizeWithSpecials(self, specials, 
                              color=['#A8A8A8'], spcolor=['g'], 
                              hatch='.', sphatch='O', 
                              fill=False, spfill=False, **kwargs):
        """
        Визуализация сетки с выделением элементов, 
        заданных их номерами в списке specials
        """
        
        self.visualize(color=  color, hatch=  hatch, fill=  fill, **kwargs)
        self.visualizeSpecials(specials, 
                       color=spcolor, hatch=sphatch, fill=spfill, **kwargs)
                       
    def visualizeNodes(self, values, **kwargs):
        """
        Визуализация сетки градиентом около вершин по значениям color
        """

        plotMeshNodes(self._vizualizedNodes, self.cells, values, **kwargs)
        
        
def meshFrom(inputstream=None, name="doc/meshes/test.k", reader=None, logger=None):
        """
        Параметры
        -------------
       
        inputstream : iterable, optional
            Поток входных данных, с которыми будет работать reader
            Если None (default), то inputstream = open(name)
            
        name : str, optional
            Если inputstream = None, то устанавливается inputstream = open(name)
            
        reader : StreamReaderBase subclass, optional
            Класс, которым будет осуществляться обработка входных данных input
            Результатом его работы должен быть словарь, соответствующий входным
            данным конструктора MeshClass
            По умолчанию используется KFileReader
        
        logger : logging-type object, optional
            Лог для класса обработки входных данных
            Если None (default), то используется лог по умолчанию у reader
                    
        """
        
        if inputstream is None:
            inputstream = open(name)
            
        if reader is None:
            reader = KFileReader(logger)
            
        reader.readstream(inputstream)
        return MeshClass(**reader.pop(), copy=False)
        