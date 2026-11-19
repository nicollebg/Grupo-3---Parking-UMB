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
| `test_tarifas.py` | Estrategias base: por hora o fracción, tarifa plana y valores por tipo. |
| `test_tarifas_especiales.py` | Tarifa nocturna (con sus límites horarios), convenio, mensualidad y planes por defecto (Strategy). |
| `test_parqueadero.py` | Entradas, salidas, capacidad, duplicados, cobro, recaudo e inyección de otra estrategia. |
| `test_espacios_reportes.py` | Espacios numerados, cobro según el plan y reporte por fecha. |
| `test_placas.py` | Formato de placa de carro, moto y código de bicicleta. |
| `test_validaciones.py` | Normalización y validación de placa y tipo; creación del `Vehiculo`. |
| `test_fabrica_vehiculos.py` | Factory Method: creación de vehículos por tipo. |
| `test_observer.py` | Observer: suscripción, notificación y baja de observadores. |
| `test_patrones.py` | Verificación de que Strategy, Factory Method y Observer están bien aplicados (con `unittest.mock`). |
| `test_menu.py` | Integración del menú de consola con el servicio y manejo de errores. |
| `test_interfaz_web.py` | API de la interfaz web: entrada, salida, planes, espacios, reporte, errores y archivos estáticos. |

`contexto.py` solo agrega `src/` al path para que las pruebas puedan importar los paquetes del proyecto.