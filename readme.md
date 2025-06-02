# Reservas App

Esta aplicación está desarrollada en Django y permite gestionar reservas de espacios. Tiene distintos roles (usuario, admin, moderador) que pueden reservar y administrar salas.

---

## Dependencias

- **Python 3.x**
- **Django 5.2**  
- **django-filters**
- **django-widget-tweaks**
- **django-compressor**
- **Tailwind CSS CLI** (versión ^4.1.6)

Además, en el archivo [package.json](c:\Users\josej\Reservas_app\package.json) se especifican las siguientes dependencias de desarrollo:
- `@tailwindcss/cli`
- `tailwindcss`

---

## Instalación y Primera Ejecución

1. **Crear y activar entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv env
   env\Scripts\activate
   ```

2. **Instalar dependencias de Python:**
   ```bash
   pip install django django-filters django-widget-tweaks django-compressor
   ```

3. **Instalar dependencias de Tailwind CSS:**
   ```bash
   npm install
   ```

4. **Generar archivos estáticos de Tailwind:**
   ```bash
   npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch
   ```

5. **Aplicar migraciones y arrancar el servidor:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```

---

## Estructura del Proyecto

```
Reservas_app/
│
├── my_app/                # Configuración principal de Django (settings, urls, wsgi)
│   ├── settings.py        # Configuración principal de la aplicación
│   ├── urls.py            # Rutas globales
│   └── wsgi.py            # Configuración para el servidor WSGI
│
├── reservas/              # Aplicación principal
│   ├── admin.py           # Registro de modelos en el admin
│   ├── models.py          # Definición de modelos (Espacio, Reserva, etc.)
│   ├── views.py           # Vistas generales de la aplicación
│   ├── urls.py            # Rutas específicas de la aplicación
│   ├── migrations/        # Archivos de migraciones de la base de datos
│   ├── templates/         # Plantillas HTML (dashboard, CRUD, etc.)
│   ├── management/        # Comandos de gestión (ej. cargar espacios de prueba)
│   └── library/           # Funcionalidades extendidas y reutilizables
│        ├── context_proccesors/  # Procesadores de contexto para inyectar variables en las plantillas
│        ├── filters/             # Filtros personalizados para consultas y procesamiento de datos
│        ├── forms/               # Formularios personalizados de la aplicación
│        ├── mixins/              # Mixins para reutilizar lógica en las vistas
│        ├── utils/               # Funciones y utilidades generales
│        └── views/               # Vistas auxiliares y helpers extendidos
│
├── static/                # Archivos estáticos
│   ├── src/               # Archivos fuente (CSS con Tailwind)
│   └── css/               # Archivos estáticos compilados
│
├── .gitignore             # Archivos y carpetas a ignorar en Git
└── readme.md              # Este archivo (documentación y guía)
```

---

## Notas Adicionales

- **Configuración de compresión de archivos estáticos:**  
  En [settings.py](c:\Users\josej\Reservas_app\my_app\settings.py) se ha configurado `django-compressor` para gestionar la compresión y concatenación de archivos CSS y JavaScript.
- **Acceso y permisos:**  
  La lógica de permisos y acceso al dashboard se encuentra en parte en los archivos de vistas y en el manejador de señales, según los grupos definidos en la configuración.


## Prioridad:
- Exportar a excel las tablas
- Cron Job, que se rechazen automáticamente las reservas pendientes y anteriores a hoy. 
- Autocerrar la sesión al cerrar el navegador, o después de inactividad
- View detail para cada modulo.
- Si un espacio cambia de estado disponible a no disponible, se deben rechazar todas las reservas desde el momento en que no esta disponible, a futuro. 
- Panel de usuario/profile, (Cambiar contraseña unicamente). Puede ser un icono de tuerca en el nombre del perfil
- Notificaciones afirmativas al hacer submit
- Reservas solo debe listar espacios DISPONIBLES 

## No prioridad
- aside responsive (drawer de base.html)
- Field con Django selec2 para buscar el usuario
- Pruebas de los componentes
- Botón de más, para registrar ubicación al momento de crear un espacio, o de registrar un usuario
- Pag404 -> redireccionar 
- Pag403 -> Permiso denegado
- Crear Panel de estadísticas en el dashboard
- Para el selec2widget, añadir modo oscuro, y tamaños
- En los formularios de editar reservas, al aprobar o rechazar, añadir un campo para que se muestre el mensaje de aprobacion
- Guardar un Log de actividades realizadas por cada usuario
- Revisar  los templates base y base_header, para que base extienda de base_header
- Añadir campo para el full name al registrar