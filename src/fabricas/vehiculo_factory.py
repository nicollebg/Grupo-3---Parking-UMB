
"""Implementacion de Factory Method para crear vehiculos.
    Se utiliza para centralizar la creación de vehículos. 
    En lugar de crear directamentre los objetos desde el menu, 
    se usa fabrica que identifica que tipo de vehiculo se quiere
    registrar y utiliza el creador correspondiente.
    """

from abc import ABC, abstractmethod

from modelos.vehiculo import TIPOS_VALIDOS, Vehiculo
from utilidades.validaciones import normalizar_tipo


class CreadorVehiculo(ABC):
    """Creador abstracto que define el metodo de fabrica."""

    @abstractmethod
    def crear_vehiculo(self, placa):
        """Construye un vehiculo del tipo definido por el creador."""


class CreadorCarro(CreadorVehiculo):

    def crear_vehiculo(self, placa):
        return Vehiculo(placa, "carro")


class CreadorMoto(CreadorVehiculo):

    def crear_vehiculo(self, placa):
        return Vehiculo(placa, "moto")


class CreadorBicicleta(CreadorVehiculo):

    def crear_vehiculo(self, placa):
        return Vehiculo(placa, "bicicleta")


class FabricaVehiculos:
    """Selecciona el creador adecuado para cada tipo de vehiculo."""

    def __init__(self):
        self._creadores = {
            "carro": CreadorCarro(),
            "moto": CreadorMoto(),
            "bicicleta": CreadorBicicleta(),
        }

    def crear(self, placa, tipo):
        tipo = normalizar_tipo(tipo, TIPOS_VALIDOS)
        creador = self._creadores[tipo]

        return creador.crear_vehiculo(placa)
