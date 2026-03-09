from abc import ABC, abstractmethod
from typing import Optional, List, Any
from src.core.board import Board
from src.core.heuristics import manhattan_distance, linear_conflict

class Nodo(ABC):
    def __init__(self, estado: tuple, g: int, dimension: int, padre: Optional['Nodo'] = None):
        self.estado = estado          # Tupla plana con las piezas
        self.g = g
        self.h = 0.0
        self.dimension = dimension    # Necesario para reconstruir Board
        self.padre = padre
        self.hijos: List['Nodo'] = []
        self.prev: Optional['Nodo'] = None
        self.next: Optional['Nodo'] = None
        self.en_lista: Optional[str] = None

    @abstractmethod
    def generar_hijos(self, goal: tuple) -> List['NodoA']:
        board = Board.from_tuple(self.estado, self.dimension)
        hijos_board = board.get_neighbors()
        print(f"DEBUG: Nodo {self.estado[:5]}... tiene {len(hijos_board)} vecinos")
        """Genera los nodos hijos a partir del estado actual."""
        pass

    @abstractmethod
    def calcular_heuristica(self, goal: tuple) -> float:
        """Calcula el valor heurístico h para este nodo."""
        pass

    def f(self) -> float:
        return self.g + self.h

    def __hash__(self):
        return hash(self.estado)

    def __eq__(self, other):
        return isinstance(other, Nodo) and self.estado == other.estado

    def __repr__(self):
        return f"Nodo(g={self.g}, h={self.h:.1f}, estado={self.estado[:4]}...)"


class NodoA(Nodo):
    def __init__(self, estado, g, dimension, padre=None, heuristicas=None):
        super().__init__(estado, g, dimension, padre)
        # Si no se especifican heuristicas, usar solo Manhattan
        self.heuristicas = heuristicas if heuristicas is not None else [manhattan_distance]

    def calcular_heuristica(self, goal: tuple) -> float:
        board = Board.from_tuple(self.estado, self.dimension)
        goal_board = Board.from_tuple(goal, self.dimension)
        # Tomar el máximo de todas las heurísticas
        return max(h(board, goal_board) for h in self.heuristicas)

    def generar_hijos(self, goal: tuple) -> List['NodoA']:
        board = Board.from_tuple(self.estado, self.dimension)
        hijos_board = board.get_neighbors()
        hijos = []
        for b in hijos_board:
            nuevo_g = self.g + 1
            nodo = NodoA(b.to_tuple(), nuevo_g, self.dimension, padre=self, heuristicas=self.heuristicas)
            nodo.h = nodo.calcular_heuristica(goal)
            hijos.append(nodo)
        return hijos


class NodoCC(Nodo):
    def __init__(self, estado, g, dimension, padre=None, heuristicas=None):
        super().__init__(estado, g, dimension, padre)
        # Por defecto usa linear_conflict, pero puede recibir una lista
        self.heuristicas = heuristicas if heuristicas is not None else [linear_conflict]

    def calcular_heuristica(self, goal: tuple) -> float:
        board = Board.from_tuple(self.estado, self.dimension)
        goal_board = Board.from_tuple(goal, self.dimension)
        return max(h(board, goal_board) for h in self.heuristicas)

    def generar_hijos(self, goal: tuple) -> List['NodoCC']:
        board = Board.from_tuple(self.estado, self.dimension)
        hijos_board = board.get_neighbors()
        hijos = []
        for b in hijos_board:
            nuevo_g = self.g + 1
            nodo = NodoCC(b.to_tuple(), nuevo_g, self.dimension, padre=self, heuristicas=self.heuristicas)
            nodo.h = nodo.calcular_heuristica(goal)
            hijos.append(nodo)
        return hijos