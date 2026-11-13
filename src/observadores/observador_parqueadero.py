
"""Implementacion del patron Observer."""

from abc import ABC, abstractmethod


class ObservadorParqueadero(ABC):
    """Interfaz que deben implementar los observadores."""

    @abstractmethod
    def actualizar(self, evento, registro, espacios_disponibles):
        """Recibe informacion cuando ocurre un evento."""


class ObservadorConsola(ObservadorParqueadero):
    """Muestra notificaciones de entradas y salidas."""

    def __init__(self, escribir=print):
        self._escribir = escribir

    def actualizar(self, evento, registro, espacios_disponibles):

        vehiculo = registro.vehiculo

        if evento == "entrada":

            mensaje = (
                f"Notificacion: ingreso {vehiculo.tipo} "
                f"{vehiculo.placa}. "
                f"Espacios disponibles: {espacios_disponibles}."
            )

        elif evento == "salida":

            mensaje = (
                f"Notificacion: salida {vehiculo.tipo} "
                f"{vehiculo.placa}. "
                f"Espacios disponibles: {espacios_disponibles}."
            )

        else:
            return

        self._escribir(mensaje)
