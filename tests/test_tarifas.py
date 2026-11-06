import unittest

import contexto  # noqa: F401

from servicios.tarifas import (
    EstrategiaTarifa,
    TarifaPlana,
    TarifaPorHora,
    crear_tarifas_por_defecto,
)
from utilidades.excepciones import DatoInvalidoError


class TestTarifaPorHora(unittest.TestCase):
    def setUp(self):
        self.tarifa = TarifaPorHora(3000)

    def test_cobra_minimo_una_hora(self):
        self.assertEqual(self.tarifa.calcular(0), 3000)
        self.assertEqual(self.tarifa.calcular(5), 3000)

    def test_hora_exacta_cobra_una_hora(self):
        self.assertEqual(self.tarifa.calcular(60), 3000)

    def test_fraccion_se_cobra_como_hora_completa(self):
        self.assertEqual(self.tarifa.calcular(61), 6000)
        self.assertEqual(self.tarifa.calcular(130), 9000)

    def test_rechaza_minutos_negativos(self):
        with self.assertRaises(DatoInvalidoError):
            self.tarifa.calcular(-1)

    def test_rechaza_valor_hora_invalido(self):
        with self.assertRaises(DatoInvalidoError):
            TarifaPorHora(0)


class TestTarifaPlana(unittest.TestCase):
    def test_cobra_el_mismo_valor_sin_importar_el_tiempo(self):
        tarifa = TarifaPlana(1000)
        self.assertEqual(tarifa.calcular(10), 1000)
        self.assertEqual(tarifa.calcular(600), 1000)

    def test_rechaza_valor_invalido(self):
        with self.assertRaises(DatoInvalidoError):
            TarifaPlana(-5)


class TestTarifasPorDefecto(unittest.TestCase):
    def test_cada_tipo_tiene_una_estrategia(self):
        tarifas = crear_tarifas_por_defecto()
        self.assertEqual(set(tarifas), {"carro", "moto", "bicicleta"})
        for estrategia in tarifas.values():
            self.assertIsInstance(estrategia, EstrategiaTarifa)

    def test_estrategias_distintas_dan_valores_distintos(self):
        tarifas = crear_tarifas_por_defecto()
        self.assertEqual(tarifas["carro"].calcular(90), 6000)
        self.assertEqual(tarifas["moto"].calcular(90), 3000)
        self.assertEqual(tarifas["bicicleta"].calcular(90), 1000)

    def test_no_se_puede_instanciar_la_interfaz(self):
        with self.assertRaises(TypeError):
            EstrategiaTarifa()


if __name__ == "__main__":
    unittest.main()