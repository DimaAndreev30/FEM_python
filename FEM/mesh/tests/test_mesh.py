from math import isclose

from FEM.mesh import MeshClass, meshFrom


class TestMeshClass:
    
    def test_props(self):
        mesh = meshFrom(name='doc/meshes/mini_test.k')
        
        assert mesh.N == 7, "incorrect number of nodes"
        assert mesh.M == 3, "incorrect number of cells"
        
        mesh.computeCenters()
        assert isclose(mesh.centers[0][1], 0.5), "incorrect centers"
        
        mesh.computeMaxDiff()
        assert isclose(mesh.maxDiff[1], 1.25), "incorrect maxDiff"
        
        mesh.computeNeighbours()
        assert isclose(mesh.neighbours[2][1], 1), "incorrect neighbours"
        
        mesh.computeMatrixS()