"""
Implementación del algoritmo IDA* (Iterative Deepening A*).
Responde a la Pregunta 2: Pseudocódigo y Pregunta 4: Implementación.

Integrado con las heurísticas de heuristics.py para tableros hasta 8x8.
"""
import time
import os
import sys
from typing import List, Optional, Tuple, Dict, Set

# Añadir la raíz del proyecto al sys.path para permitir importaciones desde 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.board import Board
from src.core.heuristics import (
    manhattan_distance,
    get_heuristic,
    get_heuristic_name,
    evaluacion_f
)


class IDAStar:
    """
    Implementación del algoritmo IDA* para el sliding puzzle.

    Características:
    - Búsqueda en profundidad iterativa con poda por f(n) = g(n) + h(n)
    - Optimizado para tableros de 4x4 hasta 8x8
    - Detección de ciclos simples
    - Estadísticas de búsqueda
    """

    def __init__(self, heuristic_func=manhattan_distance, max_time=None):
        """
        Inicializa el solver IDA*.

        Args:
            heuristic_func: Función heurística a usar (por defecto Manhattan)
            max_time: Tiempo máximo de ejecución en segundos (opcional)
        """
        self.heuristic = heuristic_func
        self.max_time = max_time
        self.nodes_expanded = 0
        self.max_depth = 0
        self.start_time = 0
        self.states_visited: Set[str] = set()
        self.solution_moves: List[str] = []
        self.solution_path: List[Board] = []

    def search(self, start: Board, goal: Board) -> Tuple[Optional[List[str]], float, int, int]:
        """
        Método principal que ejecuta IDA*.

        Args:
            start: Tablero inicial
            goal: Tablero objetivo

        Returns:
            Tuple: (movimientos, tiempo_segundos, nodos_expandidos, profundidad_maxima)
            Si no encuentra solución, movimientos = None
        """
        # Reiniciar estadísticas
        self.nodes_expanded = 0
        self.max_depth = 0
        self.states_visited.clear()
        self.start_time = time.time()

        # =========================================================
        # PASO 1: Calcular umbral inicial = h del nodo raíz
        # =========================================================
        threshold = self.heuristic(start, goal)

        # Camino actual (lista de tableros)
        path = [start]

        # Movimientos realizados
        moves = []

        iteration = 1
        while True:
            # Verificar timeout
            if self.max_time and (time.time() - self.start_time) > self.max_time:
                print(f"⏱️  Timeout después de {self.max_time} segundos")
                return None, time.time() - self.start_time, self.nodes_expanded, self.max_depth

            # =========================================================
            # PASO 2: Búsqueda en profundidad con límite threshold
            # =========================================================
            result, new_threshold = self._depth_limited_search(
                node=start,
                goal=goal,
                g=0,
                threshold=threshold,
                path=path,
                moves=moves
            )

            # =========================================================
            # PASO 3: Si encontró solución
            # =========================================================
            if result is not None:
                elapsed = time.time() - self.start_time
                self.solution_moves = result
                self.solution_path = path
                return result, elapsed, self.nodes_expanded, self.max_depth

            # =========================================================
            # PASO 4: Si no hay solución posible
            # =========================================================
            if new_threshold == float('inf'):
                elapsed = time.time() - self.start_time
                return None, elapsed, self.nodes_expanded, self.max_depth

            # =========================================================
            # PASO 5: Aumentar umbral para siguiente iteración
            # =========================================================
            threshold = new_threshold
            iteration += 1

            if iteration % 10 == 0:
                print(f"🔄 Iteración {iteration}, umbral = {threshold:.1f}, "
                      f"nodos expandidos = {self.nodes_expanded}")

    def _depth_limited_search(self, node: Board, goal: Board, g: int,
                              threshold: float, path: List[Board],
                              moves: List[str]) -> Tuple[Optional[List[str]], float]:
        """
        Búsqueda en profundidad con límite de costo f = g + h.

        Args:
            node: Nodo actual
            goal: Nodo objetivo
            g: Profundidad actual
            threshold: Umbral de costo actual
            path: Camino recorrido (para detección de ciclos)
            moves: Movimientos realizados hasta ahora

        Returns:
            Tuple: (movimientos_completos si encontró, nuevo_umbral mínimo)
        """
        # Verificar timeout
        if self.max_time and (time.time() - self.start_time) > self.max_time:
            return None, float('inf')

        self.nodes_expanded += 1
        self.max_depth = max(self.max_depth, g)

        # =========================================================
        # PASO 1: Calcular f = g + h
        # =========================================================
        h = self.heuristic(node, goal)
        f = g + h

        # =========================================================
        # PASO 2: Poda - si f excede el umbral
        # =========================================================
        if f > threshold:
            return None, f

        # =========================================================
        # PASO 3: Verificar si es el objetivo
        # =========================================================
        if node == goal:
            return moves, threshold

        # =========================================================
        # PASO 4: Generar sucesores y ordenar por heurística
        # =========================================================
        successors = node.get_future_boards()

        # Calcular h para cada sucesor y filtrar ciclos
        successors_with_h = []
        for succ in successors:
            # Evitar ciclos simples (no volver al padre inmediato)
            if len(path) > 1 and succ == path[-2]:
                continue

            # Evitar estados ya visitados en esta rama (opcional, mejora rendimiento)
            succ_tuple = str(succ)
            if succ_tuple in self.states_visited:
                continue

            h_succ = self.heuristic(succ, goal)
            successors_with_h.append((succ, h_succ))

        # Ordenar por heurística (mejor primero) - crucial para rendimiento
        successors_with_h.sort(key=lambda x: x[1])

        # =========================================================
        # PASO 5: Explorar sucesores
        # =========================================================
        min_threshold = float('inf')

        for succ, h_succ in successors_with_h:
            # Determinar el movimiento realizado
            move = self._get_move(node, succ)

            # Marcar como visitado en esta rama
            self.states_visited.add(str(succ))

            # Llamada recursiva
            result, new_thresh = self._depth_limited_search(
                node=succ,
                goal=goal,
                g=g + 1,
                threshold=threshold,
                path=path + [succ],
                moves=moves + [move]
            )

            # Desmarcar al retroceder (backtracking)
            self.states_visited.remove(str(succ))

            if result is not None:
                return result, threshold

            if new_thresh < min_threshold:
                min_threshold = new_thresh

        return None, min_threshold

    def _get_move(self, from_board: Board, to_board: Board) -> str:
        """
        Determina qué movimiento se realizó entre dos tableros.
        Basado en el movimiento del espacio vacío.

        Returns:
            'U' (Arriba), 'D' (Abajo), 'L' (Izquierda), 'R' (Derecha)
        """
        empty_before = from_board.get_empty_position()
        empty_after = to_board.get_empty_position()

        dr = empty_after[0] - empty_before[0]
        dc = empty_after[1] - empty_before[1]

        if dr == -1:
            return 'U'  # El vacío subió → la pieza bajó
        elif dr == 1:
            return 'D'  # El vacío bajó → la pieza subió
        elif dc == -1:
            return 'L'  # El vacío izquierda → pieza derecha
        elif dc == 1:
            return 'R'  # El vacío derecha → pieza izquierda
        else:
            return '?'  # No debería ocurrir

    def get_statistics(self) -> dict:
        """Retorna estadísticas detalladas de la última búsqueda."""
        return {
            'nodes_expanded': self.nodes_expanded,
            'max_depth': self.max_depth,
            'solution_length': len(self.solution_moves) if self.solution_moves else 0,
            'heuristic': get_heuristic_name(self.heuristic),
            'solution_moves': ','.join(self.solution_moves) if self.solution_moves else "None"
        }

    def print_solution(self, start: Board, goal: Board):
        """Imprime la solución de forma legible."""
        if not self.solution_moves:
            print("❌ No se encontró solución")
            return

        print("\n" + "=" * 60)
        print("✅ SOLUCIÓN ENCONTRADA")
        print("=" * 60)
        print(f"📋 Movimientos: {','.join(self.solution_moves)}")
        print(f"📊 Estadísticas:")
        print(f"   • Nodos expandidos: {self.nodes_expanded}")
        print(f"   • Profundidad: {self.max_depth}")
        print(f"   • Longitud solución: {len(self.solution_moves)}")
        print(f"   • Heurística: {get_heuristic_name(self.heuristic)}")

        # Mostrar los primeros movimientos si es muy larga
        if len(self.solution_moves) > 20:
            print(f"\n📝 Primeros 20 movimientos: {','.join(self.solution_moves[:20])}...")


# ============================================================================
# FUNCIÓN AUXILIAR: Verificar si un puzzle tiene solución
# ============================================================================

def es_resoluble(board: Board, goal: Board) -> bool:
    """
    Verifica si un puzzle 8-puzzle o 15-puzzle tiene solución.
    Útil para filtrar instancias sin solución antes de ejecutar IDA*.

    Regla: El número de inversiones + fila del vacío debe ser par.
    """
    # Convertir tablero a lista lineal ignorando el vacío
    linear = []
    zero_row = 0

    dimension = board.get_dimension()
    for i in range(dimension):
        for j in range(dimension):
            piece = board.get_piece(i, j)
            if piece == "#":
                zero_row = i
            else:
                linear.append(int(piece))

    # Contar inversiones
    inversiones = 0
    for i in range(len(linear)):
        for j in range(i + 1, len(linear)):
            if linear[i] > linear[j]:
                inversiones += 1

    # Para tableros de dimensión impar: (inversiones % 2) debe ser 0
    if dimension % 2 == 1:
        return inversiones % 2 == 0
    # Para tableros de dimensión par: (inversiones + fila_vacio) % 2 debe ser 1
    else:
        return (inversiones + zero_row) % 2 == 1


# ============================================================================
# FUNCIÓN DE PRUEBA CON EL EJEMPLO DEL EXAMEN
# ============================================================================

def test_con_ejemplo_examen():
    """Prueba IDA* con el ejemplo dado en la Pregunta 2 del examen."""
    print("=" * 70)
    print("PRUEBA IDA* CON EJEMPLO DEL EXAMEN (Pregunta 2)")
    print("=" * 70)

    # Crear el tablero objetivo del ejemplo
    goal_board = Board(3, [
        "1", "2", "3",
        "8", "#", "4",
        "7", "6", "5"
    ])

    # Crear el tablero inicial del ejemplo
    start_board = Board(3, [
        "1", "2", "3",
        "8", "4", "5",
        "7", "6", "#"
    ])

    print("\n📋 Tablero inicial:")
    print(start_board)
    print("\n🎯 Tablero objetivo:")
    print(goal_board)

    # Verificar si es resoluble
    if not es_resoluble(start_board, goal_board):
        print("\n⚠️  Este puzzle NO tiene solución")
        return

    # Probar con diferentes heurísticas
    heuristicas_a_probar = ['1', '2', '3', '4']

    for heur_key in heuristicas_a_probar:
        print(f"\n{'-' * 50}")
        heur_func = get_heuristic(heur_key)
        heur_name = get_heuristic_name(heur_func)
        print(f"🔍 Probando con heurística: {heur_name}")

        solver = IDAStar(heuristic_func=heur_func)
        moves, elapsed, nodes, depth = solver.search(start_board, goal_board)

        if moves:
            output = ",".join(moves)
            print(f"   ✅ Solución: {output}")
            print(f"   ⏱️  Tiempo: {elapsed:.4f}s")
            print(f"   📊 Nodos: {nodes}")

            # Verificar que coincide con lo esperado
            if output == "U,L":
                print(f"   ✓ Coincide con la salida esperada 'U,L'")
            else:
                print(f"   ✗ Se esperaba 'U,L' pero se obtuvo '{output}'")
        else:
            print(f"   ❌ No se encontró solución")

    print("\n" + "=" * 70)


# ============================================================================
# FUNCIÓN DE PRUEBA CON TABLERO GENERADO
# ============================================================================

def test_con_archivo(archivo: str, heuristica: str = '2'):
    """
    Prueba IDA* con un archivo generado por generator.py.

    Args:
        archivo: Ruta al archivo .txt
        heuristica: Clave de heurística ('1','2','3','4')
    """
    from src.io.io_handler import leer_archivo

    print("=" * 70)
    print(f"PRUEBA IDA* CON ARCHIVO: {archivo}")
    print("=" * 70)

    # Leer el archivo
    n, start_board, goal_board = leer_archivo(archivo)

    if not start_board or not goal_board:
        print("❌ Error al leer el archivo")
        return

    print(f"\n📏 Dimensión: {n}x{n}")
    print("\n📋 Tablero inicial:")
    print(start_board)
    print("\n🎯 Tablero objetivo:")
    print(goal_board)

    # Verificar si es resoluble
    if not es_resoluble(start_board, goal_board):
        print("\n⚠️  Este puzzle NO tiene solución")
        return

    # Obtener heurística
    heur_func = get_heuristic(heuristica)
    heur_name = get_heuristic_name(heur_func)
    print(f"\n🧠 Heurística: {heur_name}")

    # Resolver
    print("\n🔍 Buscando solución...")
    solver = IDAStar(heuristic_func=heur_func)
    moves, elapsed, nodes, depth = solver.search(start_board, goal_board)

    if moves:
        output = ",".join(moves)
        print(f"\n✅ SOLUCIÓN ENCONTRADA")
        print(f"   Movimientos: {output}")
        print(f"   ⏱️  Tiempo: {elapsed:.4f} segundos")
        print(f"   📊 Nodos expandidos: {nodes}")
        print(f"   📏 Profundidad: {depth}")

        # Mostrar resumen si es muy larga
        if len(moves) > 30:
            print(f"\n📝 Resumen: {','.join(moves[:15])}...{','.join(moves[-15:])}")
    else:
        print(f"\n❌ No se encontró solución en {elapsed:.2f} segundos")


# ============================================================================
# PSEUDOCÓDIGO (RESPUESTA PREGUNTA 2)
# ============================================================================

PSEUDOCODIGO = """
===============================================================================
PREGUNTA 2: PSEUDOCÓDIGO DE IDA* (Iterative Deepening A*)
===============================================================================

ALGORITMO IDA_STAR(inicio, objetivo, heuristica):
    // Umbral inicial = heurística del nodo raíz
    threshold = heuristica(inicio, objetivo)

    MIENTRAS (TRUE) HACER:
        // Búsqueda en profundidad con límite threshold
        [encontrado, nuevo_umbral] = DFS_LIMITADO(inicio, objetivo, 0, threshold, [])

        SI (encontrado) ENTONCES:
            movimientos = extraer_movimientos(camino)
            IMPRIMIR movimientos separados por comas
            RETORNAR movimientos
        FIN SI

        SI (nuevo_umbral == INFINITO) ENTONCES:
            IMPRIMIR "No se encontró solución"
            RETORNAR None
        FIN SI

        threshold = nuevo_umbral
    FIN MIENTRAS


ALGORITMO DFS_LIMITADO(nodo, objetivo, g, threshold, camino):
    f = g + heuristica(nodo, objetivo)

    SI (f > threshold) ENTONCES:
        RETORNAR [FALSE, f]
    FIN SI

    SI (nodo == objetivo) ENTONCES:
        RETORNAR [TRUE, threshold]
    FIN SI

    min_umbral = INFINITO

    PARA CADA vecino EN sucesores(nodo) HACER:
        SI (vecino == padre(nodo)) CONTINUAR  // Evitar ciclos

        [encontrado, umbral] = DFS_LIMITADO(vecino, objetivo, g+1, threshold, camino+[vecino])

        SI (encontrado) ENTONCES:
            RETORNAR [TRUE, threshold]
        FIN SI

        SI (umbral < min_umbral) ENTONCES:
            min_umbral = umbral
        FIN SI
    FIN PARA

    RETORNAR [FALSE, min_umbral]


FUNCIÓN sucesores(nodo):
    // Retorna lista de estados alcanzables moviendo el espacio vacío
    sucesores = []
    PARA CADA dirección EN ['U','D','L','R'] HACER:
        nuevo = mover(nodo, dirección)
        SI (nuevo != None) ENTONCES:
            sucesores.agregar(nuevo)
        FIN SI
    FIN PARA
    RETORNAR sucesores


FUNCIÓN extraer_movimientos(camino):
    // Convierte camino de tableros a secuencia de movimientos
    movimientos = []
    PARA i DESDE 0 HASTA longitud(camino)-2 HACER:
        vacio_antes = posicion_vacio(camino[i])
        vacio_despues = posicion_vacio(camino[i+1])

        SI (vacio_despues.fila < vacio_antes.fila): movimientos.agregar('U')
        SINO SI (vacio_despues.fila > vacio_antes.fila): movimientos.agregar('D')
        SINO SI (vacio_despues.col < vacio_antes.col): movimientos.agregar('L')
        SINO SI (vacio_despues.col > vacio_antes.col): movimientos.agregar('R')
    FIN PARA
    RETORNAR movimientos

===============================================================================
EJEMPLO DE SALIDA:
Para la entrada del examen, la salida debe ser: U,L
===============================================================================
"""

# ============================================================================
# MAIN: Ejecutar pruebas
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='IDA* Solver para Sliding Puzzle')
    parser.add_argument('--modo', choices=['ejemplo', 'archivo', 'pseudocodigo'],
                        default='ejemplo', help='Modo de ejecución')
    parser.add_argument('--archivo', type=str, default='data/input/ejemplo.txt',
                        help='Archivo a procesar (para modo archivo)')
    parser.add_argument('--h', type=str, default='2',
                        help='Heurística a usar: 1=Hamming, 2=Manhattan, 3=Linear, 4=Corner')

    args = parser.parse_args()

    if args.modo == 'ejemplo':
        test_con_ejemplo_examen()

    elif args.modo == 'archivo':
        test_con_archivo(args.archivo, args.h)

    elif args.modo == 'pseudocodigo':
        print(PSEUDOCODIGO)