__all__ = ["getD", "getB",
           "getStrain", "getCellsStrain",
           "applyCP", 
           "getK", "getM", "getF", 
           "horzBorder", "vertBorder", "applyNeiman", "setFNeiman", "fixAxis"]
           

import numpy as np
import scipy.sparse.linalg as sp

from .formFunc import getDNMatrix


# Упругие свойства:

def getD(E, mu):
    """
    Вычисляет матрицу для закона Гука
    """
    
    return np.array([[1.0, mu, 0.0], 
                     [mu, 1.0, 0.0], 
                     [0.0, 0.0, (1 - mu)/2]], dtype=np.double
                   )*E/(1 - mu*mu)


# Расчет деформаций и напряжений по узловым значениям перемещений:

def getB(coords, S):
    """
    Рассчет матрицы B для четырехугольных элементов для
    дальнейшего расчета деформаций
    """
    
    (X1, Y1), (X2, Y2), (X3, Y3), (X4, Y4) = coords
    return np.array([[Y2 - Y4, Y3 - Y1], 
                     [X4 - X2, X1 - X3]])/(2*S)
    
    """
    Альтернативный способ:
    
    asym = np.array([[ 0.0,  1.0],
                     [-1.0,  0.0]], dtype=np.double)
    form = np.array([[ 0.0, -1.0],
                     [ 1.0,  0.0],
                     [ 0.0,  1.0],
                     [-1.0,  0.0]], dtype=np.double)
    return asym@coords.T@form/(2*S)
    """
    
                     
def getStrain(U, B):
    """
    Вычисляет деформации на четырехугольном элементе с
    узловыми значениями перемещений U и матрицей B
    """
    (exx, exy), (eyx, eyy) = B@(U[0:2] - U[2:4])
    return [exx, eyy, exy + eyx]
    
def getCellsStrain(mesh, U):
    """
    Расчет деформаций на элементах сетки по узловым значениям перемещений U
    """

    return np.array([getStrain(U[cell], getB(coords, S))
                    for cell, coords, S in zip(mesh.cells, mesh.coords, mesh.S)])


# Метод согласованных результантов для расчета деформаций и напряжений в узлах сетки:

def applyCP(mesh, values):
    """
    Методом согласованных результантов вычисляет значения в узлах сетки mesh
    на основе средних по элементам значений values
    """
    
    R = np.zeros(shape=(mesh.N, ), dtype=np.double)
    for value, cell, S, trS in zip(values, mesh.cells, mesh.S, mesh.trS):
        R[cell] += (S + trS)*value
    
    mesh.computeMatrixS()
    return sp.cg(mesh.matrixS, R)[0]
    
    
# Расчет глобальных матриц для уравнений теории упругости:                   
                   
def getK(mesh, D,
         points=np.array([[-1.0, -1.0], 
                          [ 1.0, -1.0], 
                          [ 1.0,  1.0], 
                          [-1.0,  1.0]], dtype=np.double), #/np.sqrt(3),
         weights=np.array([1.0, 1.0, 1.0, 1.0], dtype=np.double)):
    """
    Рассчитывает глобальную матрицу жесткости K 
    для сетки из четырехугольных элементов
    
    При интегрировании по элементу используется квадратичная формула
    с опорными точками points и весами weights
    """
    
    # Предварительные расчеты, зависящие только от сетки, но не от упругих свойств:
    
    DNML = [getDNMatrix(t, s) for (t, s) in points]

    XX = np.zeros(shape=(mesh.N, mesh.N), dtype=np.double)
    YY = np.zeros(shape=(mesh.N, mesh.N), dtype=np.double)
    XY = np.zeros(shape=(mesh.N, mesh.N), dtype=np.double)
    
    for cell, coords in zip(mesh.cells, mesh.coords):
        
        X, Y = coords.T
        XX_loc = np.zeros(shape=(4, 4), dtype=np.double)
        YY_loc = np.zeros(shape=(4, 4), dtype=np.double)
        XY_loc = np.zeros(shape=(4, 4), dtype=np.double)
        for w, DNM in zip(weights, DNML):
            dNdX, dNdY = DNM@Y, X@DNM
            J = np.abs(X@dNdX)
            XX_loc += w*dNdX[:, np.newaxis]@dNdX[np.newaxis, :]/J
            YY_loc += w*dNdY[:, np.newaxis]@dNdY[np.newaxis, :]/J
            XY_loc += w*dNdX[:, np.newaxis]@dNdY[np.newaxis, :]/J
            
        for i in range(4):
            XX[cell[i], cell] += XX_loc[i]
            YY[cell[i], cell] += YY_loc[i]
            XY[cell[i], cell] += XY_loc[i]
            
    
    # Вычисление матрицы K на основе предварительных расчетов:
    
    K = np.zeros(shape=(2*mesh.N, 2*mesh.N), dtype=np.double)
    
    K[0::2, 0::2] = XX*D[0, 0] + YY*D[2, 2]
    K[1::2, 1::2] = YY*D[1, 1] + XX*D[2, 2]
    K[0::2, 1::2] = XY  *D[0, 1] + XY.T*D[2, 2]
    K[1::2, 0::2] = XY.T*D[0, 1] + XY  *D[2, 2]
            
    return K
    

def getM(mesh, po, t):
    """
    Рассчитывает глобальную матрицу масс системы M
    """
    
    mesh.computeSMatrix()
    M = np.zeros(shape=(2*mesh.N, 2*mesh.N), dtype=np.double)
    
    M[0::2, 0::2] = mesh.matrixS
    M[1::2, 1::2] = mesh.matrixS
    M *= po*t/6
    
    return M
    
    
def getF(mesh):
    """
    Возвращает нулевой вектор граничных нагрузок
    """
    
    return np.zeros(shape=(2*mesh.N,), dtype=np.double)
    

def horzBorder(y):
    return lambda a: np.isclose(a[..., 1], y, atol=1e-100)
def vertBorder(x):
    return lambda a: np.isclose(a[..., 0], x, atol=1e-100)
    
def applyNeiman(mesh, F, p, indx1, indx2):
    """
    Устанавливает равномерную граничную нагрузку p
    на ребро, соединяющее вершины с индексами indx1, indx2
    """
    
    a1, a2 = mesh.nodes[[indx1, indx2]]
    v = np.array([a2[1] - a1[1], a1[0] - a2[0]], dtype=np.double)

    F[2*indx1:2*indx1 + 2] += p*v/2
    F[2*indx2:2*indx2 + 2] += p*v/2

def setFNeiman(mesh, F, p, border_func):
    """
    Устанавливает равномерную граничную нагрузку p 
    вдоль границы border_func(a) = True
    """
    
    isBorder = border_func(mesh.nodes)
    for cell in mesh.cells:
        
        prev = cell[-1]
        for curr in cell:
            if isBorder[prev] and isBorder[curr]:
                applyNeiman(mesh, F, p, prev, curr)
            prev = curr
            
        
def fixAxis(mesh, K, F, axis, border_func):
    """
    Фиксирует положение (Ux = 0 для axis = 0, Uy = 0 для axis = 1)
    вдоль границы border_func(a) = True
    """
    
    for i in np.where(border_func(mesh.nodes))[0]:
        indx = 2*i + axis
        # F -= val*K[:, indx]
        F[indx] = 0 # val
        
        K[:, indx] = 0
        K[indx, :] = 0
        K[indx, indx] = 1

