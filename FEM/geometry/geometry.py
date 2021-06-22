def getS(a, b, c):
    """
    Вычисляет ориентированную площадь двумерного треугольника с вершинами a, b, c
    """
    
    return ((b[0]*c[1] - c[0]*b[1]) + \
            (c[0]*a[1] - a[0]*c[1]) + \
            (a[0]*b[1] - b[0]*a[1]))/2
            
def getFigureS(coords):
    """
    Вычисляет ориентированную площадь двумерного контура, задаваемого координатами coords
    """

    return ((coords[:-1, 0]*coords[1:, 1] - coords[:-1, 1]*coords[1:, 0]).sum() + \
             coords[ -1, 0]*coords[0 , 1] - coords[ -1, 1]*coords[0 , 0])/2

    
def getCenter(coords):
    """
    Вычисляет центры точек с координатами coords
    """

    return coords.mean(axis=-2)


def isBelong(a, coords):
    """
    Проверяет принадлежность точки a двумерному контуру с координатами вершин coords
    в предположении, что он ориентирован против часовой стрелки
    """
    
    return  getS(a, coords[ -1],   coords[0])    >= 0 and \
           (getS(a, coords[:-1].T, coords[1:].T) >= 0).all()
    
