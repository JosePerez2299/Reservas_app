# templatetags/form_style.py
from django import template
from django.utils.safestring import mark_safe
from django.forms.boundfield import BoundField
from django.forms import Textarea, CheckboxInput, Select

register = template.Library()

@register.filter(name='mystyle')
def mystyle(obj):
    """
    Si le pasas un formulario, itera sobre visible_fields().
    Si le pasas un BoundField, lo renderiza solo a él.
    """
    # Caso 1: un campo suelto
    if isinstance(obj, BoundField):
        field = obj
        label_html = field.label_tag(attrs={"class": "label block text-sm font-bold"})
        widget = field.field.widget
        base = "w-full input-sm neutral"
        if isinstance(widget, Textarea):
            css = f"textarea {base}"
        elif isinstance(widget, Select):
            css = f"select {base}"
        elif isinstance(widget, CheckboxInput):
            css = "checkbox"
        else:
            css = f"input {base}"
        widget_html = field.as_widget(attrs={"class": css, "id": field.auto_id})
        help_html = f"<p class='text-xs mt-1 text-gray-500'>{field.help_text}</p>" if field.help_text else ""
        error_html = "".join(f"<p class='text-xs mt-1 text-red-600'>{e}</p>" for e in field.errors)
        return mark_safe(f"<div class='form-control mb-4'>{label_html}{widget_html}{help_html}{error_html}</div>")

    # Caso 2: un formulario completo
    output = ""
    for field in obj.visible_fields():
        # reutilizas el mismo código anterior...
        label_html = field.label_tag(attrs={"class": "label block text-sm font-bold"})
        widget = field.field.widget
        base = "w-full input-sm neutral"
        if isinstance(widget, Textarea):
            css = f"textarea {base}"
        elif isinstance(widget, Select):
            css = f"select {base}"
        elif isinstance(widget, CheckboxInput):
            css = "checkbox"
        else:
            css = f"input {base}"
        widget_html = field.as_widget(attrs={"class": css, "id": field.auto_id})
        help_html = f"<p class='text-xs mt-1 text-gray-500'>{field.help_text}</p>" if field.help_text else ""
        error_html = "".join(f"<p class='text-xs mt-1 text-red-600'>{e}</p>" for e in field.errors)
        output += f"<div class='form-control mb-4'>{label_html}{widget_html}{help_html}{error_html}</div>"

    return mark_safe(output)
