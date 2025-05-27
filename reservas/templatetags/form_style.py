# templatetags/form_style.py
from django import template
from django.utils.safestring import mark_safe
from django.forms.boundfield import BoundField
from django.forms import Textarea, CheckboxInput, Select

register = template.Library()

@register.filter(name='mystyle')
def mystyle(obj):
    """
    Aplica estilos personalizados a formularios de Django optimizado para modales.
    Uso: {{ form|mystyle }} o {{ form.field_name|mystyle }}
    """
    
    if isinstance(obj, BoundField):
        return _render_field(obj)
    
    if hasattr(obj, 'visible_fields'):
        return _render_form(obj)
    
    return str(obj)


def _render_field(field):
    """Renderiza un campo individual con estilos aplicados."""
    label_html = _get_label_html(field)
    widget_html = _get_widget_html(field)
    help_html = _get_help_html(field)
    error_html = _get_error_html(field.errors)
    
    # Agregar clase de error al contenedor si hay errores
    container_class = "form-control mb-4 max-w-full overflow-hidden"
    if field.errors:
        container_class += " has-error"
    
    return mark_safe(
        f"<div class='{container_class}'>"
        f"{label_html}"
        f"{widget_html}"
        f"{help_html}"
        f"{error_html}"
        f"</div>"
    )


def _render_form(form):
    """Renderiza un formulario completo con todos sus campos."""
    fields_html = "".join(_render_field(field) for field in form.visible_fields())
    non_field_errors_html = _get_non_field_errors_html(form)
    
    return mark_safe(f"{non_field_errors_html}{fields_html}")


def _get_label_html(field):
    """Genera el HTML de la etiqueta del campo posicionada arriba."""
    if not field.label:
        return ""
    
    required_indicator = "<span class='text-error ml-1'>*</span>" if field.field.required else ""
    
    return (
        f"<div class='mb-2'>"
        f"<span class='text-sm font-semibold text-base-content '>{field.label}</span>"
        f"{required_indicator}"
        f"</div>"
    )


def _get_widget_html(field):
    """Genera el HTML del widget del campo con las clases CSS apropiadas."""
    widget_classes = _get_widget_classes(field.field.widget)
    
    # Para errores, agregar clase de error específica de DaisyUI
    if field.errors:
        if isinstance(field.field.widget, Textarea):
            widget_classes = widget_classes.replace("textarea-bordered", "textarea-bordered textarea-error")
        elif isinstance(field.field.widget, Select):
            widget_classes = widget_classes.replace("select-bordered", "select-bordered select-error")
        else:
            widget_classes = widget_classes.replace("input-bordered", "input-bordered input-error")
    
    return field.as_widget(attrs={
        "class": widget_classes,
        "id": field.auto_id
    })


def _get_widget_classes(widget):
    base_classes = "input input-bordered w-full focus:input-primary transition-colors duration-200"

    widget_type_classes = {
        Textarea: "textarea textarea-bordered w-full focus:textarea-primary transition-colors duration-200 min-h-[80px] resize-y",
        Select: "select select-bordered w-full focus:select-primary transition-colors duration-200",
        CheckboxInput: "checkbox checkbox-primary"
    }

    # Verifica si tiene un tipo específico como 'date', 'time', etc.
    input_type = getattr(widget, 'input_type', None)

    if input_type == 'date':
        return "input input-bordered w-full focus:input-primary transition-colors duration-200 datepicker"
    elif input_type == 'time':
        return "input input-bordered w-full focus:input-primary transition-colors duration-200"

    return widget_type_classes.get(type(widget), base_classes)


def _get_help_html(field):
    """Genera el HTML del texto de ayuda si existe."""
    if not field.help_text:
        return ""
    return (
        f"<div class='flex items-start mt-2'>"
        f"<svg class='w-4 h-4 text-info mt-0.5 mr-2 flex-shrink-0' fill='currentColor' viewBox='0 0 20 20'>"
        f"<path fill-rule='evenodd' d='M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z' clip-rule='evenodd'/>"
        f"</svg>"
        f"<p class='text-xs text-base-content/70 leading-relaxed w-full break-words overflow-wrap-anywhere whitespace-normal'>"
        f"{field.help_text}</p>"
        f"</div>"
    )


def _get_error_html(errors):
    """Genera el HTML de los errores del campo."""
    if not errors:
        return ""
    
    error_items = ""
    for error in errors:
        error_items += (
            f"<div class='flex items-start mt-2'>"
            f"<svg class='w-4 h-4 text-error mt-0.5 mr-2 flex-shrink-0' fill='currentColor' viewBox='0 0 20 20'>"
            f"<path fill-rule='evenodd' d='M18 10a8 8 0 11-16 0 8 8 0 0116 0zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z' clip-rule='evenodd'/>"
            f"</svg>"
            f"<p class='text-xs text-error leading-relaxed w-full break-words overflow-wrap-anywhere whitespace-normal'>"
            f"{error}</p>"
            f"</div>"
        )
    
    return error_items


def _get_non_field_errors_html(form):
    """Genera el HTML de errores no relacionados con campos específicos."""
    if not form.non_field_errors():
        return ""
    
    errors_html = ""
    for error in form.non_field_errors():
        errors_html += (
            f"<div class='alert alert-error shadow-lg mb-4'>"
            f"<div class='flex items-start'>"
            f"<svg class='w-5 h-5 text-error-content flex-shrink-0 mr-3' fill='currentColor' viewBox='0 0 20 20'>"
            f"<path fill-rule='evenodd' d='M18 10a8 8 0 11-16 0 8 8 0 0116 0zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z' clip-rule='evenodd'/>"
            f"</svg>"
            f"<span class='text-sm text-error-content w-full break-words overflow-wrap-anywhere whitespace-normal'>{error}</span>"
            f"</div>"
            f"</div>"
        )
    
    return errors_html