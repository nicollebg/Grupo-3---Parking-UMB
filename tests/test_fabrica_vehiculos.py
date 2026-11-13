
import unittest

import contexto  # noqa: F401

from fabricas.vehiculo_factory import (
    CreadorVehiculo,
    FabricaVehiculos,
)

from modelos.vehiculo import Vehiculo
from utilidades.excepciones import DatoInvalidoError


class TestFabricaVehiculos(unittest.TestCase):

    def setUp(self):
        self.fabrica = FabricaVehiculos()

    def test_crea_carro(self):
        vehiculo = self.fabrica.crear("abc123", "carro")

        self.assertEqual(
            vehiculo,
            Vehiculo("ABC123", "carro")
        )

    def test_crea_moto(self):
        vehiculo = self.fabrica.crear("def456", "moto")

        self.assertEqual(
            vehiculo,
            Vehiculo("DEF456", "moto")
        )

    def test_crea_bicicleta(self):
        vehiculo = self.fabrica.crear("ghi789", "bicicleta")

        self.assertEqual(
            vehiculo,
            Vehiculo("GHI789", "bicicleta")
        )

    def test_normaliza_tipo(self):
        vehiculo = self.fabrica.crear("abc123", " CARRO ")

        self.assertEqual(vehiculo.tipo, "carro")

    def test_rechaza_tipo_no_permitido(self):

        with self.assertRaises(DatoInvalidoError):
            self.fabrica.crear("ABC123", "avion")

    def test_rechaza_placa_invalida(self):

        with self.assertRaises(DatoInvalidoError):
            self.fabrica.crear("!!", "carro")

    def test_creador_abstracto_no_se_instancia(self):

        with self.assertRaises(TypeError):
            CreadorVehiculo()


if __name__ == "__main__":
    unittest.main()
