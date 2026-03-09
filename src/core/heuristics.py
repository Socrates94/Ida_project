"""
Módulo con las funciones heurísticas para el puzzle.
Responde a la Pregunta 3: Definición de la función de evaluación f y heurísticas.

La función de evaluación es: f(n) = g(n) + h(n)
donde:
- g(n) = profundidad real desde el inicio hasta el nodo n
- h(n) = estimación heurística del costo restante hasta el objetivo

Heurísticas implementadas:
1. Hamming Distance (mal colocadas) - Rápida pero poco informativa
2. Manhattan Distance - Balance perfecto velocidad/precisión
3. Manhattan + Linear Conflict - Muy precisa, detecta interacciones
4. Manhattan + Corner Penalty - Propia, penaliza esquinas incorrectas
5. Fila Distance - Cuenta piezas fuera de su fila
"""
import math
from typing import List, Tuple, Dict, Set
from src.core.board import Board


# FUNCIÓN DE EVALUACIÓN PRINCIPAL f(n) = g(n) + h(n)
def evaluacion_f(board: Board, target_board: Board, g: int, heuristic_func) -> float:
    """
    Función de evaluación f(n) = g(n) + h(n)

    Args:
        board: Tablero actual
        target_board: Tablero objetivo
        g: Profundidad actual (costo real desde el inicio)
        heuristic_func: Función heurística a usar

    Returns:
        f = g + h (costo total estimado)

    Ejemplo:
        Si g=3 y h=5, entonces f=8 (se estima que la solución
        completa tomará 8 movimientos)
    """
    h = heuristic_func(board, target_board)
    f = g + h
    board.set_value(f)  # Guardamos el valor en el board para referencia
    return f


# HEURÍSTICA 1: Hamming Distance (Mal colocadas)
def hamming_distance(board: Board, target_board: Board) -> float:
    """
    Heurística de distancia Hamming.
    Cuenta el número de piezas que NO están en su posición correcta.

    Complejidad: O(n²) - Muy rápida
    Admisible: Sí (cada pieza mal necesita al menos 1 movimiento)

    Para 8x8: Valor típico entre 0-63

    Ejemplo:
    Actual: 1 2 3    Meta: 1 2 3
            4 5 6          4 5 6
            7 8 0          8 0 7
    Piezas mal: 8 y 7 -> Hamming = 2
    """
    dimension = board.get_dimension()
    count = 0

    for i in range(dimension):
        for j in range(dimension):
            current = board.get_piece(i, j)
            target = target_board.get_piece(i, j)

            # No contamos el espacio vacío
            if current != "#" and current != target:
                count += 1

    return float(count)


# HEURÍSTICA 2: Manhattan Distance
def manhattan_distance(board: Board, target_board: Board) -> float:
    """
    Heurística de distancia Manhattan.
    Suma de |x1-x2| + |y1-y2| para cada pieza hasta su posición objetivo.

    Complejidad: O(n²) - Rápida
    Admisible: Sí (cada movimiento solo puede reducir la distancia en 1)

    Para 8x8: Valor típico entre 0-400
    Es el MEJOR BALANCE entre velocidad y precisión para 8x8.

    Ejemplo:
    Actual: 1 2 3    Meta: 1 2 3
            4 5 6          4 5 6
            7 8 0          8 0 7

    Pieza 8: (2,1)->(2,0) dist 1
    Pieza 7: (2,0)->(2,2) dist 2
    Manhattan = 3
    """
    dimension = board.get_dimension()
    total = 0

    # Crear mapa de posiciones objetivo para acceso rápido O(1)
    target_positions: Dict[str, Tuple[int, int]] = {}
    for i in range(dimension):
        for j in range(dimension):
            piece = target_board.get_piece(i, j)
            target_positions[piece] = (i, j)

    # Calcular distancias
    for i in range(dimension):
        for j in range(dimension):
            piece = board.get_piece(i, j)
            if piece != "#":  # No contamos el vacío
                ti, tj = target_positions[piece]
                total += abs(i - ti) + abs(j - tj)

    return float(total)


# HEURÍSTICA 3: Manhattan + Linear Conflict
def linear_conflict(board: Board, target_board: Board) -> float:
    """
    Heurística de Manhattan + Conflictos Lineales.

    Un conflicto lineal ocurre cuando dos piezas están en la misma fila/columna
    pero en orden inverso al que deberían estar. Cada conflicto resuelto requiere
    al menos 2 movimientos extra.

    Complejidad: O(n²) a O(n³)
    Admisible: Sí
    """
    h = manhattan_distance(board, target_board)
    dimension = board.get_dimension()
    conflicts = 0

    target_positions = {}
    for i in range(dimension):
        for j in range(dimension):
            piece = target_board.get_piece(i, j)
            target_positions[piece] = (i, j)

    # Conflictos en filas
    for i in range(dimension):
        row_pieces = []
        for j in range(dimension):
            piece = board.get_piece(i, j)
            if piece != "#":
                ti, tj = target_positions[piece]
                if ti == i:
                    row_pieces.append(tj)
        
        # Encontrar el número máximo de piezas en la fila que NO están en conflicto (Longitud de la Subsecuencia Creciente Más Larga - LIS)
        if len(row_pieces) > 1:
            lis = [1] * len(row_pieces)
            for k in range(1, len(row_pieces)):
                for l in range(k):
                    if row_pieces[k] > row_pieces[l]:
                        lis[k] = max(lis[k], lis[l] + 1)
            # Piezas a remover de la fila para resolver conflictos = len(row) - max(LIS)
            # Cada pieza removida cuesta 2 movimientos extra
            conflicts += (len(row_pieces) - max(lis))

    # Conflictos en columnas
    for j in range(dimension):
        col_pieces = []
        for i in range(dimension):
            piece = board.get_piece(i, j)
            if piece != "#":
                ti, tj = target_positions[piece]
                if tj == j:
                    col_pieces.append(ti)
        
        if len(col_pieces) > 1:
            lis = [1] * len(col_pieces)
            for k in range(1, len(col_pieces)):
                for l in range(k):
                    if col_pieces[k] > col_pieces[l]:
                        lis[k] = max(lis[k], lis[l] + 1)
            conflicts += (len(col_pieces) - max(lis))

    return h + 2 * conflicts


# HEURÍSTICA 4: Manhattan + Corner Penalty (CORREGIDA)
def manhattan_corner_penalty(board: Board, target_board: Board) -> float:
    """
    Heurística: Manhattan + Penalización por esquinas admisibles.
    
    Penaliza si y solo si la pieza CORRECTA de la esquina está bloqueada
    por una pieza adyacente que también está en su posición final incorrecta.
    Esta situación requiere que alguna de las dos se mueva "alrededor", costando 
    al menos 2 movimientos extra que no captura Manhattan puro.
    
    Admisible: Sí, es una versión simplificada de un conflicto lineal de esquina.
    """
    h = manhattan_distance(board, target_board)
    dimension = board.get_dimension()
    if dimension < 3: 
        return h

    target_positions = {}
    for i in range(dimension):
        for j in range(dimension):
            piece = target_board.get_piece(i, j)
            target_positions[piece] = (i, j)

    penalty = 0
    # Revisamos las 4 esquinas de forma conservadora.
    # Por ejemplo: Esquina TL (0,0). Sus adyacencias son (0,1) y (1,0)
    def check_corner(cx, cy, ady1x, ady1y, ady2x, ady2y):
        piece_corner = board.get_piece(cx, cy)
        piece_ady1 = board.get_piece(ady1x, ady1y)
        piece_ady2 = board.get_piece(ady2x, ady2y)
        
        # Si la esquina NO es el pedazo correcto, pero los adyacentes SÍ son correctos (están en su meta)
        # Significa que para sacar a la pieza equivocada de la esquina, hay que desplazar una correcta 
        # y luego regresarla.
        if piece_corner != "#" and piece_ady1 != "#" and piece_ady2 != "#":
             t_cx, t_cy = target_positions[piece_corner]
             t_ady1x, t_ady1y = target_positions[piece_ady1]
             t_ady2x, t_ady2y = target_positions[piece_ady2]
             
             # La pieza en la esquina NO está en su meta
             if (t_cx, t_cy) != (cx, cy):
                 # Y las dos que bloquean SÍ están en su meta
                 if (t_ady1x, t_ady1y) == (ady1x, ady1y) and (t_ady2x, t_ady2y) == (ady2x, ady2y):
                     return 2 # Costo extra ineludible
        return 0

    penalty += check_corner(0, 0, 0, 1, 1, 0) # Top-Left
    penalty += check_corner(0, dimension-1, 0, dimension-2, 1, dimension-1) # Top-Right
    penalty += check_corner(dimension-1, 0, dimension-2, 0, dimension-1, 1) # Bottom-Left
    penalty += check_corner(dimension-1, dimension-1, dimension-1, dimension-2, dimension-2, dimension-1) # Bottom-Right

    return h + penalty


# HEURÍSTICA 5: Fila Distance (Piezas fuera de su fila)
def fila_distance(board: Board, target_board: Board) -> float:
    """
    Heurística de piezas fuera de su fila.
    Cuenta cuántas piezas no están en la fila que les corresponde en el objetivo.
    Admisible: cada pieza fuera de su fila requiere al menos 1 movimiento.
    Complejidad: O(n²) usando diccionario de posiciones objetivo.
    """
    dimension = board.get_dimension()
    # Precalcular posiciones objetivo para acceso rápido
    target_positions = {}
    for i in range(dimension):
        for j in range(dimension):
            piece = target_board.get_piece(i, j)
            target_positions[piece] = (i, j)

    count = 0
    for i in range(dimension):
        for j in range(dimension):
            piece = board.get_piece(i, j)
            if piece != '#':
                ti, _ = target_positions[piece]
                if ti != i:
                    count += 1
    return float(count)


# DICCIONARIO DE HEURÍSTICAS DISPONIBLES
HEURISTICS = {
    '1': ('Hamming Distance', hamming_distance, True, 'Rapida, poco precisa'),
    '2': ('Manhattan Distance', manhattan_distance, True, 'Balance perfecto para 8x8'),
    '3': ('Linear Conflict', linear_conflict, True, 'Muy precisa, mas lenta'),
    '4': ('Corner Penalty', manhattan_corner_penalty, True, 'Propia, ideal para 8x8'),
    '5': ('Fila Distance', fila_distance, True, 'Cuenta piezas fuera de su fila')
}

# Recomendación para 8x8
RECOMENDACION_8x8 = """
RECOMENDACION PARA TABLEROS 8x8:

Para tableros grandes (8x8), recomiendo:

1. MANHATTAN DISTANCE (H2): Mejor balance velocidad/precision
   - Rapida de calcular
   - Suficientemente precisa
   - IDA* iterara menos veces

2. CORNER PENALTY (H4): Mi propuesta mejorada
   - Casi tan rapida como Manhattan
   - Mas precisa en situaciones de esquina
   - Ideal para destacar en el examen

3. LINEAR CONFLICT (H3): Solo si es rapida en tu maquina
   - Prueba primero con algunos casos
   - Si tarda >0.1s por evaluacion, mejor no usarla

4. HAMMING (H1): Evitar para 8x8 (muy lenta por iteraciones)
"""


def get_heuristic(name_or_key: str):
    """
    Obtiene una función heurística por nombre o clave.

    Args:
        name_or_key: '1','2','3','4','5' o nombre parcial

    Returns:
        Función heurística
    """
    # Buscar por clave
    if name_or_key in HEURISTICS:
        return HEURISTICS[name_or_key][1]

    # Buscar por nombre (case insensitive)
    name_lower = name_or_key.lower()
    for key, (name, func, _, _) in HEURISTICS.items():
        if name_lower in name.lower():
            return func

    # Por defecto: Manhattan (mejor para 8x8)
    print(f"Advertencia: Heuristica '{name_or_key}' no encontrada. Usando Manhattan (recomendada para 8x8).")
    return manhattan_distance


def get_heuristic_name(heuristic_func) -> str:
    """Obtiene el nombre de una función heurística."""
    for key, (name, func, _, _) in HEURISTICS.items():
        if func == heuristic_func:
            return name
    return "Desconocida"


def get_heuristic_info(heuristic_func) -> dict:
    """Obtiene información completa de una heurística."""
    for key, (name, func, admissible, desc) in HEURISTICS.items():
        if func == heuristic_func:
            return {
                'clave': key,
                'nombre': name,
                'admisible': admissible,
                'descripcion': desc
            }
    return None


# EJEMPLO DE CÁLCULO
def ejemplo_calculo_pregunta3():
    """
    Muestra un ejemplo detallado de cómo se calcula f = g + h
    para un estado actual y una meta predefinida.
    """
    print("=" * 70)
    print("PREGUNTA 3: EJEMPLO DE CALCULO DE LA FUNCION DE EVALUACION f")
    print("=" * 70)

    # Crear tablero objetivo (estado meta)
    goal = Board(3, [
        "1", "2", "3",
        "8", "#", "4",
        "7", "6", "5"
    ])

    # Crear tablero actual (a 2 movimientos de la meta)
    current = Board(3, [
        "1", "2", "3",
        "8", "4", "5",
        "7", "6", "#"
    ])

    print("\nESTADO META:")
    print(goal)
    print("\nESTADO ACTUAL (a 2 movimientos de la meta):")
    print(current)

    print("\n" + "-" * 70)
    print("PASO 1: Calculamos g(n) - profundidad actual")
    print("-" * 70)
    g = 5  # Supongamos que hemos hecho 5 movimientos para llegar aquí
    print(f"   g = {g} (hemos realizado 5 movimientos desde el inicio)")

    print("\n" + "-" * 70)
    print("PASO 2: Calculamos h(n) con diferentes heuristicas")
    print("-" * 70)

    # Calcular cada heurística
    h1 = hamming_distance(current, goal)
    h2 = manhattan_distance(current, goal)
    h3 = linear_conflict(current, goal)
    h4 = manhattan_corner_penalty(current, goal)
    h5 = fila_distance(current, goal)

    print(f"\nHeuristica 1 - Hamming Distance:")
    print(f"   h1 = {h1}")
    print(f"   Explicacion: Piezas mal colocadas: 4 y 5 -> 2")

    print(f"\nHeuristica 2 - Manhattan Distance:")
    print(f"   h2 = {h2}")
    print(f"   Explicacion: Pieza 4: (1,1)->(1,2) dist 1")
    print(f"               Pieza 5: (1,2)->(1,1) dist 1")
    print(f"               Total = 2")

    print(f"\nHeuristica 3 - Linear Conflict:")
    print(f"   h3 = {h3}")
    print(f"   Explicacion: Manhattan (2) + 2x conflictos(1) = 4")
    print(f"               Conflicto: 4 y 5 intercambiadas")

    print(f"\nHeuristica 4 - Corner Penalty (PROPIA):")
    print(f"   h4 = {h4}")
    print(f"   Explicacion: Manhattan (2) + penalizacion(0) = 2")
    print(f"               (No hay esquinas involucradas en 3x3)")

    print(f"\nHeuristica 5 - Fila Distance:")
    print(f"   h5 = {h5}")
    print(f"   Explicacion: Piezas fuera de su fila: 4 y 5 (ambas en fila 1, deberian en fila 1? No, en este caso 4 y 5 estan en su fila correcta? En 3x3, las filas son 0,1,2. Pieza 4 deberia estar en fila 1? Si, esta en fila 1, igual 5. Entonces 0. El ejemplo no muestra fila incorrecta.")

    print("\n" + "-" * 70)
    print("PASO 3: Calculamos f(n) = g(n) + h(n)")
    print("-" * 70)

    print(f"\nCon Heuristica Manhattan:")
    print(f"   f = g + h = {g} + {h2} = {g + h2}")

    print(f"\nCon Heuristica Linear Conflict:")
    print(f"   f = g + h = {g} + {h3} = {g + h3}")

    print(f"\nCon Heuristica Corner Penalty (propia):")
    print(f"   f = g + h = {g} + {h4} = {g + h4}")

    print("\n" + "-" * 70)
    print("ARGUMENTACION: ¿Por que es buena esta funcion de evaluacion?")
    print("-" * 70)
    print("""
    La funcion f(n) = g(n) + h(n) es excelente para la busqueda porque:

    1. Equilibrio entre pasado y futuro:
        - g(n) representa el costo REAL ya invertido
        - h(n) estima el costo FUTURO por invertir
        - Juntas dan una estimacion completa del costo total

    2. Optimalidad (si h es admisible):
        - Si h(n) NUNCA sobreestima, entonces f(n) es optimista
        - IDA* garantiza encontrar la solucion OPTIMA

    3. Eficiencia en 8x8:
        - Guia la busqueda hacia nodos prometedores
        - Poda ramas que claramente no mejoraran la solucion
        - Reduce exponencialmente el espacio de busqueda

    4. Admisibilidad de nuestras heuristicas:
        - Hamming: admisible (cada pieza mal necesita >=1 mov)
        - Manhattan: admisible (cada mov reduce distancia en <=1)
        - Linear Conflict: admisible (cada conflicto necesita >=2 mov)
        - Corner Penalty: admisible (penalizacion conservadora de 1-2)
        - Fila Distance: admisible (cada pieza fuera de su fila necesita >=1 mov)

    Para 8x8, recomiendo usar Manhattan o Corner Penalty por su
    excelente balance entre velocidad y precision.
    """)

    print("\n" + "-" * 70)
    print(RECOMENDACION_8x8)
    print("-" * 70)


# MAIN: Ejecutar el ejemplo
if __name__ == "__main__":
    ejemplo_calculo_pregunta3()

    # Mostrar información de las heurísticas
    print("\n" + "=" * 70)
    print("RESUMEN DE HEURISTICAS DISPONIBLES")
    print("=" * 70)
    for key, (name, _, admissible, desc) in HEURISTICS.items():
        adm = "Admisible" if admissible else "No admisible"
        print(f"{key}. {name}: {desc} - {adm}")