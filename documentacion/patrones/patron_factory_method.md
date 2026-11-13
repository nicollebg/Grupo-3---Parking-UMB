
# Patron Factory Method

## Problema que resuelve

Antes de implementar este patron, el menu construia directamente los objetos Vehiculo. Esto hacia que la capa de presentacion conociera los detalles de creacion.

## Justificacion

Factory Method permite definir una interfaz para crear objetos y delegar la construccion a creadores especializados.

## Aplicacion en el proyecto

- CreadorVehiculo: clase abstracta que define crear_vehiculo().
- CreadorCarro: crea vehiculos de tipo carro.
- CreadorMoto: crea vehiculos de tipo moto.
- CreadorBicicleta: crea vehiculos de tipo bicicleta.
- FabricaVehiculos: selecciona el creador correspondiente.
- MenuConsola: utiliza la fabrica para crear los vehiculos.

## Beneficios

- Centraliza la creacion de vehiculos.
- Reduce el acoplamiento entre el menu y los modelos.
- Facilita agregar nuevos tipos de vehiculos.
- Conserva las validaciones existentes.

## Ubicacion

- Implementacion: src/fabricas/vehiculo_factory.py
- Integracion: src/componentes/menu.py
- Pruebas: tests/test_fabrica_vehiculos.py
