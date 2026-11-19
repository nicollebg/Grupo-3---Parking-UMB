import unittest

import contexto  # noqa: F401

from fabricas.vehiculo_factory import FabricaVehiculos
from modelos.vehiculo import Vehiculo
from utilidades.excepciones import DatoInvalidoError
from utilidades.validaciones import validar_placa_para_tipo


class TestPlacasColombianas(unittest.TestCase):
    """Control de placa segun el tipo de vehiculo (formatos usados en Colombia)."""

    def test_placas_de_carro_validas(self):
        for placa in ("ABC123", "xyz987", " def456 "):
            with self.subTest(placa=placa):
                self.assertEqual(Vehiculo(placa, "carro").tipo, "carro")

    def test_placas_de_carro_invalidas(self):
        # Una placa de moto (ABC12D) o con otro formato no sirve para un carro
        for placa in ("ABC12D", "AB1234", "ABCD12", "123ABC", "ABC1234"):
            with self.subTest(placa=placa):
                with self.assertRaises(DatoInvalidoError):
                    Vehiculo(placa, "carro")

    def test_placas_de_moto_validas(self):
        for placa in ("ABC12D", "xyz98a", " def45g "):
            with self.subTest(placa=placa):
                self.assertEqual(Vehiculo(placa, "moto").tipo, "moto")

    def test_placas_de_moto_invalidas(self):
        # Una placa de carro (ABC123) no sirve para una moto
        for placa in ("ABC123", "ABC1D2", "AB12CD", "ABC12", "ABCD12"):
            with self.subTest(placa=placa):
                with self.assertRaises(DatoInvalidoError):
                    Vehiculo(placa, "moto")

    def test_bicicleta_usa_codigo_porque_no_tiene_placa(self):
        for codigo in ("BIC001", "12345", "SER9A7B", "abcde"):
            with self.subTest(codigo=codigo):
                self.assertEqual(Vehiculo(codigo, "bicicleta").tipo, "bicicleta")

    def test_codigo_de_bicicleta_invalido(self):
        for codigo in ("AB1", "BIC-001", "ABCDEFGH"):
            with self.subTest(codigo=codigo):
                with self.assertRaises(DatoInvalidoError):
                    Vehiculo(codigo, "bicicleta")

    def test_mensajes_indican_el_formato_esperado(self):
        mensajes = {"carro": "ABC123", "moto": "ABC12D", "bicicleta": "BIC001"}

        for tipo, ejemplo in mensajes.items():
            with self.subTest(tipo=tipo):
                with self.assertRaises(DatoInvalidoError) as contexto:
                    validar_placa_para_tipo("@@@@@@", tipo)
                self.assertIn(ejemplo, str(contexto.exception))

    def test_la_fabrica_tambien_valida_la_placa_por_tipo(self):
        fabrica = FabricaVehiculos()

        self.assertEqual(fabrica.crear("abc12d", "moto").placa, "ABC12D")

        with self.assertRaises(DatoInvalidoError):
            fabrica.crear("ABC123", "moto")


if __name__ == "__main__":
    unittest.main()