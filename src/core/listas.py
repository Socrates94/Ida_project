from typing import Optional, Iterator
from .node import Nodo

class ListaDoble:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.cabeza: Optional[Nodo] = None
        self.cola: Optional[Nodo] = None
        self.tamano: int = 0

    def insertar_al_final(self, nodo: Nodo) -> None:
        """Inserta un nodo al final de la lista."""
        if nodo.en_lista is not None:
            raise ValueError(f"El nodo ya está en la lista {nodo.en_lista}")
        nodo.prev = self.cola
        nodo.next = None
        if self.cola:
            self.cola.next = nodo
        else:
            self.cabeza = nodo
        self.cola = nodo
        nodo.en_lista = self.nombre
        self.tamano += 1

    def insertar_al_inicio(self, nodo: Nodo) -> None:
        if nodo.en_lista is not None:
            raise ValueError(f"El nodo ya está en la lista {nodo.en_lista}")
        nodo.prev = None
        nodo.next = self.cabeza
        if self.cabeza:
            self.cabeza.prev = nodo
        else:
            self.cola = nodo
        self.cabeza = nodo
        nodo.en_lista = self.nombre
        self.tamano += 1

    def eliminar(self, nodo: Nodo) -> None:
        """Elimina un nodo de la lista (debe estar en ella)."""
        if nodo.en_lista != self.nombre:
            return  # Opcional: lanzar excepción si se prefiere
        if nodo.prev:
            nodo.prev.next = nodo.next
        else:
            self.cabeza = nodo.next
        if nodo.next:
            nodo.next.prev = nodo.prev
        else:
            self.cola = nodo.prev
        nodo.prev = None
        nodo.next = None
        nodo.en_lista = None
        self.tamano -= 1

    def extraer_primero(self) -> Optional[Nodo]:
        if self.cabeza is None:
            return None
        nodo = self.cabeza
        self.eliminar(nodo)
        return nodo

    def esta_vacia(self) -> bool:
        return self.cabeza is None

    def __iter__(self) -> Iterator[Nodo]:
        actual = self.cabeza
        while actual:
            yield actual
            actual = actual.next