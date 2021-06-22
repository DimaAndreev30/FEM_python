__all__ = ["KFileReader"]


from functools import wraps


from .base import StreamReaderBase
from FEM.geometry import getS


class KFileReader(StreamReaderBase):
    """
    Базовый класс для чтения данных о двумерной четырехугольной сетке типа MeshClass
    из файлов в формате '*.k', сгенерированных в cao-Fidesys
    
    Возвращает данные в виде четырех списков: nodes, cells, S, trS
    Назначение и формат см. в описании класса MeshClass
    
    """
    
    def __init__(self, *args, **kwargs):
        super(KFileReader, self).__init__(*args, **kwargs)
        
        
    def _reset(self):
        
        self.__nodes = []
        self.__cells = []
        self.__S = []
        self.__trS = []
        
        self.__nNode = 0
        self.__nodes_id = {}
        
        self._isReady = True
        
        self._apply = self.__block_reader
        
    def _extract(self):
        return {'nodes' : self.__nodes, 
                'cells' : self.__cells, 
                'S'     : self.__S, 
                'trS'   : self.__trS}
    
    
    def __skipSpaceDecarator(reader):
        
        @wraps(reader)
        def wrapper(self, line):
            line = line.split('$')[0].strip()
            if line:
                reader(self, line)
        
        return wrapper
            
    @__skipSpaceDecarator
    def __block_reader(self, line):
        
        if line[0] == '*':
            if line.find("NODE") != -1:
                self.__isInput = False
                self._apply = self.__node_reader
            elif line.find("ELEMENT_SHELL") != -1:
                self.__isInput = False
                self._apply = self.__shell_reader
            elif line.find("END") != -1:
                self._isEnd = True
                self._apply = self._end_reader
            else:
                self._logger.info(f"Skipping '{line}' block")
                self._apply = self.__skipping
        else:
            raise TypeError(f"Unexpected statement '{line}'")
            
    @__skipSpaceDecarator
    def __skipping(self, line):
        
        if line[0] == '*':
            self._apply = self.__block_reader
            self._apply(line)
            
    @__skipSpaceDecarator
    def __node_reader(self, line):
        
        try:
            nid, x, y = line.split()[0:3]
            self.__nodes_id[nid] = self.__nNode
            self.__nodes.append((float(x), float(y)))
        except ValueError:
            if self.__isInput is False:
                self._logger.warning("No nodes in *NODE* block found")

            self._apply = self.__block_reader
            self._apply(line)
        else:
            self.__isInput = True
            self.__nNode += 1
            
    @__skipSpaceDecarator
    def __shell_reader(self, line):
        
        try:
            # Считываем информацию о ячейке
            cellid, _, *indx = line.split()[0:6]
            n1, n2, n3, n4 = (self.__nodes_id[nid] for nid in indx)
            
            a1, a2, a3, a4 = (self.__nodes[i] for i in (n1, n2, n3, n4))
            
        except ValueError:
            if self.__isInput is False:
                self._logger.warning("No cells in *ELEMENT_SHELL* block found")
                
            self._apply = self.__block_reader
            self._apply(line)
            
        except KeyError:
            raise TypeError(f"Invalid node ID in cell number {cellid}")
            
        else:
            self.__isInput = True
            
            # Упорядочиваем вершины так, что бы ориентированная площадь была > 0:
            S1, S3 = getS(a4, a1, a2), getS(a2, a3, a4)
            if S1 + S3 < 0:
                n2, n4 = n4, n2
                
                a2, a4 = a4, a2
                S1, S3 = -S1, -S3
                
            # Делим четырехугольник на два треугольника лучшим образом:
            def getDot(a, b, c): 
                return (a[0] - c[0])*(b[0] - c[0]) + \
                       (a[1] - c[1])*(b[1] - c[1])
            sin = S1*getDot(a2, a4, a3) + S3*getDot(a2, a4, a1)
            if sin > 0:
                n1, n2, n3, n4 = n4, n1, n2, n3
                
                S2, S4 = S1, S3
                S1, S3 = getS(a3, a4, a1), getS(a1, a2, a3)
            else:
                S2, S4 = getS(a1, a2, a3), getS(a3, a4, a1)
            
            # Нумеруем вершины так, что бы центр четырехугольника
            # оказался в треугольнике с вершинами n1-n2-n3:
            if S2 < S4:
                self.__cells.append([n3, n4, n1, n2])
                self.__trS.append([S3, S4, S1, S2])
            else:
                self.__cells.append([n1, n2, n3, n4])
                self.__trS.append([S1, S2, S3, S4])
            self.__S.append(S1 + S3)
            
