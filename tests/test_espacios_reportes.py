import unittest
from datetime import date, datetime, timedelta

import contexto  # noqa: F401

from modelos.vehiculo import Vehiculo
from servicios.parqueadero import Parqueadero
from utilidades.excepciones import (
    DatoInvalidoError,
    EspacioNoDisponibleError,
)


class RelojFalso:
    def __init__(self, inicio=datetime(2026, 11, 6, 8, 0)):
        self.ahora = inicio

    def __call__(self):
        return self.ahora

    def avanzar(self, **tiempo):
        self.ahora += timedelta(**tiempo)


class TestEspaciosNumerados(unittest.TestCase):
    def setUp(self):
        self.reloj = RelojFalso()
        self.parqueadero = Parqueadero(3, reloj=self.reloj)

    def test_asigna_el_primer_espacio_libre(self):
        a = self.parqueadero.registrar_entrada(Vehiculo("AAA111", "carro"))
        b = self.parqueadero.registrar_entrada(Vehiculo("BBB222", "carro"))
        self.assertEqual((a.espacio, b.espacio), (1, 2))

    def test_reutiliza_el_espacio_que_se_libera(self):
        self.parqueadero.registrar_entrada(Vehiculo("AAA111", "carro"))
        self.parqueadero.registrar_entrada(Vehiculo("BBB222", "carro"))
        self.parqueadero.registrar_salida("AAA111")

        nuevo = self.parqueadero.registrar_entrada(Vehiculo("CCC333", "carro"))

        self.assertEqual(nuevo.espacio, 1)

    def test_permite_elegir_un_espacio(self):
        registro = self.parqueadero.registrar_entrada(
            Vehiculo("AAA111", "carro"), espacio=3
        )
        self.assertEqual(registro.espacio, 3)
        self.assertEqual(self.parqueadero.espacios_libres, [1, 2])

    def test_rechaza_espacio_ocupado(self):
        self.parqueadero.registrar_entrada(Vehiculo("AAA111", "carro"), espacio=2)
        with self.assertRaises(EspacioNoDisponibleError):
            self.parqueadero.registrar_entrada(Vehiculo("BBB222", "carro"), espacio=2)

    def test_rechaza_espacios_fuera_de_rango_o_de_tipo_incorrecto(self):
        for espacio in (0, 4, -1, "2", 1.5, True):
            with self.subTest(espacio=espacio):
                with self.assertRaises(DatoInvalidoError):
                    self.parqueadero.registrar_entrada(
                        Vehiculo("AAA111", "carro"), espacio=espacio
                    )

    def test_un_rechazo_no_deja_el_vehiculo_registrado(self):
        with self.assertRaises(DatoInvalidoError):
            self.parqueadero.registrar_entrada(Vehiculo("AAA111", "carro"), espacio=9)
        self.assertEqual(self.parqueadero.espacios_disponibles, 3)

    def test_mapa_de_espacios(self):
        self.parqueadero.registrar_entrada(Vehiculo("AAA111", "carro"), espacio=2)

        mapa = self.parqueadero.mapa_espacios()

        self.assertEqual([n for n, _ in mapa], [1, 2, 3])
        self.assertIsNone(mapa[0][1])
        self.assertEqual(mapa[1][1].vehiculo.placa, "AAA111")


class TestPlanesEnElParqueadero(unittest.TestCase):
    def test_cobro_segun_el_plan_elegido(self):
        # (plan, tipo, placa, hora de entrada, horas de estadia, esperado)
        casos = [
            ("normal", "carro", "AAA111", 10, 2, 6000),
            ("nocturna", "carro", "AAA111", 21, 5, 8000),
            ("nocturna", "moto", "AAA11A", 21, 5, 5000),
            ("nocturna", "carro", "AAA111", 9, 2, 6000),
            ("convenio", "carro", "AAA111", 10, 2, 4200),
            ("convenio", "moto", "AAA11A", 10, 2, 2100),
            ("mensualidad", "carro", "AAA111", 10, 8, 0),
        ]
        for plan, tipo, placa, hora, horas, esperado in casos:
            with self.subTest(plan=plan, tipo=tipo, hora=hora):
                reloj = RelojFalso(datetime(2026, 11, 6, hora, 0))
                parqueadero = Parqueadero(2, reloj=reloj)
                parqueadero.registrar_entrada(Vehiculo(placa, tipo), plan=plan)
                reloj.avanzar(hours=horas)

                registro = parqueadero.registrar_salida(placa)

                self.assertEqual(registro.plan, plan)
                self.assertEqual(registro.valor_cobrado, esperado)

    def test_plan_invalido(self):
        parqueadero = Parqueadero(1)
        with self.assertRaises(DatoInvalidoError):
            parqueadero.registrar_entrada(Vehiculo("AAA111", "carro"), plan="vip")

    def test_estimar_cobro_respeta_el_plan(self):
        reloj = RelojFalso()
        parqueadero = Parqueadero(1, reloj=reloj)
        registro = parqueadero.registrar_entrada(
            Vehiculo("AAA111", "carro"), plan="convenio"
        )
        reloj.avanzar(minutes=30)
        self.assertEqual(parqueadero.estimar_cobro(registro), 2100)


class TestReportePorFecha(unittest.TestCase):
    def setUp(self):
        self.reloj = RelojFalso(datetime(2026, 11, 5, 10, 0))
        self.parqueadero = Parqueadero(5, reloj=self.reloj)

    def _estadia(self, placa, tipo, plan="normal", horas=1):
        self.parqueadero.registrar_entrada(Vehiculo(placa, tipo), plan=plan)
        self.reloj.avanzar(hours=horas)
        self.parqueadero.registrar_salida(placa)

    def test_reporte_vacio(self):
        reporte = self.parqueadero.reporte_por_fecha(date(2026, 11, 5))
        self.assertEqual(reporte["salidas"], 0)
        self.assertEqual(reporte["total"], 0)
        self.assertEqual(reporte["por_tipo"], {})

    def test_reporte_separa_los_dias(self):
        self._estadia("AAA111", "carro")                 # 5 nov: $3.000
        self._estadia("BBB22B", "moto")                  # 5 nov: $1.500
        self.reloj.avanzar(days=1)
        self._estadia("CCC333", "carro", horas=2)        # 6 nov: $6.000

        dia5 = self.parqueadero.reporte_por_fecha(date(2026, 11, 5))
        dia6 = self.parqueadero.reporte_por_fecha(date(2026, 11, 6))

        self.assertEqual((dia5["salidas"], dia5["total"]), (2, 4500))
        self.assertEqual((dia6["salidas"], dia6["total"]), (1, 6000))
        self.assertEqual(self.parqueadero.total_recaudado(), 10500)

    def test_reporte_agrupa_por_tipo_y_por_plan(self):
        self._estadia("AAA111", "carro")
        self._estadia("BBB222", "carro", plan="convenio")
        self._estadia("CCC33C", "moto")
        self._estadia("DDD44", "bicicleta")

        reporte = self.parqueadero.reporte_por_fecha(date(2026, 11, 5))

        self.assertEqual(reporte["por_tipo"]["carro"], {"cantidad": 2, "total": 5100})
        self.assertEqual(reporte["por_tipo"]["moto"], {"cantidad": 1, "total": 1500})
        self.assertEqual(reporte["por_tipo"]["bicicleta"], {"cantidad": 1, "total": 1000})
        self.assertEqual(reporte["por_plan"]["normal"]["cantidad"], 3)
        self.assertEqual(reporte["por_plan"]["convenio"], {"cantidad": 1, "total": 2100})
        self.assertEqual(reporte["total"], 7600)

    def test_por_defecto_usa_la_fecha_de_hoy(self):
        self._estadia("AAA111", "carro")
        self.assertEqual(self.parqueadero.reporte_por_fecha()["salidas"], 1)

    def test_fechas_con_movimientos(self):
        self._estadia("AAA111", "carro")
        self.reloj.avanzar(days=2)
        self._estadia("BBB222", "carro")

        self.assertEqual(
            self.parqueadero.fechas_con_movimientos(),
            [date(2026, 11, 7), date(2026, 11, 5)],
        )

    def test_fecha_invalida(self):
        for fecha in ("2026-11-05", 20261105, [1]):
            with self.subTest(fecha=fecha):
                with self.assertRaises(DatoInvalidoError):
                    self.parqueadero.reporte_por_fecha(fecha)


if __name__ == "__main__":
    unittest.main()