"""Menú de consola: capa de presentación que se apoya en el servicio Parqueadero."""

from modelos.vehiculo import TIPOS_VALIDOS, Vehiculo
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
    def __init__(self, parqueadero, leer=input, escribir=print):
        self._parqueadero = parqueadero
        self._leer = leer
        self._escribir = escribir
        self._acciones = {
            "1": self._registrar_entrada,
            "2": self._registrar_salida,
            "3": self._consultar_disponibilidad,
            "4": self._mostrar_estacionados,
            "5": self._mostrar_historial,
        }

    def ejecutar(self):
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
                self._escribir(f"Error: {error}")

    def _mostrar_menu(self):
        self._escribir("\n===== SISTEMA DE GESTIÓN DE PARQUEADERO =====")
        for opcion in OPCIONES:
            self._escribir(opcion)

    def _registrar_entrada(self):
        placa = self._leer("Ingrese la placa: ")
        tipo = self._leer(f"Ingrese el tipo de vehículo ({', '.join(TIPOS_VALIDOS)}): ")

        registro = self._parqueadero.registrar_entrada(Vehiculo(placa, tipo))
        self._escribir(f"Vehículo registrado correctamente: {registro.mostrar_informacion()}")

    def _registrar_salida(self):
        placa = self._leer("Ingrese la placa del vehículo que sale: ")

        registro = self._parqueadero.registrar_salida(placa)
        minutos = round(registro.minutos_permanencia())
        self._escribir(f"Permanencia: {minutos} minutos.")
        self._escribir(f"Valor a pagar: ${registro.valor_cobrado:,}")

    def _consultar_disponibilidad(self):
        disponibles = self._parqueadero.espacios_disponibles
        self._escribir(f"Espacios disponibles: {disponibles} de {self._parqueadero.capacidad}")

    def _mostrar_estacionados(self):
        self._escribir("\n--- VEHÍCULOS EN EL PARQUEADERO ---")
        self._mostrar_lista(self._parqueadero.registros_activos, "No hay vehículos estacionados.")

    def _mostrar_historial(self):
        self._escribir("\n--- HISTORIAL DE SALIDAS ---")
        self._mostrar_lista(self._parqueadero.historial, "Aún no hay salidas registradas.")
        self._escribir(f"Total recaudado: ${self._parqueadero.total_recaudado():,}")

    def _mostrar_lista(self, registros, mensaje_vacio):
        if not registros:
            self._escribir(mensaje_vacio)
            return
        for registro in registros:
            self._escribir(registro.mostrar_informacion())