# Pruebas del sistema

Pruebas automatizadas con `unittest` (biblioteca estándar de Python, no requiere instalar nada).

## Cómo ejecutarlas

Desde la raíz del repositorio:

```bash
python -m unittest discover -s tests -v
```

## Qué se verifica

| Archivo | Qué comprueba |
|---|---|
| `test_tarifas.py` | Estrategias de cobro del patrón Strategy: por hora o fracción, tarifa plana y valores por tipo de vehículo. |
| `test_parqueadero.py` | Registro de entradas y salidas, capacidad máxima, placas duplicadas, cobro y recaudo, e inyección de otra estrategia. |
| `test_validaciones.py` | Normalización y validación de placa y tipo, y creación del `Vehiculo`. |
| `test_menu.py` | Integración del menú de consola con el servicio, incluido el manejo de errores. |

`contexto.py` solo agrega `src/` al path para que las pruebas puedan importar los paquetes del proyecto.