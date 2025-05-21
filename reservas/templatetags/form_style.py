from django import template
from django.utils.safestring import mark_safe
from django.forms import Textarea, CheckboxInput, Select, PasswordInput

register = template.Library()

@register.filter(name='mystyle')
def mystyle(form):
    non_field_errors = "".join(
        [f"<div class='alert alert-error text-sm mb-4'>{e}</div>" for e in form.non_field_errors()]
    )
    output = non_field_errors

    for field in form.visible_fields():
        widget = field.field.widget

        if isinstance(widget, Textarea):
            css_class = "textarea neutral input-sm w-full"
        elif isinstance(widget, CheckboxInput):
            css_class = "checkbox"
        elif isinstance(widget, Select):
            css_class = "select neutral input-sm w-full"
        elif isinstance(widget, PasswordInput):
            css_class = "input neutral input-sm w-full"
        else:
            css_class = "input neutral input-sm w-full"

        help_text = f"<label class='label-text-alt text-sm text-'>{field.help_text}</label>" if field.help_text else ""

        error_html = "".join(
            [f"<div class='text-error text-sm mt-1'>{e}</div>" for e in field.errors]
        )

        widget_html = field.as_widget(attrs={
            "class": css_class,
            "id": field.auto_id,
        })

        output += f"""
        <div class="form-control mb-4">
            <label class="label">
                <span class="label-text text-xs font-semibold text-base-content">{field.label}</span>
            </label>
            {widget_html}
            {help_text}
            {error_html}
        </div>
        """

    return mark_safe(output)
