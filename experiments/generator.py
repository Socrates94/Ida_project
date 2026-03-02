# experiments/generator.py
"""
Generador de instancias para el análisis empírico (Pregunta 5).
Crea tableros revolviendo el estado meta con N movimientos aleatorios.
"""
import os
import random
import copy
import sys

# Añadir el directorio padre al path para importar Board si es necesario
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def create_goal_board(n):
    """
    Crea el tablero meta para dimensión n.
    Ejemplo 3x3:
    1 2 3
    4 5 6
    7 8 0
    """
    board = []
    value = 1
    for i in range(n):
        row = []
        for j in range(n):
            if value == n * n:
                row.append(0)
            else:
                row.append(value)
            value += 1
        board.append(row)
    return board


def find_blank(board):
    """Encuentra la posición del 0 (espacio vacío)."""
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 0:
                return i, j
    return None


def get_valid_moves(board):
    """Obtiene movimientos válidos como (di, dj)."""
    n = len(board)
    i, j = find_blank(board)
    moves = []

    if i > 0:
        moves.append((-1, 0))  # up
    if i < n - 1:
        moves.append((1, 0))  # down
    if j > 0:
        moves.append((0, -1))  # left
    if j < n - 1:
        moves.append((0, 1))  # right

    return moves


def move_to_direction(move):
    """Convierte un movimiento (di, dj) a dirección U/D/L/R."""
    di, dj = move
    if di == -1:
        return 'U'
    elif di == 1:
        return 'D'
    elif dj == -1:
        return 'L'
    elif dj == 1:
        return 'R'
    return '?'


def apply_move(board, move):
    """Aplica un movimiento al tablero."""
    i, j = find_blank(board)
    di, dj = move
    new_i, new_j = i + di, j + dj

    new_board = copy.deepcopy(board)
    new_board[i][j], new_board[new_i][new_j] = (
        new_board[new_i][new_j],
        new_board[i][j],
    )
    return new_board


def scramble_board(goal_board, moves_count):
    """
    Revuelve el tablero meta aplicando moves_count movimientos aleatorios.
    Evita deshacer el movimiento anterior para mejor dispersión.
    """
    board = copy.deepcopy(goal_board)
    last_move = None
    moves_sequence = []  # Para registro

    for _ in range(moves_count):
        valid_moves = get_valid_moves(board)

        # Evitar deshacer el movimiento anterior
        if last_move:
            inverse = (-last_move[0], -last_move[1])
            if inverse in valid_moves:
                # Si hay otros movimientos, eliminar el inverso
                if len(valid_moves) > 1:
                    valid_moves.remove(inverse)
                # Si solo está el inverso, usarlo (no hay otra opción)

        move = random.choice(valid_moves)
        board = apply_move(board, move)
        moves_sequence.append(move_to_direction(move))
        last_move = move

    return board, moves_sequence


def save_instance(n, initial_board, goal_board, index, output_dir, metadata=None):
    """
    Guarda una instancia en un archivo con el formato requerido.

    Formato:
    - Línea 1: Dimensión n
    - Siguientes n líneas: Tablero inicial (números separados por comas)
    - Siguientes n líneas: Tablero meta (números separados por comas)
    """
    # Asegurar que el directorio existe
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{n}x{n}_case_{index:03d}.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding='utf-8') as f:
        f.write(f"{n}\n")

        # Tablero inicial
        for row in initial_board:
            f.write(",".join(map(str, row)) + "\n")

        # Tablero meta
        for row in goal_board:
            f.write(",".join(map(str, row)) + "\n")

        # Opcional: guardar metadatos como comentarios
        if metadata:
            f.write("\n# Movimientos aplicados: " + ",".join(metadata['moves']) + "\n")
            f.write(f"# Dificultad: {metadata['dificultad']}\n")

    return filepath


def generar_instancias(n, movimientos, cantidad, output_dir=None):
    """
    Genera múltiples instancias para un tamaño y dificultad dados.

    Args:
        n: Dimensión del tablero
        movimientos: Número de movimientos aleatorios para revolver
        cantidad: Cantidad de instancias a generar
        output_dir: Directorio de salida (por defecto: data/instances/{n}x{n}/)

    Returns:
        Lista de rutas a los archivos generados
    """
    if output_dir is None:
        output_dir = os.path.join("data", "instances", f"{n}x{n}")

    # Determinar dificultad para metadatos
    if movimientos <= 15:
        dificultad = "facil"
    elif movimientos <= 30:
        dificultad = "medio"
    else:
        dificultad = "dificil"

    goal_board = create_goal_board(n)
    archivos_generados = []

    for i in range(1, cantidad + 1):
        initial_board, moves_sequence = scramble_board(goal_board, movimientos)

        metadata = {
            'moves': moves_sequence,
            'dificultad': dificultad,
            'movimientos_aplicados': movimientos
        }

        filepath = save_instance(
            n, initial_board, goal_board, i, output_dir, metadata
        )
        archivos_generados.append(filepath)

        if i % 10 == 0:
            print(f"  Generadas {i}/{cantidad} instancias...")

    return archivos_generados


def generar_todas_las_instancias():
    """
    Genera todas las instancias para el análisis empírico:
    - Tamaños: 4x4, 5x5, 6x6, 7x7, 8x8
    - Dificultades: fácil (10), medio (20), difícil (50)
    - Cantidad: 100 por combinación
    """
    print("=" * 70)
    print("GENERADOR DE INSTANCIAS PARA ANÁLISIS EMPÍRICO")
    print("=" * 70)

    tamanios = [4, 5, 6, 7, 8]
    dificultades = {
        'facil': 10,
        'medio': 20,
        'dificil': 50
    }
    instancias_por_combinacion = 100

    total_instancias = len(tamanios) * len(dificultades) * instancias_por_combinacion
    print(f"\n📊 Configuración:")
    print(f"   • Tamaños: {tamanios}")
    print(f"   • Dificultades: {dificultades}")
    print(f"   • Instancias por combinación: {instancias_por_combinacion}")
    print(f"   • Total a generar: {total_instancias}")
    print()

    archivos_generados = []

    for n in tamanios:
        print(f"\n📋 Generando instancias para {n}x{n}:")

        for dificultad, movs in dificultades.items():
            print(f"  • Dificultad {dificultad} ({movs} movimientos)...")

            archivos = generar_instancias(
                n=n,
                movimientos=movs,
                cantidad=instancias_por_combinacion,
                output_dir=os.path.join("data", "instances", f"{n}x{n}", dificultad)
            )
            archivos_generados.extend(archivos)

    print("\n" + "=" * 70)
    print(f"✅ GENERACIÓN COMPLETADA")
    print(f"   Total de instancias: {len(archivos_generados)}")
    print(f"   Directorio base: data/instances/")
    print("=" * 70)

    return archivos_generados


def generar_instancia_ejemplo():
    """
    Genera una instancia de ejemplo en data/input/ejemplo.txt
    para pruebas rápidas con main.py
    """
    print("Generando instancia de ejemplo...")

    n = 4
    movimientos = 20

    goal_board = create_goal_board(n)
    initial_board, moves = scramble_board(goal_board, movimientos)

    output_dir = os.path.join("data", "input")
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, "ejemplo.txt")

    with open(filepath, "w", encoding='utf-8') as f:
        f.write(f"{n}\n")
        for row in initial_board:
            f.write(",".join(map(str, row)) + "\n")
        for row in goal_board:
            f.write(",".join(map(str, row)) + "\n")

    print(f"✅ Instancia de ejemplo guardada en: {filepath}")
    print(f"   Dimensión: {n}x{n}")
    print(f"   Movimientos aplicados: {','.join(moves[:10])}...")

    return filepath


def generar_tamano_especifico(n, movimientos, cantidad=1):
    """
    Genera instancias de un tamaño específico.

    Args:
        n: Dimensión del tablero (4,5,6,7,8)
        movimientos: Número de movimientos para revolver
        cantidad: Cantidad de instancias a generar
    """
    output_dir = os.path.join("data", "input", f"{n}x{n}")
    os.makedirs(output_dir, exist_ok=True)

    goal_board = create_goal_board(n)

    for i in range(1, cantidad + 1):
        initial_board, moves = scramble_board(goal_board, movimientos)

        filename = f"{n}x{n}_{movimientos}mov_{i:02d}.txt"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding='utf-8') as f:
            f.write(f"{n}\n")
            for row in initial_board:
                f.write(",".join(map(str, row)) + "\n")
            for row in goal_board:
                f.write(",".join(map(str, row)) + "\n")

        print(f"✅ Generado: {filename}")
        print(f"   Movimientos aplicados: {','.join(moves[:10])}...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generador de instancias para sliding puzzle')
    parser.add_argument('--modo', choices=['ejemplo', 'experimento', 'tamano'],
                        default='ejemplo', help='Modo de generación')
    parser.add_argument('--n', type=int, default=4, help='Tamaño del tablero (4-8)')
    parser.add_argument('--mov', type=int, default=20, help='Número de movimientos')
    parser.add_argument('--cant', type=int, default=1, help='Cantidad de instancias')

    args = parser.parse_args()

    if args.modo == 'ejemplo':
        generar_instancia_ejemplo()

    elif args.modo == 'experimento':
        generar_todas_las_instancias()

    elif args.modo == 'tamano':
        generar_tamano_especifico(args.n, args.mov, args.cant)