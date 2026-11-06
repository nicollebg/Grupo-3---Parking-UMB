"""Punto de entrada del Sistema de Gestión de Parqueadero."""

from componentes.menu import MenuConsola
from servicios.parqueadero import Parqueadero

CAPACIDAD_PARQUEADERO = 5


def iniciar_sistema():
    parqueadero = Parqueadero(CAPACIDAD_PARQUEADERO)
    MenuConsola(parqueadero).ejecutar()


if __name__ == "__main__":
    iniciar_sistema()