# experiments/runner.py
"""
Ejecuta los experimentos masivos para el análisis empírico (Pregunta 5).
Lee las instancias generadas y ejecuta IDA* con diferentes configuraciones.
"""
import os
import sys
import time
import csv
from typing import List, Dict, Any
from datetime import datetime
import json

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ida_star import IDAStar
from src.core.heuristics import get_heuristic, get_heuristic_name, HEURISTICS
from src.io.io_handler import leer_archivo


class ExperimentRunner:
    """
    Ejecuta experimentos masivos sobre las instancias generadas.
    """

    def __init__(self, heuristic_key='2', timeout=300):
        """
        Inicializa el runner de experimentos.

        Args:
            heuristic_key: Clave de heurística a usar ('1','2','3','4')
            timeout: Tiempo máximo por instancia en segundos
        """
        self.heuristic_key = heuristic_key
        self.heuristic_func = get_heuristic(heuristic_key)
        self.heuristic_name = get_heuristic_name(self.heuristic_func)
        self.timeout = timeout
        self.results_dir = os.path.join('data', 'results', 'raw')
        os.makedirs(self.results_dir, exist_ok=True)

    def run_single_instance(self, filepath: str) -> Dict[str, Any]:
        """
        Ejecuta IDA* en una sola instancia.

        Returns:
            Diccionario con resultados
        """
        # Leer instancia
        n, start, goal = leer_archivo(filepath)

        if not start or not goal:
            return {
                'archivo': filepath,
                'tamano': 0,
                'exito': False,
                'error': 'No se pudo leer el archivo'
            }

        # Extraer metadatos del nombre del archivo
        filename = os.path.basename(filepath)
        partes = filename.replace('.txt', '').split('_')
        dificultad = 'desconocida'
        movimientos_iniciales = 0

        # Intentar extraer dificultad del path
        if 'facil' in filepath:
            dificultad = 'facil'
            movimientos_iniciales = 10
        elif 'medio' in filepath:
            dificultad = 'medio'
            movimientos_iniciales = 20
        elif 'dificil' in filepath:
            dificultad = 'dificil'
            movimientos_iniciales = 50

        # Ejecutar IDA*
        start_time = time.time()
        solver = IDAStar(heuristic_func=self.heuristic_func, max_time=self.timeout)

        try:
            moves, elapsed, nodes, depth = solver.search(start, goal)

            result = {
                'archivo': filename,
                'tamano': n,
                'dificultad': dificultad,
                'movimientos_iniciales': movimientos_iniciales,
                'exito': moves is not None,
                'tiempo_segundos': round(elapsed, 4),
                'nodos_expandidos': nodes,
                'profundidad_solucion': len(moves) if moves else 0,
                'movimientos': ','.join(moves) if moves else '',
                'heuristica': self.heuristic_name,
                'timeout': elapsed >= self.timeout if moves is None else False,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            result = {
                'archivo': filename,
                'tamano': n,
                'dificultad': dificultad,
                'movimientos_iniciales': movimientos_iniciales,
                'exito': False,
                'error': str(e),
                'tiempo_segundos': time.time() - start_time,
                'heuristica': self.heuristic_name,
                'timestamp': datetime.now().isoformat()
            }

        return result

    def run_batch(self, instances_dir: str, output_file: str = None):
        """
        Ejecuta experimentos sobre todas las instancias en un directorio.

        Args:
            instances_dir: Directorio con las instancias
            output_file: Archivo CSV de salida (opcional)

        Returns:
            Lista de resultados
        """
        if not os.path.exists(instances_dir):
            print(f"❌ Directorio no encontrado: {instances_dir}")
            return []

        # Buscar todos los archivos .txt
        instances = []
        for root, dirs, files in os.walk(instances_dir):
            for file in files:
                if file.endswith('.txt'):
                    instances.append(os.path.join(root, file))

        instances.sort()
        print(f"📊 Encontradas {len(instances)} instancias en {instances_dir}")

        if not instances:
            return []

        # Ejecutar experimentos
        results = []
        total = len(instances)

        for i, inst_path in enumerate(instances, 1):
            print(f"  [{i}/{total}] Procesando: {os.path.basename(inst_path)}")
            result = self.run_single_instance(inst_path)
            results.append(result)

            # Mostrar resultado rápido
            status = "✅" if result['exito'] else "❌"
            print(f"     {status} Tiempo: {result['tiempo_segundos']:.2f}s, "
                  f"Nodos: {result.get('nodos_expandidos', 0)}")

        # Guardar resultados
        if output_file:
            self._save_results(results, output_file)

        return results

    def run_all_difficulties(self, base_dir: str = 'data/instances'):
        """
        Ejecuta experimentos sobre todas las dificultades y tamaños.

        Args:
            base_dir: Directorio base de instancias
        """
        tamanios = ['4x4', '5x5', '6x6', '7x7', '8x8']
        dificultades = ['facil', 'medio', 'dificil']

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(
            self.results_dir,
            f'experimento_h{self.heuristic_key}_{timestamp}.csv'
        )

        all_results = []

        print("=" * 80)
        print(f"🧪 INICIANDO EXPERIMENTO MASIVO")
        print(f"   Heurística: {self.heuristic_name} (clave {self.heuristic_key})")
        print(f"   Timeout: {self.timeout}s por instancia")
        print(f"   Resultados: {output_file}")
        print("=" * 80)

        for tamano in tamanios:
            for dificultad in dificultades:
                instances_dir = os.path.join(base_dir, tamano, dificultad)

                if not os.path.exists(instances_dir):
                    print(f"\n⚠️  Directorio no encontrado: {instances_dir}")
                    continue

                print(f"\n📌 Procesando: {tamano} - {dificultad}")
                results = self.run_batch(instances_dir)
                all_results.extend(results)

        # Guardar todos los resultados
        self._save_results(all_results, output_file)

        print("\n" + "=" * 80)
        print(f"✅ EXPERIMENTO COMPLETADO")
        print(f"   Total instancias: {len(all_results)}")
        print(f"   Resultados guardados en: {output_file}")
        print("=" * 80)

        return all_results, output_file

    def _save_results(self, results: List[Dict], output_file: str):
        """Guarda resultados en CSV."""
        if not results:
            return

        # Definir campos
        fieldnames = [
            'archivo', 'tamano', 'dificultad', 'movimientos_iniciales',
            'exito', 'tiempo_segundos', 'nodos_expandidos',
            'profundidad_solucion', 'heuristica', 'timeout', 'error', 'timestamp'
        ]

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for r in results:
                # Filtrar solo campos existentes
                row = {k: r.get(k, '') for k in fieldnames}
                writer.writerow(row)

        print(f"💾 Resultados guardados: {output_file}")


def main():
    """Función principal para ejecutar experimentos."""
    import argparse

    parser = argparse.ArgumentParser(description='Ejecutar experimentos masivos')
    parser.add_argument('--heuristica', type=str, default='2',
                        choices=['1', '2', '3', '4'],
                        help='Heurística a usar (1=Hamming, 2=Manhattan, 3=Linear, 4=Corner)')
    parser.add_argument('--timeout', type=int, default=300,
                        help='Timeout por instancia en segundos')
    parser.add_argument('--modo', choices=['todo', 'resumen'], default='todo',
                        help='Modo de ejecución')

    args = parser.parse_args()

    runner = ExperimentRunner(
        heuristic_key=args.heuristica,
        timeout=args.timeout
    )

    if args.modo == 'todo':
        results, output_file = runner.run_all_difficulties()

        # Mostrar resumen rápido
        print("\n📊 RESUMEN RÁPIDO:")
        total = len(results)
        exitosos = sum(1 for r in results if r.get('exito', False))
        print(f"   Total: {total}")
        print(f"   Exitosos: {exitosos} ({exitosos / total * 100:.1f}%)")

    elif args.modo == 'resumen':
        # Aquí podríamos mostrar resumen de resultados existentes
        pass


if __name__ == '__main__':
    main()