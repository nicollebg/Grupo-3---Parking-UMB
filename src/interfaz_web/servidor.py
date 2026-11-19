"""Interfaz web del parqueadero (solo biblioteca estandar de Python).

Sirve los archivos de `estaticos/` y expone una pequena API JSON que reutiliza
el mismo servicio `Parqueadero`, la misma `FabricaVehiculos` (Factory Method),
las mismas estrategias de cobro (Strategy) y el `ObservadorEventos` (Observer)
que usa el menu de consola. La interfaz no contiene reglas de negocio.
"""

import json
import mimetypes
import threading
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from fabricas.vehiculo_factory import FabricaVehiculos
from modelos.vehiculo import TIPOS_VALIDOS
from observadores.observador_parqueadero import ObservadorEventos
from servicios import tarifas
from servicios.parqueadero import Parqueadero
from utilidades.excepciones import DatoInvalidoError, ParqueaderoError

RUTA_ESTATICOS = Path(__file__).resolve().parent / "estaticos"
FORMATO_FECHA = "%Y-%m-%d %H:%M"


def pesos(valor):
    """Formato de moneda colombiano: 8000 -> $8.000"""
    return "$" + f"{valor:,}".replace(",", ".")


def descripcion_planes():
    """Texto de cada plan de tarifa, construido con los valores reales."""
    n = tarifas.VALOR_NOCTURNO
    m = tarifas.VALOR_MENSUALIDAD
    return [
        {"clave": tarifas.PLAN_NORMAL, "nombre": "Normal",
         "descripcion": "Carro y moto por hora o fracción; bicicleta tarifa plana."},
        {"clave": tarifas.PLAN_NOCTURNA, "nombre": "Nocturna",
         "descripcion": (
             f"Si entra entre las {tarifas.HORA_INICIO_NOCTURNA}:00 y las "
             f"{tarifas.HORA_FIN_NOCTURNA}:00 paga un valor fijo: carro {pesos(n['carro'])}, "
             f"moto {pesos(n['moto'])}, bicicleta {pesos(n['bicicleta'])}.")},
        {"clave": tarifas.PLAN_CONVENIO, "nombre": "Convenio",
         "descripcion": f"{round(tarifas.DESCUENTO_CONVENIO * 100)}% de descuento sobre la tarifa normal."},
        {"clave": tarifas.PLAN_MENSUALIDAD, "nombre": "Mensualidad",
         "descripcion": (
             f"Mes pagado (carro {pesos(m['carro'])}, moto {pesos(m['moto'])}, "
             f"bicicleta {pesos(m['bicicleta'])}): cada salida cuesta $0.")},
    ]


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
            ahora = p.ahora()
            espacios = []
            activos = []
            for numero, registro in p.mapa_espacios():
                if registro is None:
                    espacios.append({"numero": numero, "registro": None})
                    continue
                datos = self._serializar(registro)
                datos["minutos"] = round(registro.minutos_permanencia(ahora))
                datos["estimado"] = p.estimar_cobro(registro)
                espacios.append({"numero": numero, "registro": datos})
                activos.append(datos)

            historial = [self._serializar(r) for r in reversed(p.historial)]
            return {
                "capacidad": p.capacidad,
                "disponibles": p.espacios_disponibles,
                "ocupados": p.capacidad - p.espacios_disponibles,
                "recaudado": p.total_recaudado(),
                "tipos": list(TIPOS_VALIDOS),
                "planes": descripcion_planes(),
                "espacios": espacios,
                "libres": p.espacios_libres,
                "activos": activos,
                "historial": historial,
                "eventos": self._observador.eventos,
            }

    def entrada(self, datos):
        with self._candado:
            vehiculo = self._fabrica.crear(
                datos.get("placa", ""), datos.get("tipo", "")
            )
            registro = self._parqueadero.registrar_entrada(
                vehiculo,
                plan=datos.get("plan") or tarifas.PLAN_NORMAL,
                espacio=self._leer_espacio(datos.get("espacio")),
            )
            return self._serializar(registro)

    def salida(self, datos):
        with self._candado:
            registro = self._parqueadero.registrar_salida(
                datos.get("placa", "")
            )
            return self._serializar(registro)

    def reporte(self, texto_fecha=None):
        with self._candado:
            fecha = None
            if texto_fecha:
                try:
                    fecha = date.fromisoformat(texto_fecha)
                except ValueError:
                    raise DatoInvalidoError("La fecha debe tener el formato AAAA-MM-DD.")

            r = self._parqueadero.reporte_por_fecha(fecha)
            return {
                "fecha": r["fecha"],
                "salidas": r["salidas"],
                "total": r["total"],
                "por_tipo": [{"tipo": k, **v} for k, v in r["por_tipo"].items()],
                "por_plan": [{"plan": k, **v} for k, v in r["por_plan"].items()],
                "registros": [self._serializar(x) for x in r["registros"]],
                "fechas": [f.isoformat() for f in self._parqueadero.fechas_con_movimientos()],
            }

    @staticmethod
    def _leer_espacio(valor):
        """El espacio llega como numero, texto o vacio (= asignar automaticamente)."""
        if valor in (None, ""):
            return None
        try:
            return int(valor)
        except (TypeError, ValueError):
            raise DatoInvalidoError("El espacio debe ser un numero.")

    @staticmethod
    def _serializar(registro):
        return {
            "placa": registro.vehiculo.placa,
            "tipo": registro.vehiculo.tipo,
            "plan": registro.plan,
            "espacio": registro.espacio,
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
            url = urlsplit(self.path)

            if url.path == "/api/estado":
                return self._json(HTTPStatus.OK, controlador.estado())

            if url.path == "/api/reporte":
                fecha = parse_qs(url.query).get("fecha", [None])[0]
                try:
                    return self._json(HTTPStatus.OK, controlador.reporte(fecha))
                except ParqueaderoError as error:
                    return self._json(
                        HTTPStatus.BAD_REQUEST, {"error": self._legible(error)}
                    )

            self._archivo(url.path)

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
                .replace("ya esta ocupado", "ya está ocupado")
                .replace("numero", "número")
                .replace("valido", "válido")
                .replace("es valida", "es válida")
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
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(contenido)

    return Manejador


def crear_servidor(capacidad, host="127.0.0.1", puerto=8000, reloj=None):
    """Arma el servicio completo y devuelve (servidor, controlador)."""
    parqueadero = Parqueadero(capacidad, reloj=reloj) if reloj else Parqueadero(capacidad)
    observador = ObservadorEventos()
    parqueadero.suscribir(observador)

    controlador = ControladorParqueadero(parqueadero, observador)
    servidor = ThreadingHTTPServer((host, puerto), crear_manejador(controlador))
    return servidor, controlador