
class Vehiculo:

    def __init__(self, placa, tipo):
        # Guardar los datos del vehiculo
        self.placa = placa
        self.tipo = tipo

    def mostrar_informacion(self):
        return f"Placa: {self.placa} | Tipo: {self.tipo}"
