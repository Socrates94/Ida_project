# src/io/io_handler.py
"""
Módulo para manejo de entrada/salida de archivos.
Responde a la Pregunta 1: Interfaz de usuario con archivo.
"""
import os
import sys
from typing import Tuple, List, Optional

# Importación relativa para cuando se ejecuta desde src/
try:
    from src.core.board import Board
except ImportError:
    # Si falla, intentamos con ruta absoluta
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.core.board import Board


def leer_archivo(ruta_archivo: str) -> Tuple[Optional[int], Optional[Board], Optional[Board]]:
    """
    Lee un archivo con el formato especificado en el examen.

    Args:
        ruta_archivo: Ruta al archivo de entrada (ej: "data/input/5x5/5x5_10mov_01.txt")

    Returns:
        Tuple: (dimension, tablero_inicial, tablero_objetivo)
    """
    # Verificar que el archivo existe
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo '{ruta_archivo}' no existe")
        return None, None, None

    print(f"Leyendo archivo: {ruta_archivo}")

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            # Leer todas las líneas
            lineas = [linea.rstrip('\n') for linea in f.readlines()]

        # Filtrar líneas vacías y comentarios
        lineas_filtradas = []
        for linea in lineas:
            linea_strip = linea.strip()
            if linea_strip and not linea_strip.startswith('#'):
                lineas_filtradas.append(linea_strip)

        if not lineas_filtradas:
            print(f"Error: El archivo '{ruta_archivo}' no contiene datos válidos")
            return None, None, None

        # 1. Leer dimensión
        try:
            n = int(lineas_filtradas[0])
        except ValueError:
            print(f"Error: La primera línea debe ser un número entero, se encontró: '{lineas_filtradas[0]}'")
            return None, None, None

        print(f"Dimensión detectada: {n}x{n}")

        # 2. Verificar que tenemos suficientes líneas
        lineas_necesarias = 1 + 2 * n
        if len(lineas_filtradas) < lineas_necesarias:
            print(f"Error: Se esperaban {lineas_necesarias} líneas, se encontraron {len(lineas_filtradas)}")
            return None, None, None

        # 3. Función auxiliar para convertir línea a lista de piezas
        def linea_a_piezas(linea: str, num_fila: int) -> List[str]:
            partes = linea.split(',')

            if len(partes) != n:
                raise ValueError(f"Fila {num_fila} tiene {len(partes)} elementos, esperaba {n}")

            piezas = []
            for idx, p in enumerate(partes):
                p = p.strip()
                if not p:
                    raise ValueError(f"Elemento vacío en fila {num_fila}, posición {idx + 1}")

                try:
                    val = int(p)
                except ValueError:
                    raise ValueError(f"Valor no numérico '{p}' en fila {num_fila}")

                if val < 0 or val >= n * n:
                    raise ValueError(f"Número {val} fuera de rango (0-{n * n - 1}) en fila {num_fila}")

                # Convertir 0 a "#", otros números a string
                piezas.append("#" if val == 0 else str(val))

            return piezas

        # 4. Leer tablero inicial
        piezas_iniciales = []
        for i in range(n):
            linea = lineas_filtradas[1 + i]
            try:
                fila_piezas = linea_a_piezas(linea, i + 1)
                piezas_iniciales.extend(fila_piezas)
            except ValueError as e:
                print(f"Error en línea {1 + i + 1} (inicial): {e}")
                return None, None, None

        # 5. Leer tablero objetivo
        piezas_objetivo = []
        for i in range(n):
            linea = lineas_filtradas[1 + n + i]
            try:
                fila_piezas = linea_a_piezas(linea, i + 1)
                piezas_objetivo.extend(fila_piezas)
            except ValueError as e:
                print(f"Error en línea {1 + n + i + 1} (objetivo): {e}")
                return None, None, None

        # 6. Crear objetos Board
        tablero_inicial = Board(n, piezas_iniciales)
        tablero_objetivo = Board(n, piezas_objetivo)

        print("Archivo leído correctamente")
        return n, tablero_inicial, tablero_objetivo

    except Exception as e:
        print(f"Error inesperado: {e}")
        return None, None, None


def formatear_salida(movimientos: List[str]) -> str:
    """Formatea lista de movimientos como string separado por comas."""
    return ",".join(movimientos) if movimientos else ""


def mostrar_tableros(inicial: Board, objetivo: Board):
    """Muestra los tableros de forma legible."""
    print("\n" + "=" * 50)
    print("TABLERO INICIAL:")
    print("=" * 50)
    print(inicial)

    print("\n" + "=" * 50)
    print("TABLERO OBJETIVO:")
    print("=" * 50)
    print(objetivo)

    # Mostrar también en formato numérico
    print("\nFormato numérico (inicial):")
    for fila in inicial.to_movements_format():
        print(fila)


# Función principal para probar la lectura
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Probador de lectura de archivos')
    parser.add_argument('archivo', nargs='?',
                        default='data/input/ejemplo.txt',
                        help='Ruta al archivo de tablero a leer')

    args = parser.parse_args()

    print("=" * 60)
    print("PRUEBA DE LECTURA DE ARCHIVOS")
    print("=" * 60)

    # Leer el archivo
    n, inicial, objetivo = leer_archivo(args.archivo)

    if inicial and objetivo:
        mostrar_tableros(inicial, objetivo)
        print("\nPrueba exitosa: El archivo se leyó correctamente.")
    else:
        print("\nError al leer el archivo.")