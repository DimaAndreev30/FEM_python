__all__ = ["getKrchU", "getKrchStressT"]


import numpy as np


def getKrchU(a, r, p, mu, G):
    """
    Вычисляет точный вектор перемещений в точке a для задачи Кирша
    """
    
    # a = (cos(phi), sin(phi))*|a|
    a2 = a*a # = (cos^2(phi), sin^2(phi))*|a|^2
    R2 = a2[0] + a2[1] # = |a|^2
    R = np.sqrt(R2) # = |a|
    cos2, sin2 = a2[0] - a2[1], a[0]*a[1] # = cos(2phi)*|a|^2, 1/2 * sin(2phi)*|a|^2
    
    polarU = p*np.array(
        [(1 - mu)*R2/(1 + mu) + r*r + (1 + r*r*(4/(1 + mu) - r*r/R2)/R2)*cos2, 
         -(1 + r*r*(2*(1 - mu)/(1 + mu) + r*r/R2)/R2)*2*sin2]
    )/(4*G*R)
    
    # Матрица перевода вектора из полярной в декартову СК:
    A = np.array([[a[0], -a[1]],
                  [a[1],  a[0]]]
                )/R
    
    return A@polarU

def getKrchStressT(a, r, p):
    """
    Вычисляет точное напряжение в точке a для задачи Кирша
    """

    # a = (cos(phi), sin(phi))*|a|
    a2 = a*a # = (cos^2(phi), sin^2(phi))*|a|^2
    R2 = a2[0] + a2[1] # = |a|^2
    cos2, sin2 = a2[0] - a2[1], a[0]*a[1] # = cos(2phi)*|a|^2, 1/2 * sin(2phi)*|a|^2
    
    polarT = p*np.array([R2 - r*r + (1 - r*r*(4 - 3*r*r/R2)/R2)*cos2,
                         R2 + r*r - (1 + 3*r*r*r*r/(R2*R2))*cos2,
                         -2*(1 + r*r*(2 - 3*r*r/R2)/R2)*sin2]
                       )/(2*R2)
    
    # Матрица перевода тензора из полярной в декартову СК:
    A = np.array([[a2[0], a2[1], -2*sin2],
                  [a2[1], a2[0],  2*sin2],
                  [ sin2, -sin2,    cos2]])/R2
    
    return A@polarT
