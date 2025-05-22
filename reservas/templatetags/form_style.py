# templatetags/form_style.py
from django import template
from django.utils.safestring import mark_safe
from django.forms import Textarea, CheckboxInput, Select, PasswordInput

register = template.Library()

@register.filter(name='mystyle')
def mystyle(form):
    output = ""
    # … non_field_errors …

    for field in form.visible_fields():
        # 1) etiqueta block-level:
        label_html = field.label_tag(attrs={"class": "label block text-sm text-base-content font-bold"})
        
        # 2) widget con anchura completa:
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

        # 3) help_text y errores igual que antes
        help_html = (f"<label class='label-text-alt block text-base-content text-xs mt-1'>{field.help_text}</label>"
                     if field.help_text else "")
        error_html = "".join(f"<div class='text-error text-base-content text-xs mt-1'>{e}</div>"
                             for e in field.errors)

        output += f"""
        <div class="form-control w-full mb-4">
          {label_html}
          {widget_html}
          {help_html}
          {error_html}
        </div>"""
    return mark_safe(output)
