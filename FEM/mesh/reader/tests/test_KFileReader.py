from FEM.mesh.reader import KFileReader


class TestKFileReader:
    
    def test_baseRead(self):
        reader = KFileReader()

        reader.readstream(open('doc/meshes/mini_test.k'))
        result = reader.pop()

        third_element = result['cells'][2]
        assert third_element == [6, 5, 2, 1], "incorrect read result"

    def test_split(self):
        reader = KFileReader()

        reader.readstream(open('doc/meshes/split_test.k'))
        result = reader.pop()

        second_element = result['cells'][1]
        assert second_element == [5, 6, 7, 4], "incorrect split result"

    def test_regularRead(self):
        reader = KFileReader()
        
        reader.readstream(open('doc/meshes/test.k'))
        reader.pop()