from collections import deque

class PageReplacementAlgorithm:
    """Classe base para garantir que todos os algoritmos sigam o mesmo padrão."""
    def __init__(self, capacity):
        self.capacity = capacity
        self.frames = []
        self.page_faults = 0
        self.evictions = 0
    
    def access(self, page_id):
        raise NotImplementedError("Os algoritmos devem implementar este método.")


#FIFO (Herda de PageReplacementAlgorithm)
class FIFO(PageReplacementAlgorithm):
    def __init__(self, capacity):
        super().__init__(capacity)
        # FIFO precisa de uma fila extra ou usar a ordem de inserção da lista
    
    def access(self, page_id):
        # 1. Verifica se está na memória (HIT)
        if page_id in self.frames:
            return True # Hit

        # 2. MISS (Page Fault)
        self.page_faults += 1
        
        # 3. Verifica se precisa remover alguém (Memória cheia)
        if len(self.frames) >= self.capacity:
            self.evictions += 1
            self.frames.pop(0) # Remove o primeiro (o mais antigo)
        
        # 4. Adiciona o novo
        self.frames.append(page_id)
        return False # Miss