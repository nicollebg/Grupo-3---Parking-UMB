"""Funciones de validación y normalización de datos de entrada."""

import re

from utilidades.excepciones import DatoInvalidoError

PATRON_PLACA = re.compile(r"^[A-Z0-9]{5,7}$")


def normalizar_placa(placa):
    """Devuelve la placa sin espacios y en mayúsculas.

    Lanza DatoInvalidoError si no es texto alfanumérico de 5 a 7 caracteres.
    """
    if not isinstance(placa, str):
        raise DatoInvalidoError("La placa debe ser un texto.")

    placa_normalizada = placa.strip().upper()

    if not PATRON_PLACA.match(placa_normalizada):
        raise DatoInvalidoError(
            "La placa debe tener entre 5 y 7 caracteres alfanuméricos (ej: ABC123)."
        )

    return placa_normalizada


def normalizar_tipo(tipo, tipos_validos):
    """Devuelve el tipo en minúsculas y comprueba que sea uno de los permitidos."""
    if not isinstance(tipo, str):
        raise DatoInvalidoError("El tipo de vehículo debe ser un texto.")

    tipo_normalizado = tipo.strip().lower()

    if tipo_normalizado not in tipos_validos:
        permitidos = ", ".join(tipos_validos)
        raise DatoInvalidoError(
            f"Tipo de vehículo no válido. Tipos permitidos: {permitidos}."
        )

    return tipo_normalizado