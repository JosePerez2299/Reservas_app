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
