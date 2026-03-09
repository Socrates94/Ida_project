#!/usr/bin/env python3
# experiments/run_all.py
"""
Script maestro que ejecuta todo el pipeline experimental:
1. Genera instancias (si no existen)
2. Ejecuta experimentos
3. Genera analisis y graficas
"""
import os
import sys
import time
from datetime import datetime

# Añadir directorio raiz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from experiments.generator import generar_todas_las_instancias
from experiments.runner import ExperimentRunner
from experiments.analyzer import ExperimentAnalyzer


def run_complete_experiment(heuristic_key='2', timeout=300, regenerate=False):
    """
    Ejecuta el experimento completo.

    Args:
        heuristic_key: Heuristica a usar
        timeout: Timeout por instancia
        regenerate: Si True, regenera instancias aunque existan
    """
    print("=" * 80)
    print("EXPERIMENTO COMPLETO - IDA* SLIDING PUZZLE")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Heuristica: {heuristic_key}")
    print(f"Timeout: {timeout}s")
    print("=" * 80)

    start_time = time.time()

    # =========================================================
    # PASO 1: Verificar/Generar instancias
    # =========================================================
    instances_dir = 'data/instances'

    if regenerate or not os.path.exists(instances_dir):
        print("\nGenerando instancias...")
        generar_todas_las_instancias()
    else:
        print("\nUsando instancias existentes en data/instances/")

    # =========================================================
    # PASO 2: Ejecutar experimentos
    # =========================================================
    print("\nEjecutando experimentos...")
    runner = ExperimentRunner(heuristic_key=heuristic_key, timeout=timeout)
    results, output_file = runner.run_all_difficulties()

    # =========================================================
    # PASO 3: Generar analisis
    # =========================================================
    print("\nGenerando analisis y graficas...")
    analyzer = ExperimentAnalyzer(output_file)
    analyzer.generar_todas_graficas()

    # =========================================================
    # RESUMEN FINAL
    # =========================================================
    total_time = time.time() - start_time

    print("\n" + "=" * 80)
    print("EXPERIMENTO COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    print(f"Tiempo total: {total_time / 60:.2f} minutos")
    print(f"Resultados: {output_file}")
    print(f"Graficas: data/results/plots/")
    print(f"Reporte: data/results/reporte.html")
    print("=" * 80)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Ejecutar experimento completo')
    parser.add_argument('--heuristica', type=str, default='2',
                        choices=['1', '2', '3', '4', '5'],
                        help='Heuristica a usar (1=Hamming, 2=Manhattan, 3=Linear, 4=Corner, 5=Fila)')
    parser.add_argument('--timeout', type=int, default=300,
                        help='Timeout por instancia (segundos)')
    parser.add_argument('--regenerate', action='store_true',
                        help='Regenerar instancias aunque existan')

    args = parser.parse_args()

    run_complete_experiment(
        heuristic_key=args.heuristica,
        timeout=args.timeout,
        regenerate=args.regenerate
    )


if __name__ == '__main__':
    main()