# Patrón Strategy: cálculo de tarifas

## 1. Nombre del patrón

**Strategy** (Estrategia), patrón de diseño de comportamiento.

## 2. Problema que busca solucionar

Cada tipo de vehículo se cobra de forma distinta: los carros y las motos pagan por hora o fracción con valores diferentes, y las bicicletas pagan una tarifa plana. Sin un patrón, el servicio tendría que resolverlo con una cadena de `if/elif` sobre el tipo de vehículo:

```python
if tipo == "carro":
    valor = horas * 3000
elif tipo == "moto":
    valor = horas * 1500
elif tipo == "bicicleta":
    valor = 1000
```

Eso mezcla la lógica de cobro con la gestión del parqueadero, y cada nuevo tipo o cambio de tarifa obliga a modificar la clase principal.

## 3. Justificación de su selección

- El cálculo del cobro es la parte del sistema que más variaciones tiene (tipos de vehículo, tarifas por hora, tarifas planas y, a futuro, convenios o tarifas nocturnas).
- Strategy permite agregar o cambiar un algoritmo de cobro sin tocar `Parqueadero` (principio abierto/cerrado).
- Cada estrategia se puede probar de forma aislada.
- Es un patrón sencillo de aplicar en Python y adecuado para el alcance del proyecto.

## 4. Descripción de su aplicación

1. `EstrategiaTarifa` define la interfaz con el método `calcular(minutos)`.
2. `TarifaPorHora` y `TarifaPlana` son estrategias concretas, cada una con su algoritmo.
3. `crear_tarifas_por_defecto()` asocia cada tipo de vehículo con su estrategia.
4. `Parqueadero` (el contexto) recibe ese diccionario en su constructor. Al registrar la salida busca la estrategia según `vehiculo.tipo` y le delega el cálculo, sin conocer los detalles.

## 5. Componentes involucrados

| Rol en el patrón | Clase | Archivo |
|---|---|---|
| Estrategia (interfaz) | `EstrategiaTarifa` | `src/servicios/tarifas.py` |
| Estrategia concreta | `TarifaPorHora` | `src/servicios/tarifas.py` |
| Estrategia concreta | `TarifaPlana` | `src/servicios/tarifas.py` |
| Contexto | `Parqueadero` | `src/servicios/parqueadero.py` |
| Cliente | `main.py` / `MenuConsola` | `src/main.py`, `src/componentes/menu.py` |

Valores de ejemplo configurados:

| Tipo | Estrategia | Valor |
|---|---|---|
| carro | `TarifaPorHora` | $3.000 por hora o fracción |
| moto | `TarifaPorHora` | $1.500 por hora o fracción |
| bicicleta | `TarifaPlana` | $1.000 |

## 6. Código correspondiente a su implementación

Interfaz y estrategias (`src/servicios/tarifas.py`):

```python
class EstrategiaTarifa(ABC):
    @abstractmethod
    def calcular(self, minutos):
        """Devuelve el valor a cobrar (en pesos) para los minutos dados."""


class TarifaPorHora(EstrategiaTarifa):
    def __init__(self, valor_hora):
        self.valor_hora = valor_hora

    def calcular(self, minutos):
        horas_cobradas = max(1, math.ceil(minutos / MINUTOS_POR_HORA))
        return horas_cobradas * self.valor_hora


class TarifaPlana(EstrategiaTarifa):
    def __init__(self, valor):
        self.valor = valor

    def calcular(self, minutos):
        return self.valor
```

Uso desde el contexto (`src/servicios/parqueadero.py`):

```python
estrategia = self._tarifas[registro.vehiculo.tipo]
registro.valor_cobrado = estrategia.calcular(registro.minutos_permanencia())
```

## 7. Beneficios obtenidos

- **Se eliminan los condicionales** por tipo de vehículo dentro de `Parqueadero`.
- **Extensible:** para un nuevo tipo de vehículo o un nuevo esquema de cobro basta con crear una clase que implemente `calcular` y registrarla en el diccionario.
- **Separación de responsabilidades:** `Parqueadero` gestiona espacios y registros; las estrategias gestionan el cobro.
- **Probable:** `tests/test_tarifas.py` verifica cada algoritmo por separado y `tests/test_parqueadero.py` comprueba que se puede inyectar una estrategia distinta.

## 8. Cómo se verifica

```bash
python -m unittest discover -s tests -v
```

Ver también el [diagrama del patrón](../diagramas/diagrama_strategy.md).