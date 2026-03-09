"""
Implementación del algoritmo IDA* (Iterative Deepening A*).
Refactorizada para garantizar la O(b*d) complejidad métrica teórica.
Integrado con tableros inmutables.
"""
import time
import math
from typing import Optional, List, Tuple

from src.core.board import Board
from src.core.heuristics import get_heuristic_name

class IDAStar:
    
    #Implementación óptima de IDA* optimizada.
    def __init__(self, heuristic_list, goal_board: Board, usar_nodo_cc=False, usar_tabu=False):
        # Guardamos la lista completa de heurísticas para usarlas combinadas
        if not isinstance(heuristic_list, list):
            self.heuristics = [heuristic_list]
        else:
             self.heuristics = heuristic_list
             
        self.goal = goal_board
        
        # Estadísticas
        self.nodes_expanded = 0
        self.max_depth = 0
        self.start_time = 0
        self.solution_moves = []
        self.max_time = None

    def _calcular_h(self, board: Board) -> float:
        """Calcula una combinación de heurísticas, usando el valor máximo (para ser optimista pero eficiente)."""
        return max(h(board, self.goal) for h in self.heuristics)

    def search(self, start_board: Board, max_time: Optional[float] = None) -> Optional[List[str]]:
        self.start_time = time.time()
        self.max_time = max_time
        self.nodes_expanded = 0
        self.max_depth = 0
        self.solution_moves = []

        # Calculamos h inicial usando la combinacion maxima
        threshold = self._calcular_h(start_board)

        print(f"Inicio IDA* con threshold inicial={threshold}")

        while True:
            visited_path = {start_board.to_tuple()}
            path = [start_board]
            
            resultado, nuevo_threshold = self._dfs(path, 0, threshold, visited_path)
            
            if resultado is not None:
                self.solution_moves = self._extraer_movimientos(resultado)
                return self.solution_moves
            
            if nuevo_threshold == float('inf'):
                return None
            
            if self.max_time and (time.time() - self.start_time) > self.max_time:
                 print("Timeout de IDA* alcanzado.")
                 return None

            threshold = nuevo_threshold
            print(f"IDDFS Profundización. Nuevo threshold: {threshold}")

    def _dfs(self, path: List[Board], g: float, threshold: float, visited: set) -> Tuple[Optional[List[Board]], float]:
        node = path[-1]
        f = g + self._calcular_h(node)
        
        self.nodes_expanded += 1
        self.max_depth = max(self.max_depth, len(path))

        if f > threshold:
            return None, f

        if node == self.goal:
            return path, threshold

        min_threshold = float('inf')
        
        # Generar hijos
        successors = node.get_future_boards()
        
        # Ordenalos por heurística max (usando nuestra funcion de combinacion) para acelerar
        successors.sort(key=lambda b: self._calcular_h(b))

        for child in successors:
             child_tuple = child.to_tuple()
             
             # Prevent Cycles in the current DFS path
             if child_tuple not in visited:
                 visited.add(child_tuple)
                 path.append(child)
                 
                 result, t = self._dfs(path, g + 1, threshold, visited)
                 
                 if result is not None:
                     return result, threshold
                 
                 if t < min_threshold:
                     min_threshold = t
                     
                 # Backtrack
                 path.pop()
                 visited.remove(child_tuple)
                 
             # Check Timeout
             if self.max_time and (time.time() - self.start_time) > self.max_time:
                 return None, float('inf')

        return None, min_threshold

    def _extraer_movimientos(self, path: List[Board]) -> List[str]:
         movimientos = []
         print(f"Extrayendo movimientos de camino de longitud {len(path)}")
         if len(path) <= 1:
            print("ADVERTENCIA: Camino con longitud <= 1")
            return []

         for i in range(len(path) - 1):
            board_actual = path[i]
            board_sig = path[i+1]
            
            v_a_r, v_a_c = board_actual.get_empty_position()
            v_d_r, v_d_c = board_sig.get_empty_position()
            
            dr = v_d_r - v_a_r
            dc = v_d_c - v_a_c

            if dr == -1: movimientos.append('U')
            elif dr == 1: movimientos.append('D')
            elif dc == -1: movimientos.append('L')
            elif dc == 1: movimientos.append('R')
            
         return movimientos

    def get_statistics(self) -> dict:
        heuristic_names = [get_heuristic_name(h) for h in self.heuristics]
        return {
            'nodes_expanded': self.nodes_expanded,
            'max_depth': self.max_depth,
            'solution_length': len(self.solution_moves),
            'heuristic': " + ".join(heuristic_names)
        }


#FUNCIÓN AUXILIAR: Verificar si un puzzle tiene solución
def es_resoluble(board: Board, goal: Board) -> bool:
    """Verifica si el puzzle tiene solución."""
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
    inversiones = 0
    for i in range(len(linear)):
        for j in range(i + 1, len(linear)):
            if linear[i] > linear[j]:
                inversiones += 1
    if dimension % 2 == 1:
        return inversiones % 2 == 0
    else:
        return (inversiones + zero_row) % 2 == 1



# Pruebas
# def test_con_ejemplo_examen():
#     from src.core.heuristics import manhattan_distance
#     print("=" * 70)
#     print("PRUEBA IDA* CON EJEMPLO DEL EXAMEN (Pregunta 2)")
#     print("=" * 70)

#     goal = Board(3, pieces=["1","2","3","8","#","4","7","6","5"])
#     start = Board(3, pieces=["1","2","3","8","4","5","7","6","#"])

#     print("\nTablero inicial:")
#     print(start)
#     print("\nTablero objetivo:")
#     print(goal)

#     if not es_resoluble(start, goal):
#         print("\nEste puzzle NO tiene solucion")
#         return

#     solver = IDAStar([manhattan_distance], goal, usar_nodo_cc=False)
#     moves = solver.search(start, max_time=10)

#     if moves:
#         output = ",".join(moves)
#         print(f"\nSolucion encontrada: {output}")
#         print(f"Estadisticas: {solver.get_statistics()}")
#         if output == "U,L":
#             print("Coincide con la salida esperada 'U,L'")
#         else:
#             print(f"Se esperaba 'U,L' pero se obtuvo '{output}'")
#     else:
#         print("\nNo se encontro solucion")


# if __name__ == "__main__":
#     test_con_ejemplo_examen()