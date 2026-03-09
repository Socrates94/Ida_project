# IDA* Solver for the N-Puzzle
## Description

This project implements the Iterative Deepening A* (IDA*) algorithm to solve the N-Puzzle problem for board sizes ranging from 4x4 up to 8x8.

The system includes:

- Board representation and movement logic
- Heuristic functions (Manhattan Distance, Linear Conflict)
- IDA* search implementation
- Instance generation for empirical analysis
- Performance metrics and visualization

---

## Project Structure
ida_project/
│
├── src/                               # Código fuente principal
│   ├── __init__.py
│   ├── main.py                        # Punto de entrada y prueba unitaria principal
│   │
│   ├── core/                          # Lógica principal del algoritmo
│   │   ├── __init__.py
│   │   ├── ida_star.py                # Implementación central del IDA* y sus matemáticas
│   │   ├── board.py                   # Lógica Inmutable de representación del Tablero
│   │   └── heuristics.py              # Diccionario y 5 funciones de costo heurístico
│   │
│   └── io/                            # Interface e I/O de archivos
│       ├── __init__.py
│       └── io_handler.py              # Parsing y decodificación
│
├── experiments/                       # Componentes de batching para Análisis Empírico
│   ├── __init__.py
│   ├── generator.py                   # Generación de M*N archivos revolviendo el estado meta
│   └── runner.py                      # Ejecución automatizada de lotes con exportación `.csv`
│
├── data/
│   ├── instances/                     # Directorios de instanciación aleatoria del generator
│   │   ├── 4x4/
│   │   ├── 5x5/
│   │   ├── 6x6/
│   │   ├── 7x7/
│   │   └── 8x8/
│   │
│   └── results/
│       └── raw/                       # Bases de datos CSV con los resultados del Runner
│
├── documentation/
│   └── PSEUDOCODIGO_IDA_STAR.txt      # Traducción requerida del pseudocódigo inicial
│
├── README.md
└── requirements.txt