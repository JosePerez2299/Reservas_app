# templatetags/form_style.py
from django import template
from django.utils.safestring import mark_safe
from django.forms.boundfield import BoundField
from django.forms import Textarea, CheckboxInput, Select, CheckboxSelectMultiple, RadioSelect

register = template.Library()

@register.filter(name='mystyle')
def mystyle(obj):
    if isinstance(obj, BoundField):
        return _render_field(obj)
    if hasattr(obj, 'visible_fields'):
        return _render_form(obj)
    return str(obj)


def _render_field(field):
    label_html = _get_label_html(field)
    widget_html = _get_widget_html(field)
    help_html = _get_help_html(field)
    error_html = _get_error_html(field.errors)

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
    widget = field.field.widget

    # Manejo especial para CheckboxSelectMultiple
    if isinstance(widget, CheckboxSelectMultiple):
        return _render_checkbox_select_multiple(field)
    
    # Manejo especial para RadioSelect
    if isinstance(widget, RadioSelect):
        return _render_radio_select(field)

    # Copiar atributos existentes del widget
    attrs = widget.attrs.copy()
    widget_classes = _get_widget_classes(widget)

    # Si hay errores, marcar el widget como error
    if field.errors:
        if isinstance(widget, Textarea):
            widget_classes = widget_classes.replace(
                "textarea-bordered",
                "textarea-bordered textarea-error"
            )
        elif isinstance(widget, Select):
            widget_classes = widget_classes.replace(
                "select-bordered",
                "select-bordered select-error"
            )
        else:
            widget_classes = widget_classes.replace(
                "input-bordered",
                "input-bordered input-error"
            )

    # Agregar o extender la clase
    existing_class = attrs.get("class", "")
    attrs["class"] = (existing_class + " " + widget_classes).strip()

    # Solo definir el ID si no está ya presente
    attrs.setdefault("id", field.auto_id)

    return field.as_widget(attrs=attrs)


def _render_radio_select(field):
    """Renderiza un RadioSelect con estilos personalizados"""
    # Usar el widget por defecto pero con CSS personalizado
    widget_html = field.as_widget(attrs={
        'class': 'space-y-2'
    })
    
    # Aplicar estilos CSS para personalizar los radio buttons
    styled_html = widget_html.replace(
        '<input type="radio"',
        '<input type="radio" class="radio radio-primary mr-2"'
    ).replace(
        '<label',
        '<label class="flex items-center mb-2 cursor-pointer text-sm text-base-content"'
    )
    
    return mark_safe(f"<div class='space-y-2'>{styled_html}</div>")


def _render_checkbox_select_multiple(field):
    """Renderiza un CheckboxSelectMultiple con estilos personalizados"""
    # Alternativa más simple: usar el widget por defecto pero con CSS personalizado
    widget_html = field.as_widget(attrs={
        'class': 'space-y-2'
    })
    
    # Aplicar estilos CSS para personalizar los checkboxes
    styled_html = widget_html.replace(
        '<input type="checkbox"',
        '<input type="checkbox" class="checkbox checkbox-primary mr-2"'
    ).replace(
        '<label',
        '<label class="flex items-center mb-2 cursor-pointer"'
    )
    
    return mark_safe(f"<div class='space-y-2'>{styled_html}</div>")


def _get_widget_classes(widget):
    base = (
        "input input-bordered w-full "
        "focus:input-primary transition-colors duration-200"
    )
    mapping = {
        # Textareas con alto fijo y scroll interno
        Textarea: (
            "textarea textarea-bordered w-full "
            "focus:textarea-primary transition-colors duration-200 "
            "h-32 overflow-y-auto resize-none"
        ),
        Select: (
            "select select-bordered w-full "
            "focus:select-primary transition-colors duration-200"
        ),
        CheckboxInput: "checkbox checkbox-primary",
        RadioSelect: "radio radio-primary",
        # No incluimos CheckboxSelectMultiple aquí porque se maneja por separado
    }

    # Widgets de tipo date/time
    t = getattr(widget, 'input_type', None)
    if t == 'date':
        return base + " datepicker"
    if t == 'time':
        return base

    return mapping.get(type(widget), base)


def _get_help_html(field):
    """Genera el HTML del texto de ayuda si existe."""
    if not field.help_text:
        return ""
    
    # Manejar help_text como lista o string
    help_text = field.help_text
    if isinstance(help_text, list):
        # Si es una lista, unir los elementos
        help_text = " ".join(str(item) for item in help_text)
    elif hasattr(help_text, '__iter__') and not isinstance(help_text, str):
        # Si es iterable pero no string, convertir a string
        help_text = " ".join(str(item) for item in help_text)
    else:
        help_text = str(help_text)
    
    # Limpiar HTML tags si los hay
    import re
    help_text = re.sub(r'<[^>]+>', '', help_text)
    
    return (
        f"<div class='flex items-start mt-2'>"
        f"<svg class='w-4 h-4 text-info mt-0.5 mr-2 flex-shrink-0' fill='currentColor' viewBox='0 0 20 20'>"
        f"<path fill-rule='evenodd' d='M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z' clip-rule='evenodd'/>"
        f"</svg>"
        f"<p class='text-xs text-base-content/70 leading-relaxed w-full break-words overflow-wrap-anywhere whitespace-normal'>"
        f"{help_text}</p>"
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
    if not form.non_field_errors():
        return ""
    html = ""
    for err in form.non_field_errors():
        html += (
            f"<div class='alert alert-error shadow-lg mb-4'>"
            f"<div class='flex items-start'>"
            f"<svg class='w-5 h-5 text-error-content mr-3' fill='currentColor' viewBox='0 0 20 20'>"
            f"<path fill-rule='evenodd' d='M18 10a8 8 0 11-16 0 8 8 0 0116 0zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z' clip-rule='evenodd'/>"
            f"</svg>"
            f"<span class='text-sm text-error-content'>{err}</span>"
            f"</div></div>"
        )
    return html