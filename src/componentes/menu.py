
"""Menu de consola del sistema de parqueadero."""

from modelos.vehiculo import TIPOS_VALIDOS
from fabricas.vehiculo_factory import FabricaVehiculos
from utilidades.excepciones import ParqueaderoError


OPCIONES = (
    "1. Registrar entrada de vehículo",
    "2. Registrar salida y cobrar",
    "3. Consultar disponibilidad",
    "4. Mostrar vehículos estacionados",
    "5. Ver historial y total recaudado",
    "6. Salir",
)


class MenuConsola:
    """Gestiona la interacción entre el usuario y el parqueadero."""

    def __init__(
        self,
        parqueadero,
        leer=input,
        escribir=print,
        fabrica_vehiculos=None
    ):
        self._parqueadero = parqueadero
        self._leer = leer
        self._escribir = escribir

        # Factory Method: fábrica encargada de crear los vehículos
        self._fabrica_vehiculos = (
            fabrica_vehiculos or FabricaVehiculos()
        )

        self._acciones = {
            "1": self._registrar_entrada,
            "2": self._registrar_salida,
            "3": self._consultar_disponibilidad,
            "4": self._mostrar_estacionados,
            "5": self._mostrar_historial,
        }

    def ejecutar(self):
        """Muestra el menú y ejecuta la opción seleccionada."""

        while True:
            self._mostrar_menu()

            try:
                opcion = self._leer("Seleccione una opción: ").strip()
            except EOFError:
                opcion = "6"

            if opcion == "6":
                self._escribir("Cerrando el sistema...")
                return

            accion = self._acciones.get(opcion)

            if accion is None:
                self._escribir("Opción no válida.")
                continue

            try:
                accion()
            except ParqueaderoError as error:
                self._mostrar_error(error)

    def _mostrar_menu(self):
        """Muestra las opciones disponibles."""

        self._escribir(
            "\n===== SISTEMA DE GESTIÓN DE PARQUEADERO ====="
        )

        for opcion in OPCIONES:
            self._escribir(opcion)

    def _mostrar_error(self, error):
        """Muestra los errores con mensajes legibles."""

        mensaje = str(error)

        mensaje = mensaje.replace(
            "El vehiculo ",
            "El vehículo "
        )

        mensaje = mensaje.replace(
            "no esta en el parqueadero",
            "no está en el parqueadero"
        )

        self._escribir(f"Error: {mensaje}")

    def _registrar_entrada(self):
        """Registra el ingreso de un vehículo."""

        placa = self._leer("Ingrese la placa: ")

        tipo = self._leer(
            f"Ingrese el tipo de vehículo "
            f"({', '.join(TIPOS_VALIDOS)}): "
        )

        # Factory Method crea el vehículo
        vehiculo = self._fabrica_vehiculos.crear(
            placa,
            tipo
        )

        registro = self._parqueadero.registrar_entrada(
            vehiculo
        )

        self._escribir(
            f"Vehículo registrado correctamente: "
            f"{registro.mostrar_informacion()}"
        )

    def _registrar_salida(self):
        """Registra la salida y muestra el valor a pagar."""

        placa = self._leer(
            "Ingrese la placa del vehículo que sale: "
        )

        registro = self._parqueadero.registrar_salida(
            placa
        )

        minutos = round(registro.minutos_permanencia())

        self._escribir(
            f"Permanencia: {minutos} minutos."
        )

        self._escribir(
            f"Valor a pagar: ${registro.valor_cobrado:,}"
        )

    def _consultar_disponibilidad(self):
        """Muestra los espacios disponibles."""

        disponibles = self._parqueadero.espacios_disponibles

        self._escribir(
            f"Espacios disponibles: {disponibles} "
            f"de {self._parqueadero.capacidad}"
        )

    def _mostrar_estacionados(self):
        """Muestra los vehículos que están actualmente dentro."""

        self._escribir(
            "\n--- VEHÍCULOS EN EL PARQUEADERO ---"
        )

        self._mostrar_lista(
            self._parqueadero.registros_activos,
            "No hay vehículos estacionados."
        )

    def _mostrar_historial(self):
        """Muestra el historial y el total recaudado."""

        self._escribir(
            "\n--- HISTORIAL DE SALIDAS ---"
        )

        self._mostrar_lista(
            self._parqueadero.historial,
            "Aún no hay salidas registradas."
        )

        self._escribir(
            f"Total recaudado: "
            f"${self._parqueadero.total_recaudado():,}"
        )

    def _mostrar_lista(self, registros, mensaje_vacio):
        """Muestra una lista de registros."""

        if not registros:
            self._escribir(mensaje_vacio)
            return

        for registro in registros:
            self._escribir(
                registro.mostrar_informacion()
            )
