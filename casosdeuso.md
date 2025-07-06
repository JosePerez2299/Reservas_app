# Calendario, cambiar botones, ver aprobar editar... 
# Cambiar la validacion para crear la reserva, eliminar el solapamiento
# Al aprobar una reserva, se rechaza la de la misma fecha y hora
# Anadir texto de help para que el usuario sepa que debe hacer
# Incluir nombre, apellido, cedula en el usuario
# template del perfil, permite cambiar contraseña

# Casos de Uso

## Como Administrador:
- **Gestión de Espacios:**
  - Crear, listar, ver y eliminar espacios.
    - **Restricción:** Sin restricciones.
  - Asignar moderadores a los espacios.
  - Ver lista de reservas por espacio (todas las reservas).

- **Gestión de Usuarios:**
  - Crear, listar y eliminar usuarios.
    - **Restricción:** Solo se pueden crear usuarios moderadores o normales, no administradores.
  - Promover permisos o degradar

- **Gestión de Reservas:**
  - Eliminar y ver reservas.
    - **Restricción:** Sin restricciones.
  - **Nota:** No puede crear reservas.

---

## Como Moderador:
- **Gestión de Espacios:**
  - Ver los espacios gestionados por su usuario.
  - Ver reservas por espacio (un espacio específico).
  - Ver lista de reservas (todas las reservas de los espacios gestionados).

- **Gestión de Reservas:**
  - Aprobar o rechazar reservas de las salas.
    - **Restricción:** Solo puede aprobar reservas si está autorizado a moderar ese espacio.

- **Gestión de Usuarios:**
  - Crear, listar y eliminar usuarios.
    - **Restricción:** Solo puede gestionar usuarios normales.
    - **Nota:** La eliminación podría ser pasiva (no eliminar por completo).

---

## Como Usuario:
- **Gestión de Reservas:**
  - Crear y gestionar sus propias reservas.
    - **Acciones permitidas:** Eliminar y ver el estado de sus reservas.

---

## El Sistema:
- Manejar reservas vencidas:
  - Si la fecha actual es mayor a la fecha de la reserva, cambiar el estatus de la reserva.
- **Panel de estadísticas:** (¿Implementar?)


Usuario(username (unique), password, email (unique), ubicacion (FK a Ubicacion), piso (max value 40))
Ubicacion (nombre)
Reserva(usuario (fk), espacio(fk), fecha de uso, hora inicio, hora fin, estado (pendiente, aprobada, rechazada), motivo de uso, aprobado_por (fk a usuario, nullable))
Espacio(nombre, ubicacion (fk), capacidad (max 1000), tipo (salon, laboratorio, auditorio), disponibilidad)


Restricciones:
Para reserva: unique en conjunto (usuario, espacio, fecha).. crear validadores para que no se solapen las horas. motivo de uso es obligatorio (no null)


