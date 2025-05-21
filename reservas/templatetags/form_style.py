from django import template
from django.utils.safestring import mark_safe
from django.forms import Textarea, CheckboxInput, Select, PasswordInput

register = template.Library()

@register.filter(name='mystyle')
def mystyle(form):
    output = ""

    for field in form.visible_fields():
        # Detectar tipo de widget
        widget = field.field.widget

        if isinstance(widget, Textarea):
            css_class = "textarea w-full"
        elif isinstance(widget, CheckboxInput):
            css_class = "checkbox"
        elif isinstance(widget, Select):
            css_class = "select w-full"
        elif isinstance(widget, PasswordInput):
            css_class = "input input-bordered w-full"  # Puedes agregar estilos especiales si quieres
        else:
            css_class = "input input-bordered w-full"

        # Errors
        errors = "".join([f"<div class='text-error text-sm mt-1'>{e}</div>" for e in field.errors])

        # Help text
        help_text = f"<p class='label text-xs text-base-content/70 mt-1'>{field.help_text}</p>" if field.help_text else ""

        # Widget con estilos
        widget_html = field.as_widget(attrs={
            "class": css_class,
            "id": field.auto_id,
            "placeholder": field.label
        })

        output += f"""
        <fieldset class="fieldset mb-4">
            <legend class="fieldset-legend text-sm font-semibold text-base-content">{field.label}</legend>
            {widget_html}
            {help_text}
            {errors}
        </fieldset>
        """

    return mark_safe(output)
