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

## 📂 Project Structure
ida_project/
│
├── src/
│ ├── core/
│ │ ├── board.py
│ │ ├── ida_star.py
│ │ └── heuristics.py
│ │
│ ├── io/
│ │ └── io_handler.py
│ │
│ ├── main.py
│ └── utils.py
│
├── experiments/
│ ├── generator.py
│ ├── runner.py
│ └── metrics.py
│
├── data/
│ ├── input/
│ ├── instances/
│ └── results/
│
├── requirements.txt
└── README.md