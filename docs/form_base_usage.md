# Template Base para Formularios AJAX

## Descripción

El template `includes/form_base_ajax.html` proporciona una base reutilizable para todos los formularios AJAX en la aplicación. Incluye:

- ✅ Manejo automático de errores con scroll
- ✅ Iconos de FontAwesome
- ✅ Estilos consistentes
- ✅ JavaScript para resaltado de campos con errores
- ✅ Estructura HTML estandarizada

## Cómo Usar

### 1. Extender el Template Base

```django
{% extends "includes/form_base_ajax.html" %}

{% block form_content %}
    <!-- Tu contenido del formulario aquí -->
{% endblock form_content %}

{% block form_script %}
    // JavaScript específico del formulario (opcional)
{% endblock form_script %}
```

### 2. Variables de Contexto Requeridas

En tu vista, asegúrate de pasar estas variables:

```python
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx['title'] = 'Título del Formulario'
    ctx['subtitle'] = 'Descripción del formulario'
    ctx['url'] = reverse_lazy('nombre_url')
    ctx['header_icon'] = 'plus'  # Icono de FontAwesome
    ctx['submit_text'] = 'Guardar'  # Texto del botón
    return ctx
```

### 3. Variables Opcionales

- `header_icon`: Icono de FontAwesome para el header (default: 'plus')
- `submit_text`: Texto del botón de envío (default: 'Guardar')

## Características Incluidas

### Manejo de Errores
- Scroll automático a errores
- Resaltado visual de campos con errores
- Lista detallada de errores
- Animaciones de shake y pulse

### Estructura HTML
- Header con icono y título
- Formulario con HTMX configurado
- Botones de acción estandarizados
- Estructura de cards para organizar campos

### JavaScript Automático
- Detección de errores al cargar
- Escucha de eventos HTMX
- Resaltado de campos con errores
- Estilos CSS dinámicos

## Ejemplo Completo

### Template
```django
{% extends "includes/form_base_ajax.html" %}

{% block form_content %}
    <div class="card bg-base-200 border border-base-300">
        <div class="card-body p-6">
            <div class="space-y-4">
                <div class="form-control">
                    <label for="{{ form.nombre.id_for_label }}" class="label">
                        <span class="label-text font-medium">{{ form.nombre.label }}</span>
                        <span class="label-text-alt text-error">* Requerido</span>
                    </label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <i class="fas fa-user text-base-content/40"></i>
                        </div>
                        {{ form.nombre }}
                    </div>
                </div>
            </div>
        </div>
    </div>
{% endblock form_content %}
```

### Vista
```python
class MiFormularioView(LoginRequiredMixin, AjaxFormMixin, CreateView):
    model = MiModelo
    form_class = MiFormularioForm
    template_name = 'mi_app/mi_formulario.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Crear Nuevo Item'
        ctx['subtitle'] = 'Complete la información requerida'
        ctx['url'] = reverse_lazy('mi_formulario_create')
        ctx['header_icon'] = 'plus'
        ctx['submit_text'] = 'Crear Item'
        return ctx
```

## Ventajas

1. **Consistencia**: Todos los formularios tienen la misma apariencia y comportamiento
2. **Mantenibilidad**: Cambios en el manejo de errores se aplican automáticamente
3. **Reutilización**: No hay que repetir código JavaScript y HTML
4. **Flexibilidad**: Cada formulario puede personalizar su contenido y JavaScript
5. **Iconos**: Uso consistente de FontAwesome en toda la aplicación

## Notas Importantes

- El template base ya incluye `{% load widget_tweaks %}` y `{% load utils %}`
- El formulario debe usar `AjaxFormMixin` para el manejo de errores
- Los campos con errores se resaltan automáticamente
- El scroll a errores funciona tanto en carga inicial como en respuestas AJAX
