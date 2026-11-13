
"""Servicio principal del sistema de parqueadero."""

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
    """Gestiona el parqueadero y notifica sus eventos."""

    def __init__(self, capacidad, tarifas=None, reloj=datetime.now):

        if not isinstance(capacidad, int) or capacidad <= 0:
            raise DatoInvalidoError(
                "La capacidad debe ser un numero entero mayor que cero."
            )

        self.capacidad = capacidad

        self._tarifas = (
            tarifas if tarifas is not None
            else crear_tarifas_por_defecto()
        )

        self._reloj = reloj
        self._activos = {}
        self._historial = []

        # Lista de observadores suscritos
        self._observadores = []

    @property
    def espacios_disponibles(self):
        return self.capacidad - len(self._activos)

    @property
    def registros_activos(self):
        return list(self._activos.values())

    @property
    def historial(self):
        return list(self._historial)

    # Observer: suscribir observadores
    def suscribir(self, observador):

        if not callable(getattr(observador, "actualizar", None)):
            raise DatoInvalidoError(
                "El observador debe implementar el metodo actualizar()."
            )

        if observador not in self._observadores:
            self._observadores.append(observador)

    # Observer: eliminar observadores
    def desuscribir(self, observador):

        if observador in self._observadores:
            self._observadores.remove(observador)

    # Observer: enviar notificaciones
    def _notificar(self, evento, registro):

        for observador in tuple(self._observadores):

            observador.actualizar(
                evento,
                registro,
                self.espacios_disponibles
            )

    def registrar_entrada(self, vehiculo):

        if vehiculo.tipo not in self._tarifas:
            raise DatoInvalidoError(
                f"No hay una tarifa configurada para '{vehiculo.tipo}'."
            )

        if vehiculo.placa in self._activos:
            raise VehiculoDuplicadoError(
                f"El vehiculo {vehiculo.placa} ya esta en el parqueadero."
            )

        if self.espacios_disponibles == 0:
            raise ParqueaderoLlenoError(
                "No hay espacios disponibles."
            )

        registro = RegistroParqueo(
            vehiculo=vehiculo,
            entrada=self._reloj()
        )

        self._activos[vehiculo.placa] = registro

        # Notificar despues de registrar correctamente la entrada
        self._notificar("entrada", registro)

        return registro

    def registrar_salida(self, placa):

        placa = normalizar_placa(placa)

        registro = self._activos.get(placa)

        if registro is None:
            raise VehiculoNoEncontradoError(
                f"El vehiculo {placa} no esta en el parqueadero."
            )

        registro.salida = self._reloj()

        # Se conserva el patron Strategy
        estrategia = self._tarifas[registro.vehiculo.tipo]

        registro.valor_cobrado = estrategia.calcular(
            registro.minutos_permanencia()
        )

        del self._activos[placa]

        self._historial.append(registro)

        # Notificar despues de registrar correctamente la salida
        self._notificar("salida", registro)

        return registro

    def total_recaudado(self):

        return sum(
            registro.valor_cobrado
            for registro in self._historial
        )
