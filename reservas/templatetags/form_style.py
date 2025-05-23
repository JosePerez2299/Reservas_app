# templatetags/form_style.py
from django import template
from django.utils.safestring import mark_safe
from django.forms.boundfield import BoundField
from django.forms import Textarea, CheckboxInput, Select

register = template.Library()

@register.filter(name='mystyle')
def mystyle(obj):
    # Caso 1: BoundField
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

    # Caso 2: formulario completo
    if hasattr(obj, 'visible_fields'):
        output = ""
        for field in obj.visible_fields():
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

        # Mostrar errores no ligados a ningún campo
        if obj.non_field_errors():
            non_field_errors = "".join(
                f"<p class='text-xs mt-1 text-red-600'>{e}</p>" for e in obj.non_field_errors()
            )
            output = f"{non_field_errors}{output}"

        return mark_safe(output)

    # Por si no es ninguno de los casos anteriores, devolvemos el string normal
    return str(obj)
