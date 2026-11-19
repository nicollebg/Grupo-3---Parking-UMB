"""Cálculo del valor a cobrar usando el patrón Strategy.

Cada estrategia encapsula un algoritmo de cobro distinto. El parqueadero
(contexto) no conoce los detalles: solo le pide a la estrategia asociada al
tipo de vehículo y al plan elegido que calcule el valor.

Estrategias:
- TarifaPorHora: por hora o fracción.
- TarifaPlana: valor fijo.
- TarifaNocturna: valor fijo si el vehículo entra en horario nocturno.
- TarifaConvenio: descuento porcentual sobre otra estrategia.
- TarifaMensualidad: el vehículo ya pagó el mes, cada estadía cuesta $0.
"""

import math
from abc import ABC, abstractmethod

from utilidades.excepciones import DatoInvalidoError

MINUTOS_POR_HORA = 60

# Planes de tarifa que se pueden elegir al registrar la entrada
PLAN_NORMAL = "normal"
PLAN_NOCTURNA = "nocturna"
PLAN_CONVENIO = "convenio"
PLAN_MENSUALIDAD = "mensualidad"
PLANES = (PLAN_NORMAL, PLAN_NOCTURNA, PLAN_CONVENIO, PLAN_MENSUALIDAD)

# Valores de ejemplo
HORA_INICIO_NOCTURNA = 19   # 7:00 p.m.
HORA_FIN_NOCTURNA = 6       # 6:00 a.m.
VALOR_NOCTURNO = {"carro": 8000, "moto": 5000, "bicicleta": 2000}
VALOR_MENSUALIDAD = {"carro": 180000, "moto": 90000, "bicicleta": 30000}
DESCUENTO_CONVENIO = 0.30


class EstrategiaTarifa(ABC):
    """Interfaz común de todas las estrategias de cobro."""

    @abstractmethod
    def calcular(self, minutos, entrada=None):
        """Devuelve el valor a cobrar (en pesos).

        `minutos` es la permanencia y `entrada` (datetime) la hora de ingreso,
        que solo usan las estrategias que dependen del horario.
        """

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

    def calcular(self, minutos, entrada=None):
        self._validar_minutos(minutos)
        horas_cobradas = max(1, math.ceil(minutos / MINUTOS_POR_HORA))
        return horas_cobradas * self.valor_hora


class TarifaPlana(EstrategiaTarifa):
    """Cobra un valor fijo sin importar el tiempo de permanencia."""

    def __init__(self, valor):
        if valor <= 0:
            raise DatoInvalidoError("El valor de la tarifa plana debe ser mayor que cero.")
        self.valor = valor

    def calcular(self, minutos, entrada=None):
        self._validar_minutos(minutos)
        return self.valor


class TarifaNocturna(EstrategiaTarifa):
    """Valor fijo si el vehículo ingresa en horario nocturno.

    Si ingresa de día, delega el cálculo en la estrategia base.
    El horario nocturno cruza la medianoche (por defecto 7 p.m. a 6 a.m.).
    """

    def __init__(self, base, valor_noche,
                 hora_inicio=HORA_INICIO_NOCTURNA, hora_fin=HORA_FIN_NOCTURNA):
        if valor_noche <= 0:
            raise DatoInvalidoError("El valor nocturno debe ser mayor que cero.")
        if not (0 <= hora_inicio <= 23 and 0 <= hora_fin <= 23):
            raise DatoInvalidoError("Las horas del horario nocturno deben estar entre 0 y 23.")
        self.base = base
        self.valor_noche = valor_noche
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin

    def es_nocturna(self, entrada):
        hora = entrada.hour
        return hora >= self.hora_inicio or hora < self.hora_fin

    def calcular(self, minutos, entrada=None):
        self._validar_minutos(minutos)
        if entrada is not None and self.es_nocturna(entrada):
            return self.valor_noche
        return self.base.calcular(minutos, entrada)


class TarifaConvenio(EstrategiaTarifa):
    """Aplica un descuento porcentual (0 < descuento < 1) sobre otra estrategia."""

    def __init__(self, base, descuento=DESCUENTO_CONVENIO):
        if not 0 < descuento < 1:
            raise DatoInvalidoError("El descuento del convenio debe estar entre 0 y 1.")
        self.base = base
        self.descuento = descuento

    def calcular(self, minutos, entrada=None):
        valor = self.base.calcular(minutos, entrada)
        return int(round(valor * (1 - self.descuento)))


class TarifaMensualidad(EstrategiaTarifa):
    """El vehículo ya pagó la mensualidad: cada estadía se cobra en $0."""

    def __init__(self, valor_mensual):
        if valor_mensual <= 0:
            raise DatoInvalidoError("El valor de la mensualidad debe ser mayor que cero.")
        self.valor_mensual = valor_mensual

    def calcular(self, minutos, entrada=None):
        self._validar_minutos(minutos)
        return 0


def crear_tarifas_por_defecto():
    """Asocia cada tipo de vehículo con su estrategia de cobro (valores de ejemplo)."""
    return {
        "carro": TarifaPorHora(3000),
        "moto": TarifaPorHora(1500),
        "bicicleta": TarifaPlana(1000),
    }


def crear_planes_por_defecto(tarifas_base):
    """Construye los planes de tarifa a partir de las tarifas normales.

    Devuelve {plan: {tipo: estrategia}}. Los planes especiales solo se crean
    para los tipos que tienen valores definidos arriba.
    """
    planes = {PLAN_NORMAL: dict(tarifas_base)}

    planes[PLAN_NOCTURNA] = {
        tipo: TarifaNocturna(base, VALOR_NOCTURNO[tipo])
        for tipo, base in tarifas_base.items() if tipo in VALOR_NOCTURNO
    }
    planes[PLAN_CONVENIO] = {
        tipo: TarifaConvenio(base)
        for tipo, base in tarifas_base.items()
    }
    planes[PLAN_MENSUALIDAD] = {
        tipo: TarifaMensualidad(VALOR_MENSUALIDAD[tipo])
        for tipo in tarifas_base if tipo in VALOR_MENSUALIDAD
    }

    return planes