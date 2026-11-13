
# Patron Observer

## Problema que resuelve

Cuando un vehiculo entra o sale del parqueadero, otros componentes necesitan conocer el evento sin que la logica principal dependa directamente de ellos.

## Justificacion

Observer permite que un objeto notifique automaticamente a otros objetos cuando ocurre un cambio o evento.

## Aplicacion en el proyecto

- Parqueadero: funciona como sujeto observable.
- ObservadorParqueadero: define la interfaz actualizar().
- ObservadorConsola: recibe los eventos y muestra notificaciones.
- suscribir(): agrega observadores.
- desuscribir(): elimina observadores.
- _notificar(): envia informacion sobre los eventos.

El sistema notifica las entradas y salidas de los vehiculos y muestra la disponibilidad actualizada.

## Beneficios

- Desacopla las notificaciones de la logica principal.
- Permite agregar nuevos observadores.
- Facilita el mantenimiento del sistema.
- Permite probar las notificaciones independientemente.

## Ubicacion

- Implementacion: src/observadores/observador_parqueadero.py
- Integracion: src/servicios/parqueadero.py
- Activacion: src/main.py
- Pruebas: tests/test_observer.py
