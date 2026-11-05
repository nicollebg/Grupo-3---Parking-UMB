
def mostrar_vehiculos(vehiculos):

    print("\n--- VEHICULOS EN EL PARQUEADERO ---")

    if not vehiculos:
        print("No hay vehiculos registrados.")
        return

    for vehiculo in vehiculos:
        print(vehiculo.mostrar_informacion())
