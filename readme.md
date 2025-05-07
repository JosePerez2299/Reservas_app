# Entidades:
- Espacio(nombre, ubicacion, capacidad, tipo (salon, laboratorio, auditorio), disponibilidad)
- Reserva (usuario, espacio, fecha de uso, hora de inicio, hora de fin, estado (pendiente, aprobada, rechazada), motivo de uso)

# Casos de uso
- Como usuario
    - Reservar Sala
    - Ver mis solicitudes

- Como Admin
    - CRUD de usuarios
    - CRUD de salas

- Como Moderador
    - Aprobar, Rechazar Solicitudes
    - CRUD de usuarios