import argparse
import sys
import time
from algorithms import FIFO, LRU, OTIMO, SECONDCHANCE, CLOCK, NRU, LFU, MFU 

def run_comparison_table(references):
    """
    Roda todos os algoritmos para 3 e 4 frames e imprime a tabela
    """
    algorithms_list = ['FIFO', 'LRU', 'OTIMO', 'CLOCK', 'SC', 'NRU', 'LFU', 'MFU']
    frame_options = [3, 4]

    # Cabeçalho da tabela
    print(f"{'Page Faults':<20} | {'3 Frames':<20} | {'4 Frames':<20} |")
    print("-" * 68)

    for algo_name in algorithms_list:
        results = []
        
        for num_frames in frame_options:
            
            # Instanciação
            if algo_name == 'FIFO':
                simulator = FIFO(num_frames)
            elif algo_name == 'LRU':
                simulator = LRU(num_frames)
            elif algo_name == 'OTIMO':
                simulator = OTIMO(num_frames, references)
            elif algo_name == 'CLOCK':
                simulator = CLOCK(num_frames)
            elif algo_name == 'SC':
                simulator = SECONDCHANCE(num_frames)
            elif algo_name == 'NRU':
                simulator = NRU(num_frames)
            elif algo_name == 'LFU':
                simulator = LFU(num_frames) 
            elif algo_name == 'MFU':
                simulator = MFU(num_frames)
            
            # --- Execução Silenciosa ---
            for page in references:
                simulator.access(page)
            
            # Guarda o resultado de faltas de página
            results.append(simulator.page_faults)
        
        # Imprime a linha da tabela
        # results[0] é para 3 frames, results[1] é para 4 frames
        print(f"{algo_name:<20} | {results[0]:<20} | {results[1]:<20} |")

def run_visual_simulation(simulator, references):
    """
    Imprime o passo a passo da memória.
    Substitui -1 por '_' .
    """
    print(f"Simulação Visual: {type(simulator).__name__} ({simulator.capacity} Frames)")
    print(f"{'Ref':<5} | {'Status':<10} | {'Memória'}")
    print("-" * 40)

    for page in references:
        # O método access retorna True (Está na memoria) ou False (Não está na memória)
        is_hit = simulator.access(page)
        
        status = " " if is_hit else "X"
        
        # Formata a memória: troca -1 por um sublinhado visual
        mem_str = "[ " + " ".join(str(p) if p != -1 else "_" for p in simulator.memory) + " ]"
        
        # Imprime a linha
        print(f"{page:<5} | {status:<10} | {mem_str}")
    
    print("-" * 40)
    print(f"Total Faltas: {simulator.page_faults}")

def main():
    #CONFIGURAÇÃO DO ARGPARSE
    parser = argparse.ArgumentParser(description='Simulador de Algoritmos de Substituição de Páginas')
    
    # --algo, --frames e --trace
    # flag -> atributo
    parser.add_argument('--algo', required=True, help='O algoritmo a ser usado (FIFO, LRU, OTIMO, etc.)')
    parser.add_argument('--frames', type=int, required=True, help='A quantidade de molduras de memória (ex: 3 ou 4)')
    parser.add_argument('--trace', required=True, help='Caminho do arquivo com a sequência de páginas')
    parser.add_argument('--visual', action='store_true', help='Exibe execução passo a passo em vez do resumo')
    args = parser.parse_args()

    # LEITURA DO ARQUIVO
    try:
        with open(args.trace, 'r') as f:
            references = [int(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Erro: O arquivo '{args.trace}' não foi encontrado.")
        sys.exit(1)
    except ValueError:
        print("Erro: O arquivo de trace deve conter apenas números inteiros.")
        sys.exit(1)

    # TABELA
    if args.algo.upper() == 'ALL':
        run_comparison_table(references)
        sys.exit(0) # Encerra o programa após imprimir a tabela

    # SELEÇÃO DO ALGORITMO
    algo_name = args.algo.upper()
    simulator = None
    
    if algo_name == 'FIFO':
        simulator = FIFO(args.frames)
    elif algo_name == 'LRU':
        simulator = LRU(args.frames)
    elif algo_name == 'OTIMO':       
        simulator = OTIMO(args.frames, references)
    elif algo_name == 'SEGUNDACHANCE':       
        simulator = SECONDCHANCE(args.frames)
    elif algo_name == 'CLOCK':       
        simulator = CLOCK(args.frames)
    elif algo_name == 'NRU':       
        simulator = NRU(args.frames)
    elif algo_name == 'LFU':
        simulator = LFU(args.frames) 
    elif algo_name == 'MFU':
        simulator = MFU(args.frames)
    else:
        print(f"Erro: O algoritmo '{algo_name}' ainda não foi implementado.")
        sys.exit(1)

    #PASSO A PASSO
    if args.visual:
        run_visual_simulation(simulator, references)
        sys.exit(0)

    # LOOP DE SIMULAÇÃO PADRAO
    print(f"Executando {algo_name} com {args.frames} frames...")
    
    start_time = time.perf_counter_ns()

    for page in references:
        simulator.access(page)
    
    end_time = time.perf_counter_ns()
    duration_ms = (end_time - start_time)

    # EXIBIÇÃO DOS RESULTADOS
    total_refs = len(references)
    taxa = (simulator.page_faults / total_refs) * 100

    print("-" * 30)
    print(f"Algoritmo: {algo_name}")
    print(f"Frames: {args.frames}")
    print(f"Referências: {total_refs}")
    print(f"Faltas de página: {simulator.page_faults}")
    print(f"Taxa de faltas: {taxa:.2f}%")
    print(f"Evicções: {simulator.evictions}")
    print("Conjunto residente final:")
    
    # Imprime os IDs dos frames
    print("frame_ids: ", end="")
    valid_frames = [str(i) for i, page in enumerate(simulator.memory) if page != -1]
    print(" ".join(valid_frames))

    # Imprime as páginas correspondentes na mesma ordem física
    print("page_ids:  ", end="")
    valid_pages = [str(page) for page in simulator.memory if page != -1]
    print(" ".join(valid_pages))
    print(f"Tempo de execução: {duration_ms:.4f} ns")
    print("-" * 30)


if __name__ == "__main__":
    main()