"""Agrega src/ al path para poder importar los paquetes del proyecto en las pruebas."""

import sys
from pathlib import Path

RUTA_SRC = str(Path(__file__).resolve().parents[1] / "src")

if RUTA_SRC not in sys.path:
    sys.path.insert(0, RUTA_SRC)