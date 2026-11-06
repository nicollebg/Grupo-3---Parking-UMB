
class Parqueadero:

    def __init__(self, capacidad):
        self.capacidad = capacidad
        self.vehiculos = []

    def registrar_vehiculo(self, vehiculo):

        # Verificar si hay espacio disponible
        if len(self.vehiculos) < self.capacidad:
            self.vehiculos.append(vehiculo)
            print("Vehiculo registrado correctamente.")
        else:
            print("No hay espacios disponibles.")

    def consultar_disponibilidad(self):
        disponibles = self.capacidad - len(self.vehiculos)

        print(f"Espacios disponibles: {disponibles}")
