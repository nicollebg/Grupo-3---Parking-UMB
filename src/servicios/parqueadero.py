"""Servicio principal: controla ingresos, salidas y cobro del parqueadero."""

from datetime import datetime

from modelos.registro import RegistroParqueo
from servicios.tarifas import crear_tarifas_por_defecto
from utilidades.excepciones import (
    DatoInvalidoError,
    ParqueaderoLlenoError,
    VehiculoDuplicadoError,
    VehiculoNoEncontradoError,
)
from utilidades.validaciones import normalizar_placa


class Parqueadero:
    """Contexto del patrón Strategy: delega el cobro en la estrategia del tipo."""

    def __init__(self, capacidad, tarifas=None, reloj=datetime.now):
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise DatoInvalidoError("La capacidad debe ser un número entero mayor que cero.")

        self.capacidad = capacidad
        self._tarifas = tarifas if tarifas is not None else crear_tarifas_por_defecto()
        self._reloj = reloj  # Se inyecta para poder probar con fechas controladas
        self._activos = {}
        self._historial = []

    @property
    def espacios_disponibles(self):
        return self.capacidad - len(self._activos)

    @property
    def registros_activos(self):
        return list(self._activos.values())

    @property
    def historial(self):
        return list(self._historial)

    def registrar_entrada(self, vehiculo):
        if vehiculo.tipo not in self._tarifas:
            raise DatoInvalidoError(f"No hay una tarifa configurada para '{vehiculo.tipo}'.")
        if vehiculo.placa in self._activos:
            raise VehiculoDuplicadoError(f"El vehículo {vehiculo.placa} ya está en el parqueadero.")
        if self.espacios_disponibles == 0:
            raise ParqueaderoLlenoError("No hay espacios disponibles.")

        registro = RegistroParqueo(vehiculo=vehiculo, entrada=self._reloj())
        self._activos[vehiculo.placa] = registro
        return registro

    def registrar_salida(self, placa):
        placa = normalizar_placa(placa)
        registro = self._activos.get(placa)
        if registro is None:
            raise VehiculoNoEncontradoError(f"El vehículo {placa} no está en el parqueadero.")

        registro.salida = self._reloj()
        estrategia = self._tarifas[registro.vehiculo.tipo]
        registro.valor_cobrado = estrategia.calcular(registro.minutos_permanencia())

        del self._activos[placa]
        self._historial.append(registro)
        return registro

    def total_recaudado(self):
        return sum(registro.valor_cobrado for registro in self._historial)