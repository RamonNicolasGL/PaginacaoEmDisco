import argparse
import sys
import time
# AQUI ESTÁ A MÁGICA: Importamos a classe do outro arquivo
from algorithms import FIFO, LRU, OTIMO, SECONDCHANCE, CLOCK, NRU 

def main():
    # --- CONFIGURAÇÃO DO ARGPARSE ---
    parser = argparse.ArgumentParser(description='Simulador de Algoritmos de Substituição de Páginas')
    
    # Define que o usuário DEVE passar --algo, --frames e --trace
    # Cada flag vira um atributo
    parser.add_argument('--algo', required=True, help='O algoritmo a ser usado (FIFO, LRU, OTIMO, etc.)')
    parser.add_argument('--frames', type=int, required=True, help='A quantidade de molduras de memória (ex: 3 ou 4)')
    parser.add_argument('--trace', required=True, help='Caminho do arquivo com a sequência de páginas')

    # Processa os argumentos. Se algo estiver errado, o script para aqui e avisa o usuário.
    args = parser.parse_args()

    # --- LEITURA DO ARQUIVO ---
    try:
        with open(args.trace, 'r') as f:
            references = [int(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Erro: O arquivo '{args.trace}' não foi encontrado.")
        sys.exit(1)
    except ValueError:
        print("Erro: O arquivo de trace deve conter apenas números inteiros.")
        sys.exit(1)

    # --- SELEÇÃO DO ALGORITMO ---
    algo_name = args.algo.upper()
    simulator = None
    print(args.algo)
    print(args.trace)
    print(args.frames)
    
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
    else:
        print(f"Erro: O algoritmo '{algo_name}' ainda não foi implementado.")
        sys.exit(1)

    # --- LOOP DE SIMULAÇÃO ---
    print(f"Executando {algo_name} com {args.frames} frames...")
    
    start_time = time.perf_counter_ns()

    for page in references:
        simulator.access(page)
    
    end_time = time.perf_counter_ns()
    duration_ms = (end_time - start_time)

    # --- EXIBIÇÃO DOS RESULTADOS [cite: 55-69] ---
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
    
    # Imprime os IDs dos frames (0, 1, 2...)
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