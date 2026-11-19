import json
import threading
import unittest
import urllib.error
import urllib.request
from datetime import datetime, timedelta

import contexto  # noqa: F401

from interfaz_web.servidor import crear_servidor
from modelos.registro import RegistroParqueo
from modelos.vehiculo import Vehiculo
from observadores.observador_parqueadero import ObservadorEventos


class RelojFalso:
    def __init__(self):
        self.ahora = datetime(2026, 11, 6, 21, 0)  # 9:00 p.m. (horario nocturno)

    def __call__(self):
        return self.ahora

    def avanzar(self, **tiempo):
        self.ahora += timedelta(**tiempo)


class TestInterfazWeb(unittest.TestCase):
    """Prueba la API de la interfaz web contra un servidor real en un puerto libre."""

    def setUp(self):
        self.reloj = RelojFalso()
        self.servidor, _ = crear_servidor(3, puerto=0, reloj=self.reloj)
        self.base = f"http://127.0.0.1:{self.servidor.server_address[1]}"
        threading.Thread(target=self.servidor.serve_forever, daemon=True).start()

    def tearDown(self):
        self.servidor.shutdown()
        self.servidor.server_close()

    def llamar(self, ruta, cuerpo=None):
        datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
        peticion = urllib.request.Request(
            self.base + ruta, data=datos,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(peticion) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def test_flujo_completo(self):
        # Entrada (Factory Method), estado, salida con cobro (Strategy) y evento (Observer)
        estado, r = self.llamar("/api/entrada", {"placa": "abc123", "tipo": "carro"})
        self.assertEqual(estado, 200)
        self.assertEqual((r["placa"], r["espacio"], r["plan"]), ("ABC123", 1, "normal"))

        _, e = self.llamar("/api/estado")
        self.assertEqual(e["ocupados"], 1)
        self.assertEqual(e["activos"][0]["estimado"], 3000)
        self.assertEqual(e["libres"], [2, 3])

        estado, r = self.llamar("/api/salida", {"placa": "ABC123"})
        self.assertEqual(estado, 200)
        self.assertEqual(r["valor"], 3000)

        _, e = self.llamar("/api/estado")
        self.assertEqual(e["recaudado"], 3000)
        self.assertEqual([x["evento"] for x in e["eventos"]], ["salida", "entrada"])

    def test_plan_y_espacio_elegidos(self):
        estado, r = self.llamar(
            "/api/entrada",
            {"placa": "ABC12D", "tipo": "moto", "plan": "nocturna", "espacio": "3"},
        )
        self.assertEqual(estado, 200)
        self.assertEqual((r["espacio"], r["plan"]), (3, "nocturna"))

        self.reloj.avanzar(hours=2)
        _, salida = self.llamar("/api/salida", {"placa": "ABC12D"})
        self.assertEqual(salida["valor"], 5000)

    def test_errores_devuelven_400_con_mensaje(self):
        casos = [
            ({"placa": "!!", "tipo": "carro"}, "placa"),
            ({"placa": "ABC123", "tipo": "moto"}, "moto"),           # placa de carro en moto
            ({"placa": "ABC12D", "tipo": "carro"}, "carro"),         # placa de moto en carro
            ({"placa": "ABC123", "tipo": "avion"}, "tipo"),
            ({"placa": "ABC123", "tipo": "carro", "plan": "vip"}, "plan"),
            ({"placa": "ABC123", "tipo": "carro", "espacio": 9}, "espacio"),
            ({"placa": "ABC123", "tipo": "carro", "espacio": "x"}, "espacio"),
        ]
        for cuerpo, texto in casos:
            with self.subTest(cuerpo=cuerpo):
                estado, r = self.llamar("/api/entrada", cuerpo)
                self.assertEqual(estado, 400)
                self.assertIn(texto, r["error"].lower())

        estado, r = self.llamar("/api/salida", {"placa": "NOEXI1"})
        self.assertEqual(estado, 400)
        self.assertIn("no está en el parqueadero", r["error"])

    def test_espacio_ocupado(self):
        self.llamar("/api/entrada", {"placa": "ABC123", "tipo": "carro", "espacio": 2})
        estado, r = self.llamar(
            "/api/entrada", {"placa": "DEF456", "tipo": "carro", "espacio": 2}
        )
        self.assertEqual(estado, 400)
        self.assertIn("ocupado", r["error"])

    def test_reporte_por_fecha(self):
        self.llamar("/api/entrada", {"placa": "ABC123", "tipo": "carro"})
        self.llamar("/api/salida", {"placa": "ABC123"})

        estado, r = self.llamar("/api/reporte?fecha=2026-11-06")
        self.assertEqual(estado, 200)
        self.assertEqual((r["salidas"], r["total"]), (1, 3000))
        self.assertEqual(r["por_tipo"], [{"tipo": "carro", "cantidad": 1, "total": 3000}])
        self.assertEqual(r["fechas"], ["2026-11-06"])

        _, otro_dia = self.llamar("/api/reporte?fecha=2026-11-07")
        self.assertEqual(otro_dia["salidas"], 0)

        _, hoy = self.llamar("/api/reporte")
        self.assertEqual(hoy["fecha"], "2026-11-06")

        estado, _ = self.llamar("/api/reporte?fecha=hoy")
        self.assertEqual(estado, 400)

    def test_sirve_pagina_y_bloquea_rutas_externas(self):
        with urllib.request.urlopen(self.base + "/") as resp:
            self.assertIn("PARKING UMB", resp.read().decode())

        estado, _ = self.llamar("/../servidor.py")
        self.assertEqual(estado, 404)


class TestObservadorEventos(unittest.TestCase):

    def test_guarda_eventos_recientes_primero(self):
        obs = ObservadorEventos(maximo=2)
        reg = RegistroParqueo(Vehiculo("ABC12D", "moto"), datetime(2026, 11, 6, 8))
        obs.actualizar("entrada", reg, 4)
        obs.actualizar("salida", reg, 5)
        obs.actualizar("otro", reg, 5)  # se ignora
        obs.actualizar("entrada", reg, 4)

        self.assertEqual([e["evento"] for e in obs.eventos], ["entrada", "salida"])


if __name__ == "__main__":
    unittest.main()