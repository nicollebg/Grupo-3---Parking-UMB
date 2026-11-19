"""Funciones de validación y normalización de datos de entrada."""

import re

from utilidades.excepciones import DatoInvalidoError

# Validación general (se aplica antes de revisar el formato propio de cada tipo)
PATRON_PLACA = re.compile(r"^[A-Z0-9]{5,7}$")

# Formatos usados en Colombia
PATRON_PLACA_CARRO = re.compile(r"^[A-Z]{3}\d{3}$")        # ABC123
PATRON_PLACA_MOTO = re.compile(r"^[A-Z]{3}\d{2}[A-Z]$")    # ABC12D
PATRON_CODIGO_BICICLETA = re.compile(r"^[A-Z0-9]{5,7}$")   # BIC001 (sin placa oficial)

REGLAS_PLACA = {
    "carro": (
        PATRON_PLACA_CARRO,
        "Placa de carro no válida: use 3 letras y 3 números (ej: ABC123).",
    ),
    "moto": (
        PATRON_PLACA_MOTO,
        "Placa de moto no válida: use 3 letras, 2 números y 1 letra (ej: ABC12D).",
    ),
    "bicicleta": (
        PATRON_CODIGO_BICICLETA,
        "La bicicleta no tiene placa en Colombia: use el código o número de serie "
        "del marco (5 a 7 letras o números, ej: BIC001).",
    ),
}


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


def validar_placa_para_tipo(placa, tipo):
    """Comprueba que la placa tenga el formato colombiano del tipo de vehículo.

    Recibe la placa ya normalizada y el tipo ya normalizado.
    """
    regla = REGLAS_PLACA.get(tipo)

    if regla is None:
        return placa

    patron, mensaje = regla

    if not patron.match(placa):
        raise DatoInvalidoError(mensaje)

    return placa


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