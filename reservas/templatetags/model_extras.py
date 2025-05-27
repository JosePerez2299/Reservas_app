from django import template

register = template.Library()

@register.simple_tag
def get_model_fields(model, exclude=None):
    exclude = exclude or []
    return [
        {'name': f.name, 'verbose': f.verbose_name}
        for f in model._meta.fields if f.name not in exclude
    ]

@register.filter
def get_attr(obj, attr_name):
    """
    Permite lookup anidado con '__' en templates.
    Ej: {{ obj|get_attr:"espacio__ubicacion" }}
    """
    try:
        for part in attr_name.split('__'):
            obj = getattr(obj, part)
        return obj
    except Exception:
        return None


@register.filter
def get_field_by_name(form, field_name):
    """
    Returns a form field by its name if it exists in the form.
    Usage: {{ form|get_field_by_name:field_name }}
    """
    try:
        return form[field_name]
    except (KeyError, AttributeError):
        return None
