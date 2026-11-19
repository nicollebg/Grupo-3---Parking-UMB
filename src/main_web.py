"""Punto de entrada de la interfaz web del Sistema de Gestion de Parqueadero."""

import argparse

from interfaz_web.servidor import crear_servidor

CAPACIDAD_PARQUEADERO = 5


def iniciar_interfaz_web():
    parser = argparse.ArgumentParser(description="Interfaz web del parqueadero")
    parser.add_argument("--puerto", type=int, default=8000)
    parser.add_argument("--capacidad", type=int, default=CAPACIDAD_PARQUEADERO)
    args = parser.parse_args()

    servidor, _ = crear_servidor(args.capacidad, puerto=args.puerto)
    print(f"Parking UMB listo en http://127.0.0.1:{args.puerto}  (Ctrl+C para detener)")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    iniciar_interfaz_web()