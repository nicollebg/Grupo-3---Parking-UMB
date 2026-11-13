# Evidencias de funcionamiento

Salidas reales del programa y de las pruebas (versión final, rama `main`).

## 1. Pruebas automáticas

Comando: `python -m unittest discover -s tests -v`

```text

----------------------------------------------------------------------
Ran 48 tests in 0.002s

OK
```

Resultado: **48 pruebas aprobadas** (tarifas, parqueadero, validaciones, menú, fábrica de vehículos y observador).

## 2. Programa en ejecución

Comando: `python src/main.py` (desde la carpeta `src`)

**Entrada de vehículos: Factory Method crea el vehículo y Observer avisa**
```text
Notificacion: ingreso carro ABC123. Espacios disponibles: 4.
Vehículo registrado correctamente: Placa: ABC123 | Tipo: carro
Notificacion: ingreso moto XYZ789. Espacios disponibles: 3.
```

**Salida: Strategy calcula el cobro y Observer avisa**
```text
Notificacion: salida carro ABC123. Espacios disponibles: 4.
Permanencia: 0 minutos.
Valor a pagar: $3,000
```

**Historial**
```text
Placa: ABC123 | Tipo: carro | Valor: $3,000
Total recaudado: $3,000
```

**Error controlado (el programa no se cierra)**
```text
Error: La placa debe tener entre 5 y 7 caracteres alfanuméricos (ej: ABC123).
```

## 3. Dónde se ve cada patrón

| Patrón | Archivo | Uso en el programa |
|---|---|---|
| Strategy | `src/servicios/tarifas.py` | Cobro por tipo: carro $3.000/h, moto $1.500/h, bicicleta $1.000 fija |
| Factory Method | `src/fabricas/vehiculo_factory.py` | El menú crea el vehículo al registrar una entrada |
| Observer | `src/observadores/observador_parqueadero.py` | Avisa cada entrada y salida con los espacios disponibles |
