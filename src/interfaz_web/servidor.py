"""Interfaz web del parqueadero (solo biblioteca estandar de Python).

Sirve los archivos de `estaticos/` y expone una pequena API JSON que reutiliza
el mismo servicio `Parqueadero`, la misma `FabricaVehiculos` (Factory Method),
las mismas estrategias de cobro (Strategy) y el `ObservadorEventos` (Observer)
que usa el menu de consola. La interfaz no contiene reglas de negocio.
"""

import json
import mimetypes
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from fabricas.vehiculo_factory import FabricaVehiculos
from modelos.vehiculo import TIPOS_VALIDOS
from observadores.observador_parqueadero import ObservadorEventos
from servicios.parqueadero import Parqueadero
from utilidades.excepciones import ParqueaderoError

RUTA_ESTATICOS = Path(__file__).resolve().parent / "estaticos"
FORMATO_FECHA = "%Y-%m-%d %H:%M"


class ControladorParqueadero:
    """Traduce las peticiones de la interfaz a llamadas al servicio."""

    def __init__(self, parqueadero, observador, fabrica=None):
        self._parqueadero = parqueadero
        self._observador = observador
        self._fabrica = fabrica or FabricaVehiculos()
        self._candado = threading.Lock()

    def estado(self):
        with self._candado:
            p = self._parqueadero
            activos = [
                {
                    "placa": r.vehiculo.placa,
                    "tipo": r.vehiculo.tipo,
                    "entrada": r.entrada.strftime(FORMATO_FECHA),
                    "minutos": round(r.minutos_permanencia(p.ahora())),
                    "estimado": p.estimar_cobro(r),
                }
                for r in p.registros_activos
            ]
            historial = [self._serializar(r) for r in reversed(p.historial)]
            return {
                "capacidad": p.capacidad,
                "disponibles": p.espacios_disponibles,
                "ocupados": p.capacidad - p.espacios_disponibles,
                "recaudado": p.total_recaudado(),
                "tipos": list(TIPOS_VALIDOS),
                "activos": activos,
                "historial": historial,
                "eventos": self._observador.eventos,
            }

    def entrada(self, datos):
        with self._candado:
            vehiculo = self._fabrica.crear(
                datos.get("placa", ""), datos.get("tipo", "")
            )
            registro = self._parqueadero.registrar_entrada(vehiculo)
            return self._serializar(registro)

    def salida(self, datos):
        with self._candado:
            registro = self._parqueadero.registrar_salida(
                datos.get("placa", "")
            )
            return self._serializar(registro)

    @staticmethod
    def _serializar(registro):
        return {
            "placa": registro.vehiculo.placa,
            "tipo": registro.vehiculo.tipo,
            "entrada": registro.entrada.strftime(FORMATO_FECHA),
            "salida": (
                registro.salida.strftime(FORMATO_FECHA)
                if registro.salida else None
            ),
            "minutos": (
                round(registro.minutos_permanencia())
                if registro.salida else None
            ),
            "valor": registro.valor_cobrado,
        }


def crear_manejador(controlador):
    """Crea la clase manejadora de peticiones ligada a un controlador."""

    class Manejador(BaseHTTPRequestHandler):

        def log_message(self, formato, *args):
            pass  # consola limpia

        # ---------- GET ----------
        def do_GET(self):
            ruta = self.path.split("?", 1)[0]

            if ruta == "/api/estado":
                return self._json(HTTPStatus.OK, controlador.estado())

            self._archivo(ruta)

        # ---------- POST ----------
        def do_POST(self):
            acciones = {
                "/api/entrada": controlador.entrada,
                "/api/salida": controlador.salida,
            }
            accion = acciones.get(self.path)

            if accion is None:
                return self._json(
                    HTTPStatus.NOT_FOUND, {"error": "Ruta no encontrada."}
                )

            try:
                largo = int(self.headers.get("Content-Length", 0))
                datos = json.loads(self.rfile.read(largo) or b"{}")
                if not isinstance(datos, dict):
                    raise ValueError
            except (ValueError, json.JSONDecodeError):
                return self._json(
                    HTTPStatus.BAD_REQUEST, {"error": "Datos no válidos."}
                )

            try:
                resultado = accion(datos)
            except ParqueaderoError as error:
                return self._json(
                    HTTPStatus.BAD_REQUEST, {"error": self._legible(error)}
                )

            self._json(HTTPStatus.OK, resultado)

        # ---------- utilidades ----------
        @staticmethod
        def _legible(error):
            return (
                str(error)
                .replace("El vehiculo ", "El vehículo ")
                .replace("no esta en el parqueadero", "no está en el parqueadero")
                .replace("ya esta en el parqueadero", "ya está en el parqueadero")
            )

        def _json(self, estado, cuerpo):
            datos = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
            self.send_response(estado)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(datos)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(datos)

        def _archivo(self, ruta):
            nombre = "index.html" if ruta in ("", "/") else ruta.lstrip("/")
            destino = (RUTA_ESTATICOS / nombre).resolve()

            # Evita salir de la carpeta de estaticos (../)
            if RUTA_ESTATICOS not in destino.parents or not destino.is_file():
                return self._json(
                    HTTPStatus.NOT_FOUND, {"error": "No encontrado."}
                )

            tipo = mimetypes.guess_type(destino.name)[0] or "application/octet-stream"
            contenido = destino.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", f"{tipo}; charset=utf-8")
            self.send_header("Content-Length", str(len(contenido)))
            self.end_headers()
            self.wfile.write(contenido)

    return Manejador


def crear_servidor(capacidad, host="127.0.0.1", puerto=8000):
    """Arma el servicio completo y devuelve (servidor, controlador)."""
    parqueadero = Parqueadero(capacidad)
    observador = ObservadorEventos()
    parqueadero.suscribir(observador)

    controlador = ControladorParqueadero(parqueadero, observador)
    servidor = ThreadingHTTPServer((host, puerto), crear_manejador(controlador))
    return servidor, controlador