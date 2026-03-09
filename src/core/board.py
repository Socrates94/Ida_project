"""
Representación del tablero del rompecabezas deslizante.
Usa "#" para representar el espacio vacío.
Optimizada para usar una tupla interna 1D para máxima velocidad en IDA*.
"""
from typing import List, Tuple, Optional

class Board:
    __slots__ = ['dimension', 'board', 'value'] # Optimizacion drástica de memoria

    def __init__(self, dimension: int, pieces: List[str] = None, t_board: tuple = None):
        """
        Inicializa un tablero inmutable.
        Args:
            dimension: Tamaño n del tablero nxn
            pieces: Lista plana de piezas en orden row-major
            t_board: Tupla 1D directamente
        """
        self.dimension = dimension
        self.value = 0.0

        if pieces is not None:
             self.board = tuple(pieces)
        elif t_board is not None:
             self.board = t_board
        else:
             raise ValueError("Either pieces or t_board must be provided")

    def set_value(self, value: float):
        self.value = value

    def get_value(self) -> float:
        return self.value

    def get_piece(self, row: int, col: int) -> str:
        """Obtiene la pieza en una posición (como si fuera 2D)."""
        return self.board[row * self.dimension + col]

    def get_dimension(self) -> int:
        return self.dimension

    def get_board(self) -> List[List[str]]:
        """Compatibilidad hacia atrás (LENTO, usar to_tuple)"""
        return [list(self.board[i * self.dimension:(i + 1) * self.dimension]) for i in range(self.dimension)]

    def _swap(self, idx1: int, idx2: int) -> tuple:
        """Helper para hacer swap en una tupla y devolver la nueva tupla"""
        lst = list(self.board)
        lst[idx1], lst[idx2] = lst[idx2], lst[idx1]
        return tuple(lst)

    def slide_piece(self, row: int, col: int) -> bool:
        """
        [DEPRECADO por inmutabilidad] No se debe usar para mutar el board directamente 
        en un árbol de búsqueda de alto rendimiento. En su lugar, usar get_future_boards.
        Por compatibilidad la dejamos pero lanzará excepción para evitar bugs de mutación de estado.
        """
        raise NotImplementedError("slide_piece is deprecated for performance reasons. Use get_future_boards() instead.")

    def get_future_boards(self) -> List['Board']:
        """
        Genera tableros sucesores devolviendo nuevos objetos inmutables.
        """
        empty_idx = self.board.index("#")
        empty_row = empty_idx // self.dimension
        empty_col = empty_idx % self.dimension
        
        future_boards = []
        
        # Arriba
        if empty_row > 0:
            swap_idx = (empty_row - 1) * self.dimension + empty_col
            future_boards.append(Board(self.dimension, t_board=self._swap(empty_idx, swap_idx)))
        # Abajo
        if empty_row < self.dimension - 1:
            swap_idx = (empty_row + 1) * self.dimension + empty_col
            future_boards.append(Board(self.dimension, t_board=self._swap(empty_idx, swap_idx)))
        # Izquierda
        if empty_col > 0:
            swap_idx = empty_row * self.dimension + (empty_col - 1)
            future_boards.append(Board(self.dimension, t_board=self._swap(empty_idx, swap_idx)))
        # Derecha
        if empty_col < self.dimension - 1:
            swap_idx = empty_row * self.dimension + (empty_col + 1)
            future_boards.append(Board(self.dimension, t_board=self._swap(empty_idx, swap_idx)))
            
        return future_boards

    def get_neighbors(self) -> List['Board']:
        return self.get_future_boards()

    def get_empty_position(self) -> Tuple[int, int]:
        idx = self.board.index("#")
        return (idx // self.dimension, idx % self.dimension)

    def get_piece_position(self, piece: str) -> Tuple[int, int]:
        idx = self.board.index(piece)
        return (idx // self.dimension, idx % self.dimension)

    def to_movements_format(self) -> List[List[int]]:
        result = []
        for i in range(self.dimension):
            row = []
            for j in range(self.dimension):
                piece = self.board[i * self.dimension + j]
                row.append(0 if piece == "#" else int(piece))
            result.append(row)
        return result

    def to_tuple(self) -> tuple:
        return self.board

    @staticmethod
    def from_tuple(tup: tuple, dim: int):
        return Board(dim, t_board=tup)

    def __eq__(self, other: 'Board') -> bool:
        if not isinstance(other, Board):
            return False
        return self.dimension == other.dimension and self.board == other.board

    def __str__(self) -> str:
        rows = [" ".join(self.board[i * self.dimension:(i + 1) * self.dimension]) for i in range(self.dimension)]
        return ".-------.\n| " + " |\n| ".join(rows) + " |\n'-------'"

    def __hash__(self) -> int:
        return hash(self.board)