# Reservas App

Reservas App es una aplicación web desarrollada en Django para la gestión de reservas de espacios. Permite la administración de usuarios (con roles y permisos diferenciados), espacios disponibles y reservas, e incluye funcionalidades avanzadas como validaciones, reportes y comandos de carga de datos de prueba.

## Índice

- Características
- Tecnologías
- Arquitectura y Estructura del Proyecto
- Instalación y Configuración
- Uso y Comandos Personalizados
- Desarrollo y Mantenimiento
- Notas y Recomendaciones
- Licencia

## Características

- Gestión de reservas de espacios con validaciones y manejo de conflictos.
- Administración de usuarios con roles (administrador, usuario, moderador).
- Panel de administración (Django Admin) integrado y personalizado.
- Generación de datos de prueba mediante comandos personalizados como:
  - `crear_usuarios_demo`
  - `crear_reservas_demo`
- Interfaz moderna con Tailwind CSS + DaisyUI.
- Soporte para filtros y búsquedas dentro de las reservas, espacios y usuarios.
- Registro de actividad y errores para facilitar el mantenimiento.

## Tecnologías

- **Lenguaje:** Python 3.x
- **Framework:** Django (versión 5.2 o superior)
- **Base de datos:** SQLite (por defecto), compatible con otros SGBD.
- **Front-end:** HTML, CSS (Tailwind CSS), DaisyUI (Tailwind Library) JavaScript
- **Dependencias adicionales:**  
   - **django-filter:** Filtros avanzados en vistas y formularios.
   - **django-widget-tweaks:** Personalización de widgets en plantillas.
   - **django-compressor:** Optimización y compresión de archivos estáticos.
   - **pandas:** Procesamiento y análisis de datos para reportes.
   - **django-auditlog:** Registro automático de cambios y auditoría.
   - **django-crispy-forms:** Formularios flexibles y personalizables.
   - **crispy-tailwind:** Integración de crispy-forms con Tailwind CSS.
   - **fontawesomefree:** Iconos modernos para la interfaz.

- **Herramientas de desarrollo:**
  - Tailwind CSS CLI
  - Comandos personalizados para la carga de datos y pruebas

## Arquitectura y Estructura del Proyecto

El proyecto se organiza de la siguiente forma:

```
Reservas_app/
│
├── apps/                   # Contiene las diferentes aplicaciones Django
│   ├── auth/               # Módulo para autenticación y gestión de usuarios
│   ├── core/               # Funcionalidades centrales y comandos de gestión (incluye comandos demo)
│   ├── espacios/           # Gestión de espacios (salas, ubicaciones, disponibilidad)
│   ├── logs/               # Registro y seguimiento de acciones y errores
│   ├── reservas/           # Funcionalidades de reservas, validaciones, gestión de estados
│   └── usuarios/           # Administración y perfil de usuarios
│
├── config/                 # Configuración principal del proyecto Django
│   ├── asgi.py
│   ├── settings.py         # Configuración global del proyecto
│   ├── urls.py             # Ruteo global de la aplicación
│   └── wsgi.py
│
├── library/                # Librerías y utilidades compartidas entre aplicaciones
│   ├── context_proccesors/ # Procesadores para inyectar variables en las plantillas
│   ├── mixins/             # Funciones utilitarias y mixins reutilizables
│   └── utils/              # Funciones generales y helpers
│
├── static/                 # Archivos estáticos (CSS, JavaScript, imágenes)
│   ├── src/                # Archivos fuente, como el input de Tailwind CSS
│   └── css/                # Hojas de estilo compiladas
│
├── templates/              # Plantillas HTML que definen la interfaz de usuario
│   ├── base.html           # Plantilla base que se extiende en otras vistas
│   └── ...                 # Vistas específicas para reservas, usuarios, etc.
│
├── db.sqlite3              # Base de datos de desarrollo (por defecto SQLite)
├── manage.py               # Script de administración de Django
├── package.json            # Configuración de dependencias de Tailwind CSS y otras herramientas en Node.js
├── requirements.txt        # Dependencias de Python
└── readme.md               # Este documento, que incluye ideas de instalación, uso e instrucciones generales
```

## Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone <URL-del-repositorio>
   cd Reservas_app
   ```

2. **Crear y activar el entorno virtual (recomendado):**
   ```bash
   python -m venv venv
   source venv/Scripts/activate    # en Windows (usa venv\Scripts\activate en CMD o PowerShell)
   ```

3. **Instalar dependencias de Python:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Instalar dependencias de Tailwind CSS:**
   Revisar el archivo package.json y ejecutar:
   ```bash
   npm install
   ```

5. **Compilar archivos estáticos con Tailwind CSS:**
   ```bash
   npm run watch:tailwind
   ```
   (Asegúrate de tener el CLI de Tailwind correctamente configurado)

6. **Aplicar migraciones y arrancar el servidor:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

7. **Crear un superusuario para el acceso al panel administrativo:**
   ```bash
   python manage.py createsuperuser
   ```

## Uso y Comandos Personalizados

La aplicación incluye varios comandos personalizados para facilitar la generación de datos de prueba y realizar tareas administrativas:

- **Crear usuarios demo:**
  ```bash
  python manage.py crear_usuarios_demo
  ```
  Este comando poblará la base de datos con usuarios de prueba sin privilegios de superusuario.

- **Crear reservas demo:**
  ```bash
  python manage.py crear_reservas_demo [total] [--verbose]
  ```
  - `total`: Número de reservas pendientes a crear por ubicación (por defecto 10).
  - `--verbose`: Muestra detalles sobre la creación y errores (ej. validaciones, integridad).

Estas utilidades ayudan a probar diferentes escenarios (como validaciones de fechas, restricciones de integridad, etc.) y mejorar el proceso de desarrollo.

## Desarrollo y Mantenimiento

- **Estructura de código:**
  Las diferentes funcionalidades están separadas en aplicaciones (apps) específicas para facilitar su mantenimiento y escalabilidad. Cada módulo maneja una parte del proceso (usuarios, reservas, espacios, logs).

- **Plantillas y Front-end:**
  La carpeta templates contiene las vistas HTML basadas en una plantilla base (`base.html`). Elementos comunes como el menú, mensajes de alerta y formularios reutilizan componentes parciales incluidos en includes.

- **Control de versiones y deploy:**
  Se utiliza Git para el control de versiones. Se recomienda realizar ramas para nuevas funcionalidades y seguir la metodología de merge mediante pull requests.
  
- **Pruebas:**
  Cada aplicación cuenta con sus propios tests en la carpeta `tests/` o en archivos específicos (ej. `tests_forms.py`, `tests_models.py` en la app de reservas). Se recomienda ejecutarlas periódicamente:
  ```bash
  python manage.py test
  ```

## Notas y Recomendaciones

- **Errores y validaciones:**
  El sistema valida la integridad de las reservas (evitando solapamientos, validaciones de fechas, etc.) y muestra estadísticas de errores durante la carga de datos demo.
  
- **Estilo y Front-end:**
  Se utiliza Tailwind CSS para un diseño moderno y responsivo. Revisa el archivo `src/css/input.css` para personalizaciones y adapta el compilado en `static/css/output.css`.

- **Seguridad y permisos:**
  La configuración de Django y dispositivos del proyecto aseguran que solo usuarios autorizados puedan acceder al panel administrativo y realizar cambios en reservas y espacios.
  
- **Mantenimiento y escalabilidad:**
  La división en múltiples apps (auth, core, espacios, logs, reservas y usuarios) permite agregar nuevas características o modificar la lógica de negocio sin afectar otras partes del sistema.

