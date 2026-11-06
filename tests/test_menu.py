import unittest

import contexto  # noqa: F401

from componentes.menu import MenuConsola
from servicios.parqueadero import Parqueadero


def ejecutar_menu(entradas, capacidad=2):
    """Corre el menú con respuestas simuladas y devuelve todo lo que imprimió."""
    respuestas = iter(entradas)
    salida = []
    parqueadero = Parqueadero(capacidad)
    MenuConsola(parqueadero, leer=lambda _: next(respuestas), escribir=salida.append).ejecutar()
    return "\n".join(salida)


class TestMenuConsola(unittest.TestCase):
    def test_flujo_completo_de_entrada_y_salida(self):
        texto = ejecutar_menu(["1", "abc123", "carro", "2", "ABC123", "5", "6"])
        self.assertIn("Vehículo registrado correctamente", texto)
        self.assertIn("Valor a pagar: $3,000", texto)
        self.assertIn("Total recaudado: $3,000", texto)

    def test_muestra_error_en_lugar_de_romperse(self):
        texto = ejecutar_menu(["1", "!!", "carro", "1", "ABC123", "avion", "2", "QQQ111", "6"])
        self.assertIn("Error: La placa debe tener", texto)
        self.assertIn("Error: Tipo de vehículo no válido", texto)
        self.assertIn("Error: El vehículo QQQ111 no está en el parqueadero.", texto)

    def test_parqueadero_lleno(self):
        texto = ejecutar_menu(
            ["1", "AAA111", "carro", "1", "BBB222", "moto", "1", "CCC333", "carro", "3", "6"],
            capacidad=2,
        )
        self.assertIn("Error: No hay espacios disponibles.", texto)
        self.assertIn("Espacios disponibles: 0 de 2", texto)

    def test_opcion_invalida(self):
        self.assertIn("Opción no válida.", ejecutar_menu(["9", "6"]))

    def test_listas_vacias(self):
        texto = ejecutar_menu(["4", "5", "6"])
        self.assertIn("No hay vehículos estacionados.", texto)
        self.assertIn("Aún no hay salidas registradas.", texto)

    def test_cierra_si_se_acaba_la_entrada(self):
        def leer(_):
            raise EOFError

        salida = []
        MenuConsola(Parqueadero(1), leer=leer, escribir=salida.append).ejecutar()
        self.assertIn("Cerrando el sistema...", salida)


if __name__ == "__main__":
    unittest.main()