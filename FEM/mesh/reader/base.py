__all__ = ["StreamReaderBase"]


import logging


class StreamReaderBase:
    """
    Базовый класс для чтения потока входных данных
    Последовательно принимает блоки информации через функцию apply.
    

    Атрибуты
    -------------
        
    isReady : bool
        Если True, значит данные готовы к интерпретации
        Не означает завершение чтения потока входных данных
    isEnd : bool
        Если True, значит найден конец потока входных данных
        
    """
    
    
    def __init__(self, logger=None):
        """
        Параметры
        -------------
        
        logger : logging-type object, optional
            Если None (default), то создается свой на основе библиотеки logging
        """
        
        if logger is None:
            self._logger = logging.getLogger("StreamReader")
        else:
            self._logger = logger
            
        self.reset()
        
        
    def readline(self, line):
        """
        Читает линию line
        """
    
        self.__lineNumber += 1
        self._logger.debug(f"Reading line number {self.__lineNumber}")
        self._apply(line)
        
    def readstream(self, stream):
        """
        Читает поток данных stream
        """
        
        for line in stream:
            self.readline(line)
            
            if self._isEnd is True:
                break
            

    def get(self):
        """
        Возвращает накопленные данные, если они готовы
        """
    
        self._logger.debug(f"Extracting data with ready is {self._isReady} and end is {self._isEnd}")
        
        if self._isReady:
            if self._isEnd is False:
                self._logger.warning("Extracting data while data stream does not reach it's end")
            return self._extract()
        else:
            raise ValueError("Data is not ready to be extracted")

    def reset(self):
        """
        Сбрасывает накопленные данные и состояние класса
        для последующего запуска чтения новых данных
        """
        
        self._logger.debug("Reset data")
    
        self.__lineNumber = 0
        self._isReady = False
        self._isEnd = False
        
        self._reset()
        
    def pop(self):
        """
        Возвращает накопленные данные, если они готовы, и сбрасывает их
        """
    
        result = self.get()
        self.reset()
        return result
        
        
    def _format(self, message):
        return f"in line number {self.__lineNumber} got '{message}'"
    
    
    @property
    def isReady(self):
        return self._isReady
    @property
    def isEnd(self):
        return self._isEnd
        
        
    def _extract(self):
        pass
    def _reset(self):
        pass
        
    
    def _apply(self, line):
        pass
    def _end_reader(self, line):
        raise ValueError("Unable to read the following line: input data has already reached the end; Try to collect the output data and use the reset function")

