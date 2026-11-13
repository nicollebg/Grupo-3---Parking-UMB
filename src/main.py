
"""Punto de entrada del Sistema de Gestion de Parqueadero."""

from componentes.menu import MenuConsola
from servicios.parqueadero import Parqueadero

from observadores.observador_parqueadero import ObservadorConsola


CAPACIDAD_PARQUEADERO = 5


def iniciar_sistema():

    parqueadero = Parqueadero(CAPACIDAD_PARQUEADERO)

    # Suscribir el observador de consola
    observador = ObservadorConsola()

    parqueadero.suscribir(observador)

    MenuConsola(parqueadero).ejecutar()


if __name__ == "__main__":
    iniciar_sistema()
