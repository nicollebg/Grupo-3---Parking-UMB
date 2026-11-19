"""Pruebas dirigidas a verificar que los patrones de diseño estan bien aplicados."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

import contexto  # noqa: F401

from fabricas.vehiculo_factory import (
    CreadorBicicleta,
    CreadorCarro,
    CreadorMoto,
    CreadorVehiculo,
    FabricaVehiculos,
)
from modelos.vehiculo import Vehiculo
from observadores.observador_parqueadero import (
    ObservadorEventos,
    ObservadorParqueadero,
)
from servicios.parqueadero import Parqueadero
from servicios.tarifas import EstrategiaTarifa, TarifaPlana, TarifaPorHora
from utilidades.excepciones import DatoInvalidoError


class RelojFalso:
    def __init__(self):
        self.ahora = datetime(2026, 11, 6, 8, 0)

    def __call__(self):
        return self.ahora

    def avanzar(self, **tiempo):
        self.ahora += timedelta(**tiempo)


class TestPatronStrategy(unittest.TestCase):
    def test_el_parqueadero_delega_el_cobro_en_la_estrategia(self):
        espia = Mock(spec=EstrategiaTarifa)
        espia.calcular.return_value = 12345
        reloj = RelojFalso()
        parqueadero = Parqueadero(
            1, tarifas={"carro": espia}, reloj=reloj, planes={"normal": {"carro": espia}}
        )
        parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"))
        reloj.avanzar(minutes=90)

        registro = parqueadero.registrar_salida("ABC123")

        self.assertEqual(registro.valor_cobrado, 12345)
        minutos, entrada = espia.calcular.call_args.args
        self.assertEqual(minutos, 90)
        self.assertEqual(entrada, datetime(2026, 11, 6, 8, 0))

    def test_se_puede_cambiar_de_estrategia_sin_modificar_el_servicio(self):
        for estrategia, esperado in ((TarifaPorHora(2000), 4000), (TarifaPlana(700), 700)):
            with self.subTest(estrategia=type(estrategia).__name__):
                reloj = RelojFalso()
                parqueadero = Parqueadero(1, tarifas={"carro": estrategia}, reloj=reloj)
                parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"))
                reloj.avanzar(hours=2)
                self.assertEqual(parqueadero.registrar_salida("ABC123").valor_cobrado, esperado)

    def test_estrategia_abstracta_no_se_puede_instanciar(self):
        with self.assertRaises(TypeError):
            EstrategiaTarifa()


class TestPatronFactoryMethod(unittest.TestCase):
    def test_cada_creador_produce_su_tipo(self):
        casos = (
            (CreadorCarro(), "ABC123", "carro"),
            (CreadorMoto(), "ABC12D", "moto"),
            (CreadorBicicleta(), "BIC001", "bicicleta"),
        )
        for creador, placa, tipo in casos:
            with self.subTest(creador=type(creador).__name__):
                self.assertIsInstance(creador, CreadorVehiculo)
                vehiculo = creador.crear_vehiculo(placa)
                self.assertIsInstance(vehiculo, Vehiculo)
                self.assertEqual(vehiculo.tipo, tipo)

    def test_la_fabrica_elige_el_creador_segun_el_tipo(self):
        fabrica = FabricaVehiculos()
        for tipo, placa in (("carro", "ABC123"), ("moto", "ABC12D"), ("bicicleta", "BIC001")):
            with self.subTest(tipo=tipo):
                self.assertEqual(fabrica.crear(placa, tipo), Vehiculo(placa, tipo))

    def test_la_fabrica_rechaza_tipos_desconocidos(self):
        with self.assertRaises(DatoInvalidoError):
            FabricaVehiculos().crear("ABC123", "avion")


class TestPatronObserver(unittest.TestCase):
    def setUp(self):
        self.parqueadero = Parqueadero(3, reloj=RelojFalso())

    def test_todos_los_observadores_reciben_cada_evento(self):
        uno, otro = Mock(spec=ObservadorParqueadero), Mock(spec=ObservadorParqueadero)
        self.parqueadero.suscribir(uno)
        self.parqueadero.suscribir(otro)

        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"))
        self.parqueadero.registrar_salida("ABC123")

        for observador in (uno, otro):
            eventos = [llamada.args[0] for llamada in observador.actualizar.call_args_list]
            self.assertEqual(eventos, ["entrada", "salida"])

    def test_el_observador_recibe_los_espacios_disponibles(self):
        observador = Mock(spec=ObservadorParqueadero)
        self.parqueadero.suscribir(observador)

        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"))

        _, registro, libres = observador.actualizar.call_args.args
        self.assertEqual(libres, 2)
        self.assertEqual(registro.espacio, 1)

    def test_un_observador_desuscrito_ya_no_recibe_eventos(self):
        observador = Mock(spec=ObservadorParqueadero)
        self.parqueadero.suscribir(observador)
        self.parqueadero.desuscribir(observador)

        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"))

        observador.actualizar.assert_not_called()

    def test_no_notifica_si_la_operacion_falla(self):
        observador = Mock(spec=ObservadorParqueadero)
        self.parqueadero.suscribir(observador)

        with self.assertRaises(DatoInvalidoError):
            self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"), plan="vip")

        observador.actualizar.assert_not_called()

    def test_rechaza_observadores_sin_metodo_actualizar(self):
        with self.assertRaises(DatoInvalidoError):
            self.parqueadero.suscribir(object())

    def test_observador_de_eventos_guarda_el_historial_reciente(self):
        observador = ObservadorEventos(maximo=3)
        self.parqueadero.suscribir(observador)

        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro"))
        self.parqueadero.registrar_entrada(Vehiculo("ABC12D", "moto"))
        self.parqueadero.registrar_salida("ABC123")
        self.parqueadero.registrar_salida("ABC12D")

        eventos = observador.eventos
        self.assertEqual(len(eventos), 3)
        self.assertEqual(
            [(e["evento"], e["placa"]) for e in eventos],
            [("salida", "ABC12D"), ("salida", "ABC123"), ("entrada", "ABC12D")],
        )


if __name__ == "__main__":
    unittest.main()