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

from src.io.io_handler import read_puzzle_file, format_movements_output
from src.core.ida_star import IDAStar
from src.core.heuristics import HEURISTICS, get_heuristic
from src.config import get_config, update_config


def print_header():
    """Imprime encabezado del programa."""
    print("=" * 70)
    print("IDA* SOLVER PARA SLIDING PUZZLE")
    print("=" * 70)
    print("Inteligencia Artificial - Primer Parcial")
    print()


def print_solution(movements: Optional[List[str]], stats: dict):
    """
    Imprime la solución en consola.

    Args:
        movements: Lista de movimientos o None si no hay solución
        stats: Diccionario con estadísticas
    """
    if movements is None:
        print("\n❌ NO SE ENCONTRÓ SOLUCIÓN")
    else:
        output = format_movements_output(movements)
        print(f"\n✅ SOLUCIÓN ENCONTRADA")
        print(f"   Movimientos: {output}")

    print("\n📊 ESTADÍSTICAS:")
    print(f"   • Tiempo de ejecución: {stats['tiempo']:.4f} segundos")
    print(f"   • Nodos expandidos: {stats['nodos']}")
    print(f"   • Profundidad de la solución: {stats['profundidad']}")
    print(f"   • Heurística utilizada: {stats['heuristica']}")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='IDA* Solver para Sliding Puzzle')
    parser.add_argument('archivo', help='Archivo de entrada con los tableros')
    parser.add_argument('-H', '--heuristica',
                        choices=list(HEURISTICS.keys()) + [name for name, _, _ in HEURISTICS.values()],
                        default='1', help='Heurística a utilizar (1-5 o nombre)')
    parser.add_argument('-t', '--timeout', type=int, default=None,
                        help='Tiempo máximo de ejecución en segundos')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Modo verbose (muestra detalles)')

    args = parser.parse_args()

    print_header()

    # Leer archivo
    print(f"📁 Leyendo archivo: {args.archivo}")
    dimension, start_board, goal_board = read_puzzle_file(args.archivo)

    if start_board is None or goal_board is None:
        print("❌ Error al leer el archivo. Abortando.")
        sys.exit(1)

    print(f"\n📋 Tablero {dimension}x{dimension}")
    print("\nEstado inicial:")
    print(start_board)
    print("\nEstado objetivo:")
    print(goal_board)

    # Configurar heurística
    heuristic_func = get_heuristic(args.heuristica)
    heuristica_nombre = "Desconocida"
    for key, (name, func, _) in HEURISTICS.items():
        if func == heuristic_func:
            heuristica_nombre = name
            break

    print(f"\n🧠 Heurística seleccionada: {heuristica_nombre}")

    # Configurar timeout si se especificó
    if args.timeout:
        update_config('timeout', args.timeout)
        print(f"⏱️  Timeout: {args.timeout} segundos")

    # Resolver
    print("\n🔍 Buscando solución...")

    solver = IDAStar(heuristic_func)
    movements, elapsed, nodes, depth = solver.search(start_board, goal_board)

