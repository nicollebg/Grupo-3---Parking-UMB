"""Modelo de vehículo."""

from dataclasses import dataclass

from utilidades.validaciones import (
    normalizar_placa,
    normalizar_tipo,
    validar_placa_para_tipo,
)

TIPOS_VALIDOS = ("carro", "moto", "bicicleta")


@dataclass(frozen=True)
class Vehiculo:
    placa: str
    tipo: str

    def __post_init__(self):
        # Se normaliza y valida al crear el objeto; frozen obliga a usar object.__setattr__
        placa = normalizar_placa(self.placa)
        tipo = normalizar_tipo(self.tipo, TIPOS_VALIDOS)

        # Control de placa segun el tipo (carro, moto o código de bicicleta)
        validar_placa_para_tipo(placa, tipo)

        object.__setattr__(self, "placa", placa)
        object.__setattr__(self, "tipo", tipo)

    def mostrar_informacion(self):
        return f"Placa: {self.placa} | Tipo: {self.tipo}"