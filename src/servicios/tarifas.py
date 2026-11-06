"""Cálculo del valor a cobrar usando el patrón Strategy.

Cada estrategia encapsula un algoritmo de cobro distinto. El parqueadero
(contexto) no conoce los detalles: solo le pide a la estrategia asociada al
tipo de vehículo que calcule el valor según los minutos de permanencia.
"""

import math
from abc import ABC, abstractmethod

from utilidades.excepciones import DatoInvalidoError

MINUTOS_POR_HORA = 60


class EstrategiaTarifa(ABC):
    """Interfaz común de todas las estrategias de cobro."""

    @abstractmethod
    def calcular(self, minutos):
        """Devuelve el valor a cobrar (en pesos) para los minutos dados."""

    @staticmethod
    def _validar_minutos(minutos):
        if minutos < 0:
            raise DatoInvalidoError("Los minutos de permanencia no pueden ser negativos.")


class TarifaPorHora(EstrategiaTarifa):
    """Cobra por hora o fracción, con un mínimo de una hora."""

    def __init__(self, valor_hora):
        if valor_hora <= 0:
            raise DatoInvalidoError("El valor por hora debe ser mayor que cero.")
        self.valor_hora = valor_hora

    def calcular(self, minutos):
        self._validar_minutos(minutos)
        horas_cobradas = max(1, math.ceil(minutos / MINUTOS_POR_HORA))
        return horas_cobradas * self.valor_hora


class TarifaPlana(EstrategiaTarifa):
    """Cobra un valor fijo sin importar el tiempo de permanencia."""

    def __init__(self, valor):
        if valor <= 0:
            raise DatoInvalidoError("El valor de la tarifa plana debe ser mayor que cero.")
        self.valor = valor

    def calcular(self, minutos):
        self._validar_minutos(minutos)
        return self.valor


def crear_tarifas_por_defecto():
    """Asocia cada tipo de vehículo con su estrategia de cobro (valores de ejemplo)."""
    return {
        "carro": TarifaPorHora(3000),
        "moto": TarifaPorHora(1500),
        "bicicleta": TarifaPlana(1000),
    }