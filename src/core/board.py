"""
Representación del tablero del rompecabezas deslizante.
Usa "#" para representar el espacio vacío (ficha 0 en el enunciado).
"""
from typing import List, Tuple, Optional


class Board:
    def __init__(self, dimension: int, pieces: List[str] = None, a_board: List[List[str]] = None):
        """
        Inicializa un tablero.
        Args:
            dimension: Tamaño n del tablero nxn
            pieces: Lista plana de piezas en orden row-major
            a_board: Matriz 2D directamente
        """
        self.dimension = dimension
        self.value = 0.0  # Para almacenar valor f (g+h) durante la búsqueda

        if pieces is not None:
            self.board = []
            for i in range(dimension):
                start = i * dimension
                self.board.append(pieces[start:start + dimension])
        elif a_board is not None:
            self.board = a_board
        else:
            raise ValueError("Either pieces or board must be provided")

    def set_value(self, value: float):
        """Establece el valor f del nodo para la búsqueda."""
        self.value = value

    def get_value(self) -> float:
        """Retorna el valor f del nodo."""
        return self.value

    def get_piece(self, row: int, col: int) -> str:
        """Obtiene la pieza en una posición."""
        return self.board[row][col]

    def set_piece(self, row: int, col: int, piece: str):
        """Establece una pieza en una posición."""
        self.board[row][col] = piece

    def get_dimension(self) -> int:
        return self.dimension

    def get_board(self) -> List[List[str]]:
        return self.board

    def slide_piece(self, row: int, col: int) -> bool:
        """
        Desliza una pieza hacia el espacio vacío.
        Args:
            row, col: Posición de la pieza a mover
        Returns:
            True si el movimiento fue válido, False en caso contrario
        """
        empty_row, empty_col = self.get_empty_position()
        piece = self.get_piece(row, col)

        # Verificar si la pieza está adyacente al vacío
        if row == empty_row:
            if abs(col - empty_col) == 1:
                self.set_piece(empty_row, empty_col, piece)
                self.set_piece(row, col, "#")
                return True
        elif col == empty_col:
            if abs(row - empty_row) == 1:
                self.set_piece(empty_row, empty_col, piece)
                self.set_piece(row, col, "#")
                return True
        return False

    def get_free_pieces_positions(self) -> List[Tuple[int, int]]:
        """
        Obtiene las posiciones de las piezas que se pueden mover (adyacentes al vacío).
        Returns:
            Lista de coordenadas (fila, columna) de piezas movibles
        """
        positions: List[Tuple[int, int]] = []
        empty_row, empty_col = self.get_empty_position()

        if empty_row > 0:
            positions.append((empty_row - 1, empty_col))
        if empty_row < self.dimension - 1:
            positions.append((empty_row + 1, empty_col))
        if empty_col > 0:
            positions.append((empty_row, empty_col - 1))
        if empty_col < self.dimension - 1:
            positions.append((empty_row, empty_col + 1))

        return positions

    def get_future_boards(self) -> List['Board']:
        """
        Genera todos los tableros sucesores válidos.
        Returns:
            Lista de nuevos tableros resultantes de mover cada pieza adyacente
        """
        future_boards = []
        for position in self.get_free_pieces_positions():
            # Crear copia profunda del tablero actual
            new_board = Board(
                self.dimension,
                None,
                [[p for p in row] for row in self.board]
            )
            new_board.slide_piece(position[0], position[1])
            future_boards.append(new_board)
        return future_boards

    def get_empty_position(self) -> Tuple[int, int]:
        """Retorna la posición (fila, columna) del espacio vacío (#)."""
        return self.get_piece_position("#")

    def get_piece_position(self, piece: str) -> Tuple[int, int]:
        """Busca la primera ocurrencia de una pieza y retorna su posición."""
        for i in range(self.dimension):
            for j in range(self.dimension):
                if self.get_piece(i, j) == piece:
                    return (i, j)
        raise ValueError(f"Piece {piece} not found in board")

    def to_movements_format(self) -> List[List[int]]:
        """
        Convierte el tablero al formato numérico requerido para salida.
        Returns:
            Matriz de enteros (0 para el espacio vacío)
        """
        result = []
        for i in range(self.dimension):
            row = []
            for j in range(self.dimension):
                piece = self.get_piece(i, j)
                if piece == "#":
                    row.append(0)
                else:
                    row.append(int(piece))
            result.append(row)
        return result

    def __eq__(self, other: 'Board') -> bool:
        if not isinstance(other, Board):
            return False
        if self.dimension != other.dimension:
            return False
        return self.board == other.board

    def __str__(self) -> str:
        return (
                ".-------.\n| "
                + ("\n| ".join([" ".join(row) + " |" for row in self.board]))
                + "\n'-------'"
        )

    def __hash__(self) -> int:
        """Permite usar Board como clave en diccionarios/sets."""
        return hash(str(self.board))