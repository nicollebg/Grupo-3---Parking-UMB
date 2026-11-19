
"""Implementacion del patron Observer.
    Se usa para pder notificar cuando ocurre un evento importsnte
    con el ingreso o a la salida de alguhn vehiculo"""

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
        
class ObservadorEventos(ObservadorParqueadero):
    """Guarda los ultimos eventos para mostrarlos en la interfaz web."""

    def __init__(self, maximo=30, reloj=None):
        from collections import deque
        from datetime import datetime

        self._reloj = reloj or datetime.now
        self._eventos = deque(maxlen=maximo)
        self._contador = 0

    def actualizar(self, evento, registro, espacios_disponibles):

        if evento not in ("entrada", "salida"):
            return

        self._contador += 1

        self._eventos.append({
            "id": self._contador,
            "evento": evento,
            "placa": registro.vehiculo.placa,
            "tipo": registro.vehiculo.tipo,
            "hora": self._reloj().strftime("%H:%M:%S"),
            "disponibles": espacios_disponibles,
        })

    @property
    def eventos(self):
        """Eventos del mas reciente al mas antiguo."""
        return list(reversed(self._eventos))
