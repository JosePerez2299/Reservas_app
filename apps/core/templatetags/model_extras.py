from django import template
from django.db.models.manager import BaseManager
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
    attr = getattr(obj, attr_name)

    # Si es un ManyToMany → conviértelo en lista de strings
    if isinstance(attr, BaseManager):
        return ", ".join(str(x) for x in attr.all())

    # Si es callable (método o property con __call__)
    if callable(attr):
        return attr()

    return attr

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
