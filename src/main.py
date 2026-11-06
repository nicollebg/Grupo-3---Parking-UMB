
from modelos.vehiculo import Vehiculo
from modelos.registro import mostrar_vehiculos
from servicios.parqueadero import Parqueadero


def iniciar_sistema():

    parqueadero = Parqueadero(5)

    while True:

        print("\n===== SISTEMA DE GESTION DE PARQUEADERO =====")
        print("1. Registrar vehiculo")
        print("2. Consultar disponibilidad")
        print("3. Mostrar vehiculos")
        print("4. Salir")

        opcion = input("Seleccione una opcion: ")

        if opcion == "1":

            placa = input("Ingrese la placa: ")
            tipo = input("Ingrese el tipo de vehiculo: ")

            vehiculo = Vehiculo(placa, tipo)
            parqueadero.registrar_vehiculo(vehiculo)

        elif opcion == "2":

            parqueadero.consultar_disponibilidad()

        elif opcion == "3":

            mostrar_vehiculos(parqueadero.vehiculos)

        elif opcion == "4":

            print("Cerrando el sistema...")
            break

        else:

            print("Opcion no valida.")


if __name__ == "__main__":
    iniciar_sistema()