import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle


def plotMesh(nodes, cells, color=['#A8A8A8'], fill=False, **kwargs):
    """
    Визуализация двумерной сетки
    
    
    Параметры
    -------------
    
    nodes : array-like
        Список координат вершин сетки (x, y)
    
    cells : iterable, int
        Список номеров вершин элементов сетки (n_1, n_2, ... n_m)
        
    color : iterable, color-type
        Список цветов, которыми будут изображены ячейки сетки
        Элементам из cells будут соответствовать цвета из cycle(color)
        
    **kwargs см.параметры функции matplotlib.plt.fill
    """
    
    for cell, clr in zip(cells, cycle(color)):
        coords = nodes[cell]
        plt.fill(coords[:, 0], coords[:, 1], color=clr, fill=fill, **kwargs)
        

def plotMeshNodes(nodes, cells, values, **kwargs):
    """
    Визуализация двумерной сетки градиентом вокруг узлов
    
    
    Параметры
    -------------
    
    nodes : array-like
        Список координат вершин сетки (x, y)
    
    cells : iterable, int
        Список номеров вершин элементов сетки
        
    **kwargs см.параметры функции matplotlib.plt.tricontourf
    """

    triangles = np.vstack(tuple(
            [[cell[0], cell[1 + i], cell[2 + i]] for i in range(len(cell) - 2)] \
            for cell in cells))
            
    plt.tricontourf(nodes[:, 0], nodes[:, 1], triangles, values, **kwargs)