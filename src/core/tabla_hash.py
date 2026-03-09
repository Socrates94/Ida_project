from typing import Optional

from src.core.node import Nodo


class TablaHash:
    def __init__(self):
        self._dict = {}

    def agregar(self, nodo: Nodo) -> None:
        self._dict[nodo.estado] = nodo

    def obtener(self, estado) -> Optional[Nodo]:
        return self._dict.get(estado)

    def eliminar(self, estado) -> None:
        if estado in self._dict:
            del self._dict[estado]

    def contiene(self, estado) -> bool:
        return estado in self._dict