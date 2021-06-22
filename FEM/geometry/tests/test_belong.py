import numpy as np

import FEM.geometry as geom


class TestBelongFunctions:

    def test_general(self):
        a, b, c, d = np.array((0, 1)), np.array((-1, -0.5)), np.array((1, -1)), np.array((1, 1))
        cell = np.array((a, b, c, d))
        
        assert geom.isBelong(np.array([0.0, 0.0]), cell) == True, "Should belong"
        assert geom.isBelong(geom.getCenter(cell), cell) == True, "Should belong"
        assert geom.isBelong(np.array([1.5, 0.0]), cell) == False, "Shouldn't belong"
        assert geom.isBelong(np.array([0.0, 1.5]), cell) == False, "Shouldn't belong"