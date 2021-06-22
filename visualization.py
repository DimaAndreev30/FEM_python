"""
Пример использования классов Normalize и LinearSegmentedColormap
из модуля colors библиотеки matplotlib:

from matplotlib.colors import Normalize, LinearSegmentedColormap

normalizer = Normalize()
colormap = LinearSegmentedColormap(
    'map',
    {'red':   [(0.0,  0.0, 0.0),
               (0.5,  1.0, 1.0),
               (1.0,  1.0, 1.0)],

     'green': [(0.0,  0.0, 0.0),
               (0.25, 0.0, 0.0),
               (0.75, 1.0, 1.0),
               (1.0,  1.0, 1.0)],

     'blue':  [(0.0,  0.0, 0.0),
               (0.5,  0.0, 0.0),
               (1.0,  1.0, 1.0)]})
               
colormap(normalizer(data).data) # -> выдает цвета в формате RGBA
"""

"""
Пример использования модуля cm библиотеки matplotlib:

from matplotlib import cm

cm.cmap_d.keys() для вывода названий предустановленных карт
'viridis' - для приятной картинки
'coolwarm' - для симметрии отрицательных/положительных значений
'gray' - для черно-белой картинки

cmap = cm.get_cmap('viridis')
mappable = cm.ScalarMappable(cmap=cmap)
mappable.to_rgba(data)
plt.colorbar(mappable)
"""


import matplotlib.pyplot as plt
import matplotlib.cm as cm


def visualizeCellsValues(mesh, values, 
                         contour=False, contour_color=[[0.0, 0.0, 0.0, 0.4]],
                         mappable=None, cmap=cm.get_cmap('viridis'), 
                         bar_orientation='vertical', bar_shrink=1.0,
                         **kwargs):
    """
    Визуализация значений values на ячейках сетки mesh
    """
        
    if mappable is None:
        mappable = cm.ScalarMappable(cmap=cmap)
    
    plt.gca().set_aspect('equal')
    mesh.visualize(color=mappable.to_rgba(values), fill=True, **kwargs)
    if contour is True:
        mesh.visualize(color=contour_color, fill=False, **kwargs)
    plt.colorbar(mappable, orientation=bar_orientation, shrink=bar_shrink)
    
    
def visualizeNodesValues(mesh, values, levels=50,
                         contour=False, contour_color=[[0.0, 0.0, 0.0, 0.4]],
                         mappable=None, cmap=cm.get_cmap('viridis'), 
                         bar_orientation='vertical', bar_shrink=1.0,
                         **kwargs):
    """
    Визуализация значений values на ячейках сетки mesh
    """
        
    if mappable is None:
        mappable = cm.ScalarMappable(cmap=cmap)
    
    plt.gca().set_aspect('equal')
    mesh.visualizeNodes(values=mappable.norm(values), cmap=mappable.cmap, levels=levels, **kwargs)
    if contour is True:
        mesh.visualize(color=contour_color, fill=False, **kwargs)
    plt.colorbar(mappable, orientation=bar_orientation, shrink=bar_shrink)