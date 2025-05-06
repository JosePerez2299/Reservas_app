# Entidades:
- Espacio(nombre, ubicacion, capacidad, tipo (salon, laboratorio, auditorio), disponibilidad)
- Reserva (usuario, espacio, fecha de uso, hora de inicio, hora de fin, estado (pendiente, aprobada, rechazada), motivo de uso)

# Casos de uso
Template Main: Pagina de bienvenida, login, signup. Redireccionar dependiendo del tipo de usuario

Si el usuario es admin:

- puede ver todas las solicitudes (con botones ver, editar, eliminar con ventanas modales)
- incluye un buscador (por espacio, usuario, email, fecha)
    - paginacion
- crear espacios

Si no: 
- Ver su lista de solicitudes (Puede tener varias reservas? Cuanto seria el maximo?)
- reservar
    - formulario, con lista de espacio, debe ser dinamico, mostar dependiendo del tipo de espacio seleccionado
    - Mensaje de culminacion
