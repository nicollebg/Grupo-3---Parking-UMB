import json
import threading
import unittest
import urllib.error
import urllib.request

import contexto  # noqa: F401

from interfaz_web.servidor import crear_servidor
from observadores.observador_parqueadero import ObservadorEventos


class TestInterfazWeb(unittest.TestCase):
    """Prueba la API de la interfaz web contra un servidor real en un puerto libre."""

    @classmethod
    def setUpClass(cls):
        cls.servidor, _ = crear_servidor(2, puerto=0)
        cls.base = f"http://127.0.0.1:{cls.servidor.server_address[1]}"
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()

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
        self.assertEqual(r["placa"], "ABC123")

        _, e = self.llamar("/api/estado")
        self.assertEqual(e["ocupados"], 1)
        self.assertEqual(e["activos"][0]["estimado"], 3000)

        estado, r = self.llamar("/api/salida", {"placa": "ABC123"})
        self.assertEqual(estado, 200)
        self.assertEqual(r["valor"], 3000)

        _, e = self.llamar("/api/estado")
        self.assertEqual(e["recaudado"], 3000)
        self.assertEqual([x["evento"] for x in e["eventos"]], ["salida", "entrada"])

    def test_errores_devuelven_400_con_mensaje(self):
        estado, r = self.llamar("/api/entrada", {"placa": "!!", "tipo": "carro"})
        self.assertEqual(estado, 400)
        self.assertIn("placa", r["error"].lower())

        estado, r = self.llamar("/api/salida", {"placa": "NOEXI1"})
        self.assertEqual(estado, 400)
        self.assertIn("no está en el parqueadero", r["error"])

        estado, _ = self.llamar("/api/entrada", {"placa": "ABC123", "tipo": "avion"})
        self.assertEqual(estado, 400)

    def test_sirve_pagina_y_bloquea_rutas_externas(self):
        with urllib.request.urlopen(self.base + "/") as resp:
            self.assertIn("PARKING UMB", resp.read().decode())

        estado, _ = self.llamar("/../servidor.py")
        self.assertEqual(estado, 404)


class TestObservadorEventos(unittest.TestCase):

    def test_guarda_eventos_recientes_primero(self):
        from datetime import datetime
        from modelos.vehiculo import Vehiculo
        from modelos.registro import RegistroParqueo

        obs = ObservadorEventos(maximo=2)
        reg = RegistroParqueo(Vehiculo("ABC123", "moto"), datetime(2026, 11, 6, 8))
        obs.actualizar("entrada", reg, 4)
        obs.actualizar("salida", reg, 5)
        obs.actualizar("otro", reg, 5)  # se ignora
        obs.actualizar("entrada", reg, 4)

        self.assertEqual([e["evento"] for e in obs.eventos], ["entrada", "salida"])


if __name__ == "__main__":
    unittest.main()