ida_project/
│
├── src/                               # Código fuente principal
│   ├── __init__.py
│   ├── main.py                         # Punto de entrada (Preguntas 1 y 2)
│   ├── config.py                       # Parámetros globales (heurística, límites, etc.)
│   │
│   ├── core/                           # Lógica principal del algoritmo
│   │   ├── __init__.py
│   │   ├── ida_star.py                 # Implementación IDA*
│   │   ├── board.py                    # Representación del tablero
│   │   └── heuristics.py               # Funciones heurísticas
│   │
│   ├── io/                             # Entrada / salida
│   │   ├── __init__.py
│   │   └── io_handler.py               # Lectura de archivos y formato salida
│   │
│   └── utils.py                        # Funciones auxiliares generales
│
├── experiments/                        # Análisis empírico (Pregunta 5)
│   ├── __init__.py
│   ├── generator.py                    # Generación de instancias (10,20,50 movs)
│   ├── runner.py                       # Ejecuta experimentos masivos
│   ├── metrics.py                      # Estadísticas
│   └── run_all.py                      # Script maestro para ejecutar todo
│
├── data/
│   ├── input/                          # Archivos manuales (para main)
│   │   └── ejemplo.txt
│   │
│   ├── instances/                      # Instancias generadas
│   │   ├── 4x4/
│   │   ├── 5x5/
│   │   ├── 6x6/
│   │   ├── 7x7/
│   │   └── 8x8/
│   │
│   └── results/
│       ├── raw/                        # Datos crudos CSV
│       ├── processed/                  # Datos agregados
│       └── plots/                      # Gráficas generadas
│
├── requirements.txt
├── README.md
└── documentation/
    └── respuestas_examen.pdf