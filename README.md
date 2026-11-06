# Sistema de Gestión de Parqueadero

## 1. Descripción del proyecto

Sistema de software de consola, desarrollado en Python, para administrar un parqueadero: registra el ingreso y la salida de vehículos, controla los espacios disponibles, calcula el valor a cobrar según el tipo de vehículo y mantiene un historial de las estadías.

## 2. Objetivo

Optimizar los procesos de administración de un parqueadero mediante el registro, seguimiento y cobro de los vehículos, mejorando la organización y el manejo de la información.

## 3. Problema que busca resolver

En algunos parqueaderos, el control de los vehículos y de la disponibilidad se hace de forma manual, lo que genera errores en los registros, dificultad para saber qué espacios están libres y problemas al calcular el tiempo de permanencia y el valor a cobrar. Este proyecto centraliza esa información y automatiza el cálculo.

## 4. Alcance

**Incluye:** registro de entradas y salidas, control de capacidad, validación de datos, cobro automático por tipo de vehículo, consulta de vehículos estacionados e historial con total recaudado.

**No incluye (por ahora):** interfaz gráfica, persistencia en base de datos o archivos (los datos viven en memoria mientras el programa está abierto), manejo de usuarios o turnos.

## 5. Funcionalidades implementadas

- Registro de entrada de vehículos (placa y tipo: carro, moto o bicicleta).
- Registro de salida con cálculo automático del tiempo de permanencia y del valor a pagar.
- Consulta de espacios disponibles (capacidad configurable, 5 por defecto).
- Consulta de los vehículos estacionados.
- Historial de salidas y total recaudado.
- Validaciones: formato de placa, tipo permitido, placas duplicadas, parqueadero lleno y vehículo inexistente.
- Manejo de errores con excepciones propias y mensajes claros en el menú, sin que el programa se cierre.

## 6. Tecnologías utilizadas

- Lenguaje de programación: Python 3.
- Pruebas: `unittest` (biblioteca estándar, sin dependencias externas).
- Editor de código: Visual Studio Code.
- Control de versiones: Git.
- Repositorio remoto: GitHub.

## 7. Estructura actual del proyecto

```text
Grupo-3---Parking-UMB/
├── README.md
├── .gitignore
├── src/
│   ├── main.py                  # punto de entrada
│   ├── componentes/
│   │   └── menu.py              # menú de consola (presentación)
│   ├── modelos/
│   │   ├── vehiculo.py          # Vehiculo (datos validados)
│   │   └── registro.py          # RegistroParqueo (estadía de un vehículo)
│   ├── servicios/
│   │   ├── parqueadero.py       # lógica del parqueadero (contexto del patrón)
│   │   └── tarifas.py           # estrategias de cobro (patrón Strategy)
│   └── utilidades/
│       ├── excepciones.py       # excepciones propias
│       └── validaciones.py      # validación y normalización de datos
├── tests/                       # pruebas automatizadas (ver tests/README.md)
└── documentacion/
    ├── patrones/patron_strategy.md
    └── diagramas/diagrama_strategy.md
```

## 8. Patrones y decisiones de construcción

### Patrón implementado: Strategy

- **Problema:** cada tipo de vehículo se cobra distinto (por hora o fracción, tarifa plana). Resolverlo con `if/elif` dentro de `Parqueadero` mezclaría el cobro con la gestión de espacios y obligaría a modificar esa clase con cada nueva tarifa.
- **Aplicación:** `EstrategiaTarifa` define `calcular(minutos)`; `TarifaPorHora` y `TarifaPlana` implementan algoritmos distintos. `Parqueadero` recibe un diccionario tipo → estrategia y, al registrar la salida, le delega el cálculo a la estrategia del tipo del vehículo.
- **Razón de uso:** permite agregar tipos de vehículo o esquemas de cobro creando una clase nueva, sin tocar el servicio principal.
- **Dónde está:** `src/servicios/tarifas.py` y `src/servicios/parqueadero.py`. Documentación completa en [`documentacion/patrones/patron_strategy.md`](documentacion/patrones/patron_strategy.md) y diagramas en [`documentacion/diagramas/diagrama_strategy.md`](documentacion/diagramas/diagrama_strategy.md).

| Tipo | Estrategia | Valor de ejemplo |
|---|---|---|
| carro | `TarifaPorHora` | $3.000 por hora o fracción |
| moto | `TarifaPorHora` | $1.500 por hora o fracción |
| bicicleta | `TarifaPlana` | $1.000 |

### Otras decisiones

- **Separación de responsabilidades:** el menú (`componentes`) solo muestra y pide datos; las reglas viven en `servicios`; los datos en `modelos`; las validaciones y errores en `utilidades`.
- **Inyección de dependencias:** `Parqueadero` recibe las tarifas y el reloj por constructor, lo que permite probar cobros con fechas controladas.
- **Manejo de errores:** todas las excepciones heredan de `ParqueaderoError`, y el menú las captura para mostrar el mensaje sin romper el programa.
- **Datos validados desde el origen:** `Vehiculo` normaliza (mayúsculas, espacios) y valida al crearse.

## 9. Instrucciones de ejecución

1. Clonar el repositorio.
2. Verificar que Python 3 esté instalado (`python --version`).
3. Ejecutar el programa desde la raíz del repositorio:

```bash
python src/main.py
```

4. Ejecutar las pruebas:

```bash
python -m unittest discover -s tests -v
```

## 10. Integrantes del equipo

- Nicolle Barrera
- Nicolas Acevedo
- Alejandro Olaya

## 11. Estado actual del proyecto

Segunda entrega: el sistema funciona de principio a fin por consola (entradas, salidas, cobro e historial), con el patrón Strategy implementado, 34 pruebas automatizadas que pasan y la documentación técnica dentro del repositorio.

## 12. Próximos avances

- Persistir los registros (archivo JSON o base de datos) para no perder la información al cerrar el programa.
- Agregar nuevas estrategias de tarifa (nocturna, por convenio, mensualidad).
- Asignar espacios numerados y reportes por fecha.
- Evaluar una interfaz gráfica o web.