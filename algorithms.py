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

class OTIMO(PageReplacementAlgorithm):
    # O construtor recebe a lista completa de referências
    def __init__(self, capacity, full_trace):
        super().__init__(capacity)
        self.full_trace = full_trace
        self.current_index = 0 # Contador para saber em qual passo da simulação estamos

    def access(self, page_id):
        # OTIMO calcula o futuro internamente usando o contador
        # O futuro é tudo que está APÓS o índice atual
        future_references = self.full_trace[self.current_index + 1:]
        
        # Incrementamos o contador para a próxima chamada
        self.current_index += 1
        
        # --- Lógica Padrão de Acesso ---
        
        # 1. HIT
        if page_id in self.memory:
            return True

        # 2. MISS
        self.page_faults += 1
        
        if -1 in self.memory:
            idx = self.memory.index(-1)
            self.memory[idx] = page_id
            return False

        # 3. EVICÇÃO
        self.evictions += 1
        
        victim_idx = -1
        farthest_distance = -1
        
        for i in range(len(self.memory)):
            candidate = self.memory[i]
            
            if candidate not in future_references:
                victim_idx = i
                break
            
            # Distância até a próxima aparição
            dist = future_references.index(candidate)
            if dist > farthest_distance:
                farthest_distance = dist
                victim_idx = i
                
        self.memory[victim_idx] = page_id
        return False

# Mantenha as importações e a classe base PageReplacementAlgorithm como estavam

class SECONDCHANCE(PageReplacementAlgorithm):
    """
    Implementação baseada na Seção 3.4.4:
    Usa uma lista encadeada (aqui simulada com list do Python).
    Se R=1, move a página para o FIM da lista (atualiza tempo de chegada).
    """
    def __init__(self, capacity):
        super().__init__(capacity)
        # Aqui self.memory vai funcionar como a Fila descrita na Fig 3.15
        # Vamos guardar dicionários para ter o ID e o bit R juntos: {'id': 7, 'r': 1}
        self.queue = [] 

    def access(self, page_id):
        # 1. HIT: Procura na fila
        for page in self.queue:
            if page['id'] == page_id:
                page['r'] = 1  # Apenas seta o bit R, não move nada ainda
                return True

        # 2. MISS
        self.page_faults += 1

        # Se tem espaço, apenas adiciona no fim (como recém-chegado)
        if len(self.queue) < self.capacity:
            self.queue.append({'id': page_id, 'r': 1})
            # Atualiza a memória visual para o relatório
            self.memory = [p['id'] for p in self.queue] + [-1]*(self.capacity - len(self.queue))
            return False

        # 3. EVICÇÃO (Memória Cheia)
        self.evictions += 1

        while True:
            # Olha o candidato mais antigo (cabeça da fila)
            candidate = self.queue[0]
            
            if candidate['r'] == 0:
                # Se R=0: É a vítima! Remove da frente.
                self.queue.pop(0)
                # Insere a nova página no final (recém-chegada)
                self.queue.append({'id': page_id, 'r': 1})
                break
            else:
                # Se R=1: Segunda Chance!
                # "O bit é limpo e a página é colocada no fim da lista" (Texto 3.4.4)
                candidate['r'] = 0
                removed = self.queue.pop(0) # Tira da frente
                self.queue.append(removed)  # Joga pro fim (atualiza tempo)
                # O loop continua e vai testar a nova "cabeça" da fila

        # Atualiza a visualização da memória
        self.memory = [p['id'] for p in self.queue]
        return False


class CLOCK(PageReplacementAlgorithm):
    """
    Implementação baseada na Seção 3.4.5:
    Lista circular. As páginas NÃO mudam de índice.
    Apenas o ponteiro se move.
    """
    def __init__(self, capacity):
        super().__init__(capacity)
        self.pointer = 0  # O "ponteiro do relógio"
        self.reference_bits = [0] * capacity # Bits R separados para facilitar

    def access(self, page_id):
        # 1. HIT
        if page_id in self.memory:
            idx = self.memory.index(page_id)
            self.reference_bits[idx] = 1 # Apenas liga o bit
            return True

        # 2. MISS
        self.page_faults += 1

        # Caso A: Espaço vazio (preenchimento linear inicial)
        if -1 in self.memory:
            empty_idx = self.memory.index(-1)
            self.memory[empty_idx] = page_id
            self.reference_bits[empty_idx] = 1
            # O texto 3.4.5 diz: "insere no relógio... e ponteiro é avançado"
            self.pointer = (self.pointer + 1) % self.capacity
            return False

        # Caso B: Evicção (Algoritmo do Relógio)
        self.evictions += 1

        while True:
            # "A página indicada pelo ponteiro é inspecionada"
            if self.reference_bits[self.pointer] == 1:
                # "Se R for 1, ele é zerado e o ponteiro avançado"
                self.reference_bits[self.pointer] = 0
                self.pointer = (self.pointer + 1) % self.capacity
            else:
                # "Se R for 0, a página é removida, a nova é inserida... e ponteiro avança"
                self.memory[self.pointer] = page_id
                self.reference_bits[self.pointer] = 1
                self.pointer = (self.pointer + 1) % self.capacity
                break
        
        return False

class NRU(PageReplacementAlgorithm):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.pointer = 0
        self.r_bits = [0] * capacity
        self.m_bits = [0] * capacity
        
        # Auxiliares para simulação
        self.access_counter = 0
        self.RESET_INTERVAL = 10 # Intervalo para zerar R (definir "Recentemente")

    def access(self, page_id):
        self.access_counter += 1
        
        # --- Simulação de Hardware ---
        # 1. Periodicamente, o SO zera os bits R para atualizar o "Recentemente"
        if self.access_counter % self.RESET_INTERVAL == 0:
            self.r_bits = [0] * self.capacity

        # 2. Simulação de Escrita: Páginas pares modificam o conteúdo (M=1)
        is_write = (page_id % 2 == 0)

        # --- Lógica de Acesso (HIT) ---
        if page_id in self.memory:
            idx = self.memory.index(page_id)
            self.r_bits[idx] = 1      # Referenciada
            if is_write:
                self.m_bits[idx] = 1  # Modificada
            return True

        # --- Lógica de Acesso (MISS) ---
        self.page_faults += 1

        # Caso A: Existe espaço vazio na memória
        if -1 in self.memory:
            empty_idx = self.memory.index(-1)
            self.memory[empty_idx] = page_id
            self.r_bits[empty_idx] = 1
            self.m_bits[empty_idx] = 1 if is_write else 0
            
            # Avança o ponteiro para manter a circularidade
            self.pointer = (self.pointer + 1) % self.capacity
            return False

        # Caso B: EVICÇÃO (Memória Cheia)
        # O texto diz: "tentar substituir primeiro páginas do nível 0... 
        # Pode ser necessário percorrer várias vezes a lista circular"
        self.evictions += 1
        
        victim_idx = -1
        
        # Tenta encontrar uma vítima percorrendo as classes em ordem: 0 -> 1 -> 2 -> 3
        for priority_class in [0, 1, 2, 3]:
            found = False
            # Varre a lista circular começando do ponteiro atual
            for i in range(self.capacity):
                curr_idx = (self.pointer + i) % self.capacity
                
                r = self.r_bits[curr_idx]
                m = self.m_bits[curr_idx]
                
                # Calcula a classe da página atual: (R*2) + M
                # R=0, M=0 -> Classe 0
                # R=0, M=1 -> Classe 1
                # R=1, M=0 -> Classe 2
                # R=1, M=1 -> Classe 3
                current_page_class = (r * 2) + m
                
                if current_page_class == priority_class:
                    victim_idx = curr_idx
                    found = True
                    break
            
            if found:
                break # Encontrou a menor classe possível, para a busca

        # Substitui a página encontrada
        self.memory[victim_idx] = page_id
        self.r_bits[victim_idx] = 1
        self.m_bits[victim_idx] = 1 if is_write else 0
        
        # Atualiza o ponteiro para a posição seguinte à substituição
        self.pointer = (victim_idx + 1) % self.capacity
        
        return False