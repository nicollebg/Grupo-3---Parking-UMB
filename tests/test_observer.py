
import unittest

from datetime import datetime, timedelta

import contexto  # noqa: F401

from modelos.vehiculo import Vehiculo

from observadores.observador_parqueadero import (
    ObservadorConsola,
    ObservadorParqueadero,
)

from servicios.parqueadero import Parqueadero
from utilidades.excepciones import DatoInvalidoError


class RelojFalso:

    def __init__(self):
        self.ahora = datetime(2026, 11, 6, 8, 0)

    def __call__(self):
        return self.ahora

    def avanzar(self, **tiempo):
        self.ahora += timedelta(**tiempo)


class ObservadorPrueba:

    def __init__(self):
        self.eventos = []

    def actualizar(self, evento, registro, espacios_disponibles):

        self.eventos.append(
            (evento, registro.vehiculo.placa, espacios_disponibles)
        )


class TestObserver(unittest.TestCase):

    def setUp(self):

        self.reloj = RelojFalso()

        self.parqueadero = Parqueadero(
            2,
            reloj=self.reloj
        )

        self.observador = ObservadorPrueba()

        self.parqueadero.suscribir(self.observador)

    def test_notifica_entrada(self):

        self.parqueadero.registrar_entrada(
            Vehiculo("ABC123", "carro")
        )

        self.assertEqual(
            self.observador.eventos,
            [("entrada", "ABC123", 1)]
        )

    def test_notifica_salida(self):

        self.parqueadero.registrar_entrada(
            Vehiculo("ABC123", "carro")
        )

        self.reloj.avanzar(minutes=30)

        self.parqueadero.registrar_salida("ABC123")

        self.assertEqual(
            self.observador.eventos,
            [
                ("entrada", "ABC123", 1),
                ("salida", "ABC123", 2)
            ]
        )

    def test_no_notifica_dos_veces_al_mismo_observador(self):

        self.parqueadero.suscribir(self.observador)

        self.parqueadero.registrar_entrada(
            Vehiculo("ABC123", "carro")
        )

        self.assertEqual(
            len(self.observador.eventos),
            1
        )

    def test_desuscribir_deja_de_notificar(self):

        self.parqueadero.desuscribir(self.observador)

        self.parqueadero.registrar_entrada(
            Vehiculo("ABC123", "carro")
        )

        self.assertEqual(self.observador.eventos, [])

    def test_rechaza_objeto_sin_actualizar(self):

        with self.assertRaises(DatoInvalidoError):
            self.parqueadero.suscribir(object())

    def test_observador_consola_muestra_notificacion(self):

        mensajes = []

        observador = ObservadorConsola(
            escribir=mensajes.append
        )

        parqueadero = Parqueadero(1, reloj=self.reloj)

        parqueadero.suscribir(observador)

        parqueadero.registrar_entrada(
            Vehiculo("ABC123", "carro")
        )

        self.assertIn(
            "ingreso carro ABC123",
            mensajes[0]
        )

        self.assertIn(
            "Espacios disponibles: 0",
            mensajes[0]
        )

    def test_interfaz_abstracta_no_se_instancia(self):

        with self.assertRaises(TypeError):
            ObservadorParqueadero()


if __name__ == "__main__":
    unittest.main()
