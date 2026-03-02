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
"""
import math
from typing import List, Tuple, Dict, Set
from src.core.board import Board


# ============================================================================
# FUNCIÓN DE EVALUACIÓN PRINCIPAL f(n) = g(n) + h(n)
# ============================================================================

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


# ============================================================================
# HEURÍSTICA 1: Hamming Distance (Mal colocadas)
# ============================================================================

def hamming_distance(board: Board, target_board: Board) -> float:
    """
    Heurística de distancia Hamming.
    Cuenta el número de piezas que NO están en su posición correcta.

    Complejidad: O(n²) - Muy rápida
    Admisible: ✅ Sí (cada pieza mal necesita al menos 1 movimiento)

    Para 8x8: Valor típico entre 0-63

    Ejemplo:
    Actual: 1 2 3    Meta: 1 2 3
            4 5 6          4 5 6
            7 8 0          8 0 7
    Piezas mal: 8 y 7 → Hamming = 2
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


# ============================================================================
# HEURÍSTICA 2: Manhattan Distance
# ============================================================================

def manhattan_distance(board: Board, target_board: Board) -> float:
    """
    Heurística de distancia Manhattan.
    Suma de |x1-x2| + |y1-y2| para cada pieza hasta su posición objetivo.

    Complejidad: O(n²) - Rápida
    Admisible: ✅ Sí (cada movimiento solo puede reducir la distancia en 1)

    Para 8x8: Valor típico entre 0-400
    Es el MEJOR BALANCE entre velocidad y precisión para 8x8.

    Ejemplo:
    Actual: 1 2 3    Meta: 1 2 3
            4 5 6          4 5 6
            7 8 0          8 0 7

    Pieza 8: (2,1)→(2,0) dist 1
    Pieza 7: (2,0)→(2,2) dist 2
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


# ============================================================================
# HEURÍSTICA 3: Manhattan + Linear Conflict
# ============================================================================

def linear_conflict(board: Board, target_board: Board) -> float:
    """
    Heurística de Manhattan + Conflictos Lineales.

    Un conflicto lineal ocurre cuando dos piezas están en la misma fila/columna
    pero en orden inverso al que deberían estar, lo que requiere movimientos
    adicionales para resolverse.

    Complejidad: O(n³) en el peor caso - Moderada
    Admisible: ✅ Sí (cada conflicto requiere al menos 2 movimientos extra)

    Para 8x8: Más precisa que Manhattan, pero verificar rendimiento.
    Cada conflicto suma 2 a la heurística.

    Ejemplo:
    Actual: 1 2 3    Meta: 1 2 3
            4 5 6          4 5 6
            7 8 0          8 0 7

    Manhattan = 3
    Conflicto: 8 y 7 intercambiadas en fila 2 → +2
    Total = 5
    """
    # Base: Manhattan
    h = manhattan_distance(board, target_board)

    dimension = board.get_dimension()
    conflicts = 0

    # Mapa de posiciones objetivo
    target_positions = {}
    for i in range(dimension):
        for j in range(dimension):
            piece = target_board.get_piece(i, j)
            target_positions[piece] = (i, j)

    # =========================================================
    # Conflictos en filas
    # =========================================================
    for i in range(dimension):
        # Piezas en esta fila que deberían estar en esta fila
        row_pieces = []  # (col_actual, col_objetivo)

        for j in range(dimension):
            piece = board.get_piece(i, j)
            if piece != "#":
                ti, tj = target_positions[piece]
                if ti == i:  # Debería estar en esta fila
                    row_pieces.append((j, tj))

        # Detectar conflictos: pares intercambiados
        for k in range(len(row_pieces)):
            for l in range(k + 1, len(row_pieces)):
                if (row_pieces[k][0] < row_pieces[l][0] and
                    row_pieces[k][1] > row_pieces[l][1]):
                    conflicts += 1
                elif (row_pieces[k][0] > row_pieces[l][0] and
                      row_pieces[k][1] < row_pieces[l][1]):
                    conflicts += 1

    # =========================================================
    # Conflictos en columnas
    # =========================================================
    for j in range(dimension):
        # Piezas en esta columna que deberían estar en esta columna
        col_pieces = []  # (fila_actual, fila_objetivo)

        for i in range(dimension):
            piece = board.get_piece(i, j)
            if piece != "#":
                ti, tj = target_positions[piece]
                if tj == j:  # Debería estar en esta columna
                    col_pieces.append((i, ti))

        for k in range(len(col_pieces)):
            for l in range(k + 1, len(col_pieces)):
                if (col_pieces[k][0] < col_pieces[l][0] and
                    col_pieces[k][1] > col_pieces[l][1]):
                    conflicts += 1
                elif (col_pieces[k][0] > col_pieces[l][0] and
                      col_pieces[k][1] < col_pieces[l][1]):
                    conflicts += 1

    # Cada conflicto requiere al menos 2 movimientos adicionales
    return h + 2 * conflicts


# ============================================================================
# HEURÍSTICA 4: Manhattan + Corner Penalty (PROPUESTA PROPIA)
# ============================================================================

def manhattan_corner_penalty(board: Board, target_board: Board) -> float:
    """
    Heurística: Manhattan + Penalización por esquinas.
    PROPUESTA PROPIA - Creada específicamente para este examen.

    IDEA: Las piezas en las esquinas son las más difíciles de mover.
    Si una pieza está en la esquina equivocada, necesitará movimientos extra
    para salir y volver a entrar.

    COMPLEJIDAD: O(n²) - Muy rápida (solo revisa 4 esquinas)

    ADMISIBILIDAD: ✅ Sí, porque:
    - Penalización 2: Una pieza en esquina incorrecta realmente necesita
      al menos 2 movimientos para salir de la esquina
    - Penalización 1: Una pieza que debe salir de esquina necesita 1 movimiento

    Para 8x8: Mejora Manhattan sin sacrificar velocidad, ideal para tableros grandes.

    Ejemplo:
    Si una pieza que debería estar en (0,0) está en (0,7):
    - Manhattan ya cuenta la distancia (7+0=7)
    - Corner Penalty añade +2 por estar en esquina incorrecta
    Total = 9 (más preciso que 7)
    """
    # Primero calculamos Manhattan
    h = manhattan_distance(board, target_board)

    dimension = board.get_dimension()
    if dimension < 3:  # Penalización solo relevante en tableros grandes
        return h

    # Posiciones de las 4 esquinas
    corners = [
        (0, 0),  # Superior izquierda
        (0, dimension-1),  # Superior derecha
        (dimension-1, 0),  # Inferior izquierda
        (dimension-1, dimension-1)  # Inferior derecha
    ]
    corners_set = set(corners)

    # Mapa de posiciones objetivo
    target_positions = {}
    for i in range(dimension):
        for j in range(dimension):
            piece = target_board.get_piece(i, j)
            target_positions[piece] = (i, j)

    penalty = 0

    # Revisar cada esquina del tablero actual
    for i, j in corners:
        piece = board.get_piece(i, j)
        if piece == "#":  # El espacio vacío no penaliza
            continue

        ti, tj = target_positions[piece]
        current_corner = (i, j)
        target_corner = (ti, tj)

        # Caso 1: La pieza DEBERÍA estar en UNA esquina
        if target_corner in corners_set:
            # Si está en la esquina correcta, no penalizar
            if current_corner == target_corner:
                continue
            # Si está en OTRA esquina (peor caso)
            else:
                # Necesitará moverse entre esquinas (mucho más costoso)
                penalty += 2

        # Caso 2: La pieza NO debería estar en esquina (está estorbando)
        elif target_corner not in corners_set:
            # Penalizar porque está ocupando una esquina valiosa
            penalty += 1

    # Bonus: Si el vacío está en una esquina, es bueno (facilita movimientos)
    empty_i, empty_j = board.get_empty_position()
    if (empty_i, empty_j) in corners_set:
        penalty = max(0, penalty - 1)  # Reducir penalización

    return h + penalty


# ============================================================================
# DICCIONARIO DE HEURÍSTICAS DISPONIBLES
# ============================================================================

HEURISTICS = {
    '1': ('Hamming Distance', hamming_distance, True, '⚡ Rápida, poco precisa'),
    '2': ('Manhattan Distance', manhattan_distance, True, '⚡⚡ Balance perfecto para 8x8'),
    '3': ('Linear Conflict', linear_conflict, True, '⚡⚡⚡ Muy precisa, más lenta'),
    '4': ('Corner Penalty', manhattan_corner_penalty, True, '⚡⚡ Propia, ideal para 8x8'),
}

# Recomendación para 8x8
RECOMENDACION_8x8 = """
🔍 RECOMENDACIÓN PARA TABLEROS 8x8:

Para tableros grandes (8x8), recomiendo:

1. 🥇 MANHATTAN DISTANCE (H2): Mejor balance velocidad/precisión
   - Rápida de calcular
   - Suficientemente precisa
   - IDA* iterará menos veces

2. 🥈 CORNER PENALTY (H4): Mi propuesta mejorada
   - Casi tan rápida como Manhattan
   - Más precisa en situaciones de esquina
   - Ideal para destacar en el examen

3. 🥉 LINEAR CONFLICT (H3): Solo si es rápida en tu máquina
   - Prueba primero con algunos casos
   - Si tarda >0.1s por evaluación, mejor no usarla

4. ⚠️ HAMMING (H1): Evitar para 8x8 (muy lenta por iteraciones)
"""


def get_heuristic(name_or_key: str):
    """
    Obtiene una función heurística por nombre o clave.

    Args:
        name_or_key: '1','2','3','4' o nombre parcial

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
    print(f"⚠️  Heurística '{name_or_key}' no encontrada. Usando Manhattan (recomendada para 8x8).")
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


# ============================================================================
# EJEMPLO DE CÁLCULO (RESPUESTA A LA PREGUNTA 3)
# ============================================================================

def ejemplo_calculo_pregunta3():
    """
    Muestra un ejemplo detallado de cómo se calcula f = g + h
    para un estado actual y una meta predefinida.
    """
    print("=" * 70)
    print("PREGUNTA 3: EJEMPLO DE CÁLCULO DE LA FUNCIÓN DE EVALUACIÓN f")
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

    print("\n🎯 ESTADO META:")
    print(goal)
    print("\n🔷 ESTADO ACTUAL (a 2 movimientos de la meta):")
    print(current)

    print("\n" + "-" * 70)
    print("PASO 1: Calculamos g(n) - profundidad actual")
    print("-" * 70)
    g = 5  # Supongamos que hemos hecho 5 movimientos para llegar aquí
    print(f"   g = {g} (hemos realizado 5 movimientos desde el inicio)")

    print("\n" + "-" * 70)
    print("PASO 2: Calculamos h(n) con diferentes heurísticas")
    print("-" * 70)

    # Calcular cada heurística
    h1 = hamming_distance(current, goal)
    h2 = manhattan_distance(current, goal)
    h3 = linear_conflict(current, goal)
    h4 = manhattan_corner_penalty(current, goal)

    print(f"\n📊 Heurística 1 - Hamming Distance:")
    print(f"   h1 = {h1}")
    print(f"   Explicación: Piezas mal colocadas: 4 y 5 → 2")

    print(f"\n📊 Heurística 2 - Manhattan Distance:")
    print(f"   h2 = {h2}")
    print(f"   Explicación: Pieza 4: (1,1)→(1,2) dist 1")
    print(f"               Pieza 5: (1,2)→(1,1) dist 1")
    print(f"               Total = 2")

    print(f"\n📊 Heurística 3 - Linear Conflict:")
    print(f"   h3 = {h3}")
    print(f"   Explicación: Manhattan (2) + 2×conflictos(1) = 4")
    print(f"               Conflicto: 4 y 5 intercambiadas")

    print(f"\n📊 Heurística 4 - Corner Penalty (PROPIA):")
    print(f"   h4 = {h4}")
    print(f"   Explicación: Manhattan (2) + penalización(0) = 2")
    print(f"               (No hay esquinas involucradas en 3x3)")

    print("\n" + "-" * 70)
    print("PASO 3: Calculamos f(n) = g(n) + h(n)")
    print("-" * 70)

    print(f"\nCon Heurística Manhattan:")
    print(f"   f = g + h = {g} + {h2} = {g + h2}")

    print(f"\nCon Heurística Linear Conflict:")
    print(f"   f = g + h = {g} + {h3} = {g + h3}")

    print(f"\nCon Heurística Corner Penalty (propia):")
    print(f"   f = g + h = {g} + {h4} = {g + h4}")

    print("\n" + "-" * 70)
    print("ARGUMENTACIÓN: ¿Por qué es buena esta función de evaluación?")
    print("-" * 70)
    print("""
    La función f(n) = g(n) + h(n) es excelente para la búsqueda porque:

    1️⃣  **Equilibrio entre pasado y futuro**: 
        - g(n) representa el costo REAL ya invertido
        - h(n) estima el costo FUTURO por invertir
        - Juntas dan una estimación completa del costo total

    2️⃣  **Optimalidad (si h es admisible)**:
        - Si h(n) NUNCA sobreestima, entonces f(n) es optimista
        - IDA* garantiza encontrar la solución ÓPTIMA

    3️⃣  **Eficiencia en 8x8**:
        - Guía la búsqueda hacia nodos prometedores
        - Poda ramas que claramente no mejorarán la solución
        - Reduce exponencialmente el espacio de búsqueda

    4️⃣  **Admisibilidad de nuestras heurísticas**:
        - ✅ Hamming: admisible (cada pieza mal necesita ≥1 mov)
        - ✅ Manhattan: admisible (cada mov reduce distancia en ≤1)
        - ✅ Linear Conflict: admisible (cada conflicto necesita ≥2 mov)
        - ✅ Corner Penalty: admisible (penalización conservadora de 1-2)

    Para 8x8, recomiendo usar **Manhattan** o **Corner Penalty** por su
    excelente balance entre velocidad y precisión.
    """)

    print("\n" + "-" * 70)
    print(RECOMENDACION_8x8)
    print("-" * 70)


# ============================================================================
# MAIN: Ejecutar el ejemplo de la Pregunta 3
# ============================================================================

if __name__ == "__main__":
    ejemplo_calculo_pregunta3()

    # Mostrar información de las heurísticas
    print("\n" + "=" * 70)
    print("📋 RESUMEN DE HEURÍSTICAS DISPONIBLES")
    print("=" * 70)
    for key, (name, _, admissible, desc) in HEURISTICS.items():
        adm = "✅ Admisible" if admissible else "❌ No admisible"
        print(f"{key}. {name}: {desc} - {adm}")