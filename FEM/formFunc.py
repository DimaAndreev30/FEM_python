import numpy as np


def get3N(coords):
    """
    Рассчитывает матрицу N для линейных функций формы
    на треугольном элементе с координатами вершин coords
    
    Таким образом, что f(x, y) = (1, x, y)N(F1, F2, F3)
    """
    
    (X1, Y1), (X2, Y2), (X3, Y3) = coords
    d1, d2, d3 = X2*Y3 - X3*Y2, X3*Y1 - X1*Y3, X1*Y2 - X2*Y1
    return np.array([[Y2 - Y3, Y3 - Y1, Y1 - Y2], 
                     [X3 - X2, X1 - X3, X2 - X1],
                     [     d1,      d2,      d3]], dtype=np.double)/(d1 + d2 + d3)


def getDNMatrix(t, s):
    """
    Рассчитывает матрицу Nij = [Ni, Nj] = (dNi/dt * dNj/ds - dNi/ds * dNj/dt)
    значений скобок пуассона для всевозможных пар функций формы
    на идеальном четырехугольном элементе:
        N1(t, s) = (1 - t)(1 - s)/4
        N2(t, s) = (1 + t)(1 - s)/4
        N3(t, s) = (1 + t)(1 + s)/4
        N4(t, s) = (1 - t)(1 + s)/4
    в точке (t, s)
    """
    
    return np.array([[      0 ,  (1 - s),  (s - t), -(1 - t)],
                     [-(1 - s),       0 ,  (1 + t), -(s + t)],
                     [ (t - s), -(1 + t),       0 ,  (1 + s)],
                     [ (1 - t),  (t + s), -(1 + s),       0 ]], dtype=np.double)/8

