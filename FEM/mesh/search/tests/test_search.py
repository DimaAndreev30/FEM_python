import numpy as np


from FEM.mesh import MeshClass, meshFrom
from FEM.mesh.search import *


mesh = meshFrom(name="doc/meshes/test.k")

def generalTestForSearchMethod(method):
    """
    Простейший тест функций, с которыми работает класс сетки для поиска элементов
    """
    
    searcher = method(mesh)
    
    # Поиск элемента по его центру:
    mesh.computeCenters()
    assert searcher.search(mesh.centers[5 ]) == 5
    assert searcher.search(mesh.centers[36]) == 36
    assert searcher.search(mesh.centers[17]) == 17
    
    assert searcher.search(mesh.centers[20]*1.1) == 20
    
    # Поиск точки за пределами области:
    assert searcher.search(np.array([0.0, 0.0])) == -1
    assert searcher.search(np.array([1.1, 0.0])) == -1
    assert searcher.search(np.array([0.0, 1.1])) == -1
    
    # Поиск точки на границах элементов:
    assert searcher.search(mesh.nodes[55]) in (25, 26, 74, 95)
    assert searcher.search((mesh.nodes[55] + mesh.nodes[53])/2) in (25, 74)
    


class TestSearch():
    
    def test_brute(self):
        generalTestForSearchMethod(BruteforseMeshSearch)
        
    def test_presel(self):
        generalTestForSearchMethod(PreselectionMeshSearch)
        
    def test_steps(self):
        generalTestForSearchMethod(StepsMeshSearch)