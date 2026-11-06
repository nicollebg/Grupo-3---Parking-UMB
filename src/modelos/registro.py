"""Modelo del registro de una estadía en el parqueadero."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from modelos.vehiculo import Vehiculo


@dataclass
class RegistroParqueo:
    vehiculo: Vehiculo
    entrada: datetime
    salida: Optional[datetime] = None
    valor_cobrado: Optional[int] = None

    @property
    def activo(self):
        return self.salida is None

    def minutos_permanencia(self, hasta=None):
        """Minutos transcurridos desde la entrada hasta la salida (o hasta `hasta`)."""
        fin = self.salida or hasta
        if fin is None:
            raise ValueError("Se requiere una fecha de referencia para un registro activo.")
        return (fin - self.entrada).total_seconds() / 60

    def mostrar_informacion(self):
        entrada = self.entrada.strftime("%Y-%m-%d %H:%M")
        texto = f"{self.vehiculo.mostrar_informacion()} | Entrada: {entrada}"
        if self.salida is not None:
            salida = self.salida.strftime("%Y-%m-%d %H:%M")
            texto += f" | Salida: {salida} | Valor: ${self.valor_cobrado:,}"
        return texto