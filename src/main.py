#!/usr/bin/env python3
"""
Punto de entrada principal del programa.
Responde a las Preguntas 1, 2 y 4.
"""
import sys
import os
import argparse
from typing import List, Optional

# Añadir el directorio padre al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.io.io_handler import leer_archivo, formatear_salida
from src.core.ida_star import IDAStar
from src.core.heuristics import get_heuristic, get_heuristic_name, HEURISTICS
from src.core.board import Board


def print_header():
    """Imprime encabezado del programa."""
    print("=" * 70)
    print("IDA* SOLVER PARA SLIDING PUZZLE")
    print("=" * 70)
    print()


def print_solution(movements: Optional[List[str]], stats: dict, elapsed: float):
    """
    Imprime la solución en consola.

    Args:
        movements: Lista de movimientos o None si no hay solución
        stats: Diccionario con estadísticas
        elapsed: Tiempo transcurrido
    """
    if movements is None:
        print("\nNO SE ENCONTRO SOLUCION")
    else:
        output = formatear_salida(movements)
        print(f"\nSOLUCION ENCONTRADA")
        print(f"   Movimientos: {output}")

    print("\nESTADISTICAS:")
    print(f"   Tiempo de ejecucion: {elapsed:.4f} segundos")
    print(f"   Nodos expandidos: {stats['nodes_expanded']}")
    print(f"   Profundidad maxima alcanzada: {stats['max_depth']}")
    print(f"   Longitud de la solucion: {stats['solution_length']}")
    print(f"   Heuristica utilizada: {stats['heuristic']}")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='IDA* Solver para Sliding Puzzle')
    parser.add_argument('archivo', help='Archivo de entrada con los tableros')
    parser.add_argument('-H', '--heuristica',
                        choices=list(HEURISTICS.keys()) + ['all'],
                        default='2', help='Heuristica a utilizar (1-5, o "all" para combinar todas)')
    parser.add_argument('-t', '--timeout', type=int, default=300,
                        help='Tiempo maximo de ejecucion en segundos (Por defecto: 300s = 5min)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Modo verbose (muestra detalles)')

    args = parser.parse_args()

    print_header()

    # Leer archivo
    #print(f"Leyendo archivo: {args.archivo}")
    dimension, start_board, goal_board = leer_archivo(args.archivo)

    if start_board is None or goal_board is None:
        print("Error al leer el archivo. Abortando.")
        sys.exit(1)

    print(f"\nTablero {dimension}x{dimension}")
    if args.verbose:
        print("\nEstado inicial:")
        print(start_board)
        print("\nEstado objetivo:")
        print(goal_board)

    # Configurar heurística(s)
    if args.heuristica == 'all':
        heuristic_func = [func for _, func, _, _ in HEURISTICS.values()]
        heuristic_name = "Combinacion de todas (Maximo)"
    else:
        heuristic_func = get_heuristic(args.heuristica)
        heuristic_name = get_heuristic_name(heuristic_func)

    print(f"\nHeuristica(s) seleccionada(s): {heuristic_name}")

    # Crear solver
    solver = IDAStar(heuristic_func, goal_board, usar_nodo_cc=False)

    # Resolver
    print("\nBuscando solucion...")
    movements = solver.search(start_board, max_time=args.timeout)
    elapsed = time.time() - solver.start_time if hasattr(solver, 'start_time') else 0.0

    stats = solver.get_statistics()
    print_solution(movements, stats, elapsed)


if __name__ == "__main__":
    import time  # necesario para elapsed
    main()