import unittest

import contexto  # noqa: F401

from modelos.vehiculo import Vehiculo
from utilidades.excepciones import DatoInvalidoError
from utilidades.validaciones import normalizar_placa, normalizar_tipo


class TestNormalizarPlaca(unittest.TestCase):
    def test_quita_espacios_y_pasa_a_mayusculas(self):
        self.assertEqual(normalizar_placa("  abc123 "), "ABC123")

    def test_rechaza_placas_invalidas(self):
        for placa in ("", "AB1", "ABC-123", "ABCDEFGH1", None, 123456):
            with self.subTest(placa=placa):
                with self.assertRaises(DatoInvalidoError):
                    normalizar_placa(placa)


class TestNormalizarTipo(unittest.TestCase):
    def test_acepta_tipos_validos_sin_importar_mayusculas(self):
        self.assertEqual(normalizar_tipo(" Moto ", ("carro", "moto")), "moto")

    def test_rechaza_tipos_desconocidos(self):
        with self.assertRaises(DatoInvalidoError):
            normalizar_tipo("avion", ("carro", "moto"))


class TestVehiculo(unittest.TestCase):
    def test_normaliza_datos_al_crearse(self):
        vehiculo = Vehiculo("abc123", "CARRO")
        self.assertEqual(vehiculo.placa, "ABC123")
        self.assertEqual(vehiculo.tipo, "carro")

    def test_mostrar_informacion(self):
        self.assertEqual(
            Vehiculo("ABC123", "moto").mostrar_informacion(),
            "Placa: ABC123 | Tipo: moto",
        )

    def test_rechaza_datos_invalidos(self):
        with self.assertRaises(DatoInvalidoError):
            Vehiculo("!!", "carro")
        with self.assertRaises(DatoInvalidoError):
            Vehiculo("ABC123", "avion")


if __name__ == "__main__":
    unittest.main()