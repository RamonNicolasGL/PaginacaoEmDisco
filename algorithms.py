class PageReplacementAlgorithm:
    def __init__(self, capacity):
        self.capacity = capacity
        # Memória física fixa: preenchida com -1 para indicar vazio
        # O índice da lista representa o ID DO FRAME (0, 1, 2...)
        self.memory = [-1] * capacity 
        self.page_faults = 0
        self.evictions = 0
    
    def access(self, page_id):
        raise NotImplementedError

    def get_resident_set(self):
        # Retorna apenas as páginas válidas (diferentes de -1)
        return self.memory

class FIFO(PageReplacementAlgorithm):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.pointer = 0  # Aponta para o próximo frame a ser substituído (Circular)

    def access(self, page_id):
        # 1. HIT: Verifica se a página já está em algum frame
        if page_id in self.memory:
            return True 

        # 2. MISS
        self.page_faults += 1

        # Verifica se vai ocorrer evicção (se o slot atual não está vazio)
        # Nota: No FIFO circular, se voltamos ao início e ele está ocupado, é evicção.
        # Uma forma simples é verificar se há -1 na memória antes de contar evicção.
        if -1 not in self.memory:
            self.evictions += 1
        
        # Substitui a página no frame apontado pelo ponteiro
        self.memory[self.pointer] = page_id
        
        # Move o ponteiro para o próximo frame (circular: 0, 1, 2 -> 0, 1...)
        self.pointer = (self.pointer + 1) % self.capacity
        
        return False

class LRU(PageReplacementAlgorithm):
    def __init__(self, capacity):
        super().__init__(capacity)
        # Lista auxiliar para controlar a ordem de uso (apenas lógica)
        # O índice 0 dessa lista será o "Menos Recentemente Usado"
        self.usage_history = [] 

    def access(self, page_id):
        # 1. HIT
        if page_id in self.memory:
            # Atualiza a prioridade: remove da posição antiga e põe no fim (mais recente)
            self.usage_history.remove(page_id)
            self.usage_history.append(page_id)
            return True

        # 2. MISS
        self.page_faults += 1
        
        if -1 in self.memory:
            # Se tem espaço vazio, coloca no primeiro frame livre
            empty_frame_idx = self.memory.index(-1)
            self.memory[empty_frame_idx] = page_id
            self.usage_history.append(page_id)
        else:
            # Memória Cheia -> EVICÇÃO
            self.evictions += 1
            
            # Descobre quem é a vítima (o primeiro da lista de histórico)
            victim_page = self.usage_history.pop(0)
            
            # Descobre em qual FRAME a vítima estava
            frame_idx = self.memory.index(victim_page)
            
            # Substitui no frame correto
            self.memory[frame_idx] = page_id
            
            # Adiciona o novo no final do histórico
            self.usage_history.append(page_id)
            
        return False