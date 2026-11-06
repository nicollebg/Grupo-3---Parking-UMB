
class ParqueaderoError(Exception):
    """Error base de todas las excepciones del sistema."""


class DatoInvalidoError(ParqueaderoError):
    """Se recibió un dato que no cumple las reglas de validación."""


class ParqueaderoLlenoError(ParqueaderoError):
    """No quedan espacios disponibles en el parqueadero."""


class VehiculoDuplicadoError(ParqueaderoError):
    """El vehículo ya se encuentra dentro del parqueadero."""


class VehiculoNoEncontradoError(ParqueaderoError):
    """El vehículo no se encuentra dentro del parqueadero."""