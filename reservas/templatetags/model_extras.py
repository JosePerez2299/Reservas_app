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
    return getattr(obj, attr_name)


@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name)



