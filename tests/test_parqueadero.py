import unittest
from datetime import datetime, timedelta

import contexto  # noqa: F401

from modelos.vehiculo import Vehiculo
from servicios.parqueadero import Parqueadero
from servicios.tarifas import TarifaPlana
from utilidades.excepciones import (
    DatoInvalidoError,
    ParqueaderoLlenoError,
    VehiculoDuplicadoError,
    VehiculoNoEncontradoError,
)


class RelojFalso:
    """Reloj controlado para probar tiempos de permanencia sin esperar."""

    def __init__(self):
        self.ahora = datetime(2026, 11, 6, 8, 0)

    def __call__(self):
        return self.ahora

    def avanzar(self, **tiempo):
        self.ahora += timedelta(**tiempo)


class TestParqueadero(unittest.TestCase):
    def setUp(self):
        self.reloj = RelojFalso()
        self.parqueadero = Parqueadero(2, reloj=self.reloj)

    def test_capacidad_invalida(self):
        for capacidad in (0, -3, "5", None):
            with self.subTest(capacidad=capacidad):
                with self.assertRaises(DatoInvalidoError):
                    Parqueadero(capacidad)

    def test_registrar_entrada_reduce_espacios(self):
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"))
        self.assertEqual(self.parqueadero.espacios_disponibles, 1)
        self.assertEqual(len(self.parqueadero.registros_activos), 1)

    def test_no_supera_la_capacidad(self):
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"))
        self.parqueadero.registrar_entrada(Vehiculo("DEF456", "moto"))
        with self.assertRaises(ParqueaderoLlenoError):
            self.parqueadero.registrar_entrada(Vehiculo("GHI789", "carro"))
        self.assertEqual(self.parqueadero.espacios_disponibles, 0)

    def test_no_permite_placa_duplicada(self):
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"))
        with self.assertRaises(VehiculoDuplicadoError):
            self.parqueadero.registrar_entrada(Vehiculo("abc123", "moto"))

    def test_salida_calcula_cobro_y_libera_espacio(self):
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"))
        self.reloj.avanzar(hours=2, minutes=10)

        registro = self.parqueadero.registrar_salida("abc123")

        self.assertEqual(registro.valor_cobrado, 9000)
        self.assertEqual(self.parqueadero.espacios_disponibles, 2)
        self.assertEqual(self.parqueadero.total_recaudado(), 9000)
        self.assertEqual(len(self.parqueadero.historial), 1)

    def test_salida_de_vehiculo_inexistente(self):
        with self.assertRaises(VehiculoNoEncontradoError):
            self.parqueadero.registrar_salida("ZZZ999")

    def test_salida_con_placa_invalida(self):
        with self.assertRaises(DatoInvalidoError):
            self.parqueadero.registrar_salida("!")

    def test_un_vehiculo_puede_volver_a_entrar_despues_de_salir(self):
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "moto"))
        self.parqueadero.registrar_salida("ABC123")
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "moto"))
        self.assertEqual(self.parqueadero.espacios_disponibles, 1)

    def test_cada_tipo_usa_su_estrategia(self):
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"))
        self.parqueadero.registrar_entrada(Vehiculo("DEF456", "bicicleta"))
        self.reloj.avanzar(hours=3)

        carro = self.parqueadero.registrar_salida("ABC123")
        bicicleta = self.parqueadero.registrar_salida("DEF456")

        self.assertEqual(carro.valor_cobrado, 9000)
        self.assertEqual(bicicleta.valor_cobrado, 1000)

    def test_se_puede_inyectar_otra_estrategia(self):
        parqueadero = Parqueadero(1, tarifas={"carro": TarifaPlana(500)}, reloj=self.reloj)
        parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"))
        self.reloj.avanzar(hours=5)
        self.assertEqual(parqueadero.registrar_salida("ABC123").valor_cobrado, 500)

    def test_rechaza_tipo_sin_tarifa_configurada(self):
        parqueadero = Parqueadero(1, tarifas={"carro": TarifaPlana(500)}, reloj=self.reloj)
        with self.assertRaises(DatoInvalidoError):
            parqueadero.registrar_entrada(Vehiculo("DEF456", "moto"))


if __name__ == "__main__":
    unittest.main()