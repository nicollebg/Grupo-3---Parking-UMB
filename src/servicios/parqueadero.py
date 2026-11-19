
"""Servicio principal del sistema de parqueadero."""

from datetime import date, datetime

from modelos.registro import RegistroParqueo
from servicios.tarifas import (
    PLAN_NORMAL,
    crear_planes_por_defecto,
    crear_tarifas_por_defecto,
)

from utilidades.excepciones import (
    DatoInvalidoError,
    EspacioNoDisponibleError,
    ParqueaderoLlenoError,
    VehiculoDuplicadoError,
    VehiculoNoEncontradoError,
)

from utilidades.validaciones import normalizar_placa


class Parqueadero:
    """Gestiona el parqueadero, sus espacios numerados y notifica sus eventos."""

    def __init__(self, capacidad, tarifas=None, reloj=datetime.now, planes=None):

        if not isinstance(capacidad, int) or capacidad <= 0:
            raise DatoInvalidoError(
                "La capacidad debe ser un numero entero mayor que cero."
            )

        self.capacidad = capacidad

        self._tarifas = (
            tarifas if tarifas is not None
            else crear_tarifas_por_defecto()
        )

        # Strategy: {plan: {tipo: estrategia}}. "normal" son las tarifas base.
        self._planes = (
            planes if planes is not None
            else crear_planes_por_defecto(self._tarifas)
        )

        self._reloj = reloj
        self._activos = {}
        self._historial = []

        # Lista de observadores suscritos
        self._observadores = []

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    @property
    def espacios_disponibles(self):
        return self.capacidad - len(self._activos)

    @property
    def registros_activos(self):
        return list(self._activos.values())

    @property
    def historial(self):
        return list(self._historial)

    @property
    def planes_disponibles(self):
        return tuple(self._planes)

    @property
    def espacios_libres(self):
        """Numeros de los espacios libres (1..capacidad), en orden."""
        ocupados = {registro.espacio for registro in self._activos.values()}
        return [n for n in range(1, self.capacidad + 1) if n not in ocupados]

    def mapa_espacios(self):
        """Lista de (numero, registro) para cada espacio; registro es None si esta libre."""
        por_espacio = {r.espacio: r for r in self._activos.values()}
        return [(n, por_espacio.get(n)) for n in range(1, self.capacidad + 1)]

    def ahora(self):
        """Hora actual segun el reloj inyectado."""
        return self._reloj()

    # ------------------------------------------------------------------
    # Observer
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------------
    def _estrategia(self, tipo, plan):
        """Strategy: devuelve la estrategia de cobro del tipo y plan dados."""

        if plan not in self._planes:
            raise DatoInvalidoError(
                f"Plan de tarifa no valido. Planes: {', '.join(self._planes)}."
            )

        estrategia = self._planes[plan].get(tipo)

        if estrategia is None:
            raise DatoInvalidoError(
                f"No hay una tarifa configurada para '{tipo}'."
            )

        return estrategia

    def _asignar_espacio(self, espacio):
        """Devuelve el espacio a usar: el pedido (si esta libre) o el primero libre."""

        libres = self.espacios_libres

        if espacio is None:
            return libres[0]

        if isinstance(espacio, bool) or not isinstance(espacio, int) \
                or not 1 <= espacio <= self.capacidad:
            raise DatoInvalidoError(
                f"El espacio debe ser un numero entre 1 y {self.capacidad}."
            )

        if espacio not in libres:
            raise EspacioNoDisponibleError(
                f"El espacio {espacio} ya esta ocupado."
            )

        return espacio

    def registrar_entrada(self, vehiculo, plan=PLAN_NORMAL, espacio=None):

        # Valida que exista estrategia para el tipo y el plan elegido
        self._estrategia(vehiculo.tipo, plan)

        if vehiculo.placa in self._activos:
            raise VehiculoDuplicadoError(
                f"El vehiculo {vehiculo.placa} ya esta en el parqueadero."
            )

        if self.espacios_disponibles == 0:
            raise ParqueaderoLlenoError(
                "No hay espacios disponibles."
            )

        numero = self._asignar_espacio(espacio)

        registro = RegistroParqueo(
            vehiculo=vehiculo,
            entrada=self._reloj(),
            espacio=numero,
            plan=plan,
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
        estrategia = self._estrategia(registro.vehiculo.tipo, registro.plan)

        registro.valor_cobrado = estrategia.calcular(
            registro.minutos_permanencia(),
            registro.entrada,
        )

        del self._activos[placa]

        self._historial.append(registro)

        # Notificar despues de registrar correctamente la salida
        self._notificar("salida", registro)

        return registro

    def estimar_cobro(self, registro, hasta=None):
        """Valor que se cobraria hoy a un registro activo (Strategy, sin cerrar la estadia)."""

        estrategia = self._estrategia(registro.vehiculo.tipo, registro.plan)

        return estrategia.calcular(
            registro.minutos_permanencia(hasta or self._reloj()),
            registro.entrada,
        )

    def total_recaudado(self):

        return sum(
            registro.valor_cobrado
            for registro in self._historial
        )

    # ------------------------------------------------------------------
    # Reportes
    # ------------------------------------------------------------------
    def fechas_con_movimientos(self):
        """Fechas (date) en las que hubo salidas, de la mas reciente a la mas antigua."""

        return sorted(
            {registro.salida.date() for registro in self._historial},
            reverse=True,
        )

    def reporte_por_fecha(self, fecha=None):
        """Resumen de las salidas de un dia (por defecto, hoy).

        Devuelve un diccionario con el total, y el desglose por tipo y por plan.
        """

        if fecha is None:
            fecha = self._reloj().date()

        if isinstance(fecha, datetime):
            fecha = fecha.date()

        if not isinstance(fecha, date):
            raise DatoInvalidoError("La fecha del reporte no es valida.")

        registros = [
            r for r in self._historial if r.salida.date() == fecha
        ]

        def agrupar(clave):
            grupos = {}
            for r in registros:
                grupo = grupos.setdefault(clave(r), {"cantidad": 0, "total": 0})
                grupo["cantidad"] += 1
                grupo["total"] += r.valor_cobrado
            return grupos

        return {
            "fecha": fecha.isoformat(),
            "salidas": len(registros),
            "total": sum(r.valor_cobrado for r in registros),
            "por_tipo": agrupar(lambda r: r.vehiculo.tipo),
            "por_plan": agrupar(lambda r: r.plan),
            "registros": registros,
        }