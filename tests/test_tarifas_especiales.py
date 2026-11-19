import unittest
from datetime import datetime

import contexto  # noqa: F401

from servicios.tarifas import (
    PLANES,
    EstrategiaTarifa,
    TarifaConvenio,
    TarifaMensualidad,
    TarifaNocturna,
    TarifaPlana,
    TarifaPorHora,
    crear_planes_por_defecto,
    crear_tarifas_por_defecto,
)
from utilidades.excepciones import DatoInvalidoError


def a_las(hora, minuto=0):
    return datetime(2026, 11, 6, hora, minuto)


class TestTarifaNocturna(unittest.TestCase):
    def setUp(self):
        self.tarifa = TarifaNocturna(TarifaPorHora(3000), 8000)

    def test_ingreso_nocturno_cobra_valor_fijo(self):
        # (hora de entrada, minutos de permanencia, valor esperado)
        casos = [
            (19, 0, 120, 8000),   # justo al empezar la noche
            (20, 30, 600, 8000),  # sin importar cuanto dure
            (23, 59, 30, 8000),
            (0, 0, 60, 8000),     # medianoche
            (5, 59, 90, 8000),    # justo antes de terminar la noche
        ]
        for hora, minuto, minutos, esperado in casos:
            with self.subTest(hora=hora, minuto=minuto, minutos=minutos):
                self.assertEqual(
                    self.tarifa.calcular(minutos, a_las(hora, minuto)), esperado
                )

    def test_ingreso_diurno_usa_la_tarifa_base(self):
        casos = [
            (6, 0, 60, 3000),     # justo al terminar la noche
            (10, 0, 61, 6000),
            (14, 0, 130, 9000),
            (18, 59, 10, 3000),   # justo antes de empezar la noche
        ]
        for hora, minuto, minutos, esperado in casos:
            with self.subTest(hora=hora, minuto=minuto, minutos=minutos):
                self.assertEqual(
                    self.tarifa.calcular(minutos, a_las(hora, minuto)), esperado
                )

    def test_sin_hora_de_entrada_usa_la_tarifa_base(self):
        self.assertEqual(self.tarifa.calcular(60), 3000)

    def test_datos_invalidos(self):
        with self.assertRaises(DatoInvalidoError):
            TarifaNocturna(TarifaPorHora(3000), 0)
        with self.assertRaises(DatoInvalidoError):
            TarifaNocturna(TarifaPorHora(3000), 8000, hora_inicio=25)
        with self.assertRaises(DatoInvalidoError):
            self.tarifa.calcular(-1, a_las(20))


class TestTarifaConvenio(unittest.TestCase):
    def test_aplica_el_descuento_sobre_la_tarifa_base(self):
        # (valor hora, minutos, descuento, esperado)
        casos = [
            (3000, 60, 0.30, 2100),
            (3000, 130, 0.30, 6300),
            (1500, 60, 0.30, 1050),
            (3000, 60, 0.50, 1500),
        ]
        for valor_hora, minutos, descuento, esperado in casos:
            with self.subTest(valor_hora=valor_hora, minutos=minutos, descuento=descuento):
                tarifa = TarifaConvenio(TarifaPorHora(valor_hora), descuento)
                self.assertEqual(tarifa.calcular(minutos), esperado)

    def test_funciona_sobre_cualquier_estrategia(self):
        self.assertEqual(TarifaConvenio(TarifaPlana(1000), 0.30).calcular(500), 700)

    def test_descuento_invalido(self):
        for descuento in (0, 1, -0.2, 1.5):
            with self.subTest(descuento=descuento):
                with self.assertRaises(DatoInvalidoError):
                    TarifaConvenio(TarifaPlana(1000), descuento)


class TestTarifaMensualidad(unittest.TestCase):
    def test_cada_estadia_cuesta_cero(self):
        tarifa = TarifaMensualidad(180000)
        for minutos in (0, 30, 600, 5000):
            with self.subTest(minutos=minutos):
                self.assertEqual(tarifa.calcular(minutos), 0)

    def test_guarda_el_valor_mensual(self):
        self.assertEqual(TarifaMensualidad(90000).valor_mensual, 90000)

    def test_valor_invalido(self):
        with self.assertRaises(DatoInvalidoError):
            TarifaMensualidad(0)


class TestPlanesPorDefecto(unittest.TestCase):
    def setUp(self):
        self.planes = crear_planes_por_defecto(crear_tarifas_por_defecto())

    def test_existen_todos_los_planes_y_tipos(self):
        self.assertEqual(set(self.planes), set(PLANES))
        for plan, estrategias in self.planes.items():
            with self.subTest(plan=plan):
                self.assertEqual(set(estrategias), {"carro", "moto", "bicicleta"})

    def test_strategy_todas_son_intercambiables(self):
        # Patron Strategy: cualquier estrategia responde a calcular(minutos, entrada)
        for plan, estrategias in self.planes.items():
            for tipo, estrategia in estrategias.items():
                with self.subTest(plan=plan, tipo=tipo):
                    self.assertIsInstance(estrategia, EstrategiaTarifa)
                    valor = estrategia.calcular(90, a_las(21))
                    self.assertIsInstance(valor, int)
                    self.assertGreaterEqual(valor, 0)

    def test_valores_de_ejemplo_por_plan(self):
        # (plan, tipo, minutos, hora de entrada, esperado)
        casos = [
            ("normal", "carro", 90, 10, 6000),
            ("normal", "moto", 90, 10, 3000),
            ("normal", "bicicleta", 90, 10, 1000),
            ("nocturna", "carro", 90, 21, 8000),
            ("nocturna", "moto", 90, 21, 5000),
            ("nocturna", "bicicleta", 90, 21, 2000),
            ("nocturna", "carro", 90, 10, 6000),
            ("convenio", "carro", 90, 10, 4200),
            ("convenio", "moto", 90, 10, 2100),
            ("convenio", "bicicleta", 90, 10, 700),
            ("mensualidad", "carro", 90, 10, 0),
            ("mensualidad", "moto", 90, 10, 0),
        ]
        for plan, tipo, minutos, hora, esperado in casos:
            with self.subTest(plan=plan, tipo=tipo, hora=hora):
                valor = self.planes[plan][tipo].calcular(minutos, a_las(hora))
                self.assertEqual(valor, esperado)


if __name__ == "__main__":
    unittest.main()